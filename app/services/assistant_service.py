from typing import Any, Dict, List, Optional
import logging
import re
import time
import requests
from app.core.config import settings
from app.services.goal_service import get_user_goals
from app.services.emission_service import get_user_emissions, get_emission_stats
from app.services.energy_service import get_user_energy_logs

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
GEMINI_CHAT_URL = "https://generativelanguage.googleapis.com/v1/models/{model}:generateContent"
MAX_RETRIES = 1
RETRY_DELAY = 5
LOGGER = logging.getLogger(__name__)


class QuotaExceededError(Exception):
    pass


_LOCAL_RESPONSES = {
    r"carbon footprint": "Your carbon footprint is the total greenhouse gases from your activities. The average person generates 4-8 tonnes CO₂/year. Key areas: transportation, diet, energy, and consumption.",
    r"reduc|lower|decrease|cut.*emission|tips|advice|suggest|recommend|help|how can i|what can i|what should": "Ways to reduce emissions:\n1. Walk, cycle, or use public transit\n2. Switch to LED bulbs and renewables\n3. Eat more plant-based meals\n4. Take shorter showers and fix leaks\n5. Buy less, choose second-hand",
    r"energy|electricity|power|solar|wind|renewable|grid|bill": "Energy tips:\n• Switch to renewables or solar panels\n• Use Energy Star appliances\n• Turn off lights and unplug devices\n• Improve insulation\n• Use a smart thermostat",
    r"water|shower|faucet|tap|irrigation": "Water tips:\n• Fix leaky faucets (saves 20 gal/day)\n• Shorter showers (5 min saves ~25 gal)\n• Use a dishwasher over hand-washing\n• Collect rainwater\n• Install low-flow fixtures",
    r"transport|car|drive|fly|flight|travel|commut|bus|train|bike|cycl|walk|ev|electric vehicle": "Transport tips:\n• A transatlantic flight ≈ 1.6 tonnes CO₂\n• Average car ≈ 4.6 tonnes CO₂/year\n• Public transit cuts emissions 45%\n• Cycling eliminates emissions\n• EVs produce 50-70% fewer emissions",
    r"diet|food|meat|vegan|vegetarian|eat|cook|meal|beef|chicken|plant.based": "Food tips:\n• Beef ~27 kg CO₂/kg; chicken ~6.9; tofu ~2\n• Plant-based diet cuts food footprint up to 73%\n• Buy local and seasonal\n• Reduce food waste\n• Try Meatless Mondays!",
    r"goal|target|pledge|track|progress|dashboard": "Goal setting:\n• Start small – one meat-free day/week\n• Track progress on the dashboard\n• Set monthly reduction targets\n• Celebrate milestones\n• Use the Goals page to monitor",
    r"recycle|waste|plastic|trash|garbage|compost|landfill|packaging": "Waste tips:\n• 5 R's: Refuse, Reduce, Reuse, Recycle, Rot\n• Avoid single-use plastics\n• Recycle correctly per local guidelines\n• Compost organic waste\n• Choose minimal packaging",
    r"climate|global warming|greenhouse|co2|methane|emission|pollut": "Climate change is driven by CO₂ and methane emissions.\n• Temperatures up ~1.1°C since pre-industrial era\n• Top sources: energy, transport, agriculture\n• A 10% individual reduction = millions of cars off roads",
    r"tree|plant|forest|deforest|nature|biodiversity|garden": "Nature solutions:\n• One tree absorbs ~22 kg CO₂/year\n• Plant native species for biodiversity\n• Deforestation = ~10% of emissions\n• Start a small garden\n• Support verified reforestation projects",
    r"shop|buy|fashion|cloth|consum|purchase|product": "Shopping tips:\n• Buy less, choose quality\n• Shop second-hand\n• Fast fashion = ~10% of global emissions\n• Look for eco-labels\n• Repair instead of replace",
    r"home|house|heat|cool|insulation|thermostat|appliance|building": "Home tips:\n• Insulation cuts heating/cooling energy 40%\n• Lower thermostat 1-2°C in winter\n• Use A+++ rated appliances\n• Switch to LED lighting\n• Consider a heat pump",
    r"offset|carbon credit|neutral|net zero|compensat": "Offsetting tips:\n• Reduce your own emissions first\n• Choose verified projects (Gold Standard, Verra)\n• Projects: reforestation, renewables, methane capture\n• Watch for greenwashing\n• Aim for net-zero",
    r"hello|hi|hey|greet|good morning|good afternoon|good evening": "Hello! 👋 I'm your Eco Assistant. Ask me about carbon footprints, energy, transport, diet, water, waste, or sustainability goals!",
    r"thank|thanks|thx|appreciate": "You're welcome! Every small step counts. Feel free to ask more! 🌱",
    r"who are you|what are you|your name|about you|what do you do": "I'm the Eco Assistant – your sustainability advisor! Ask me about carbon footprints, energy, transport, diet, water, waste, and more.",
    r"work|office|job|business|company|corporate": "Work tips:\n• Go digital to reduce paper\n• Use video calls over travel\n• Turn off equipment when leaving\n• Encourage a sustainability policy\n• Carpool or cycle to work",
    r"kid|child|family|teach|school|education|learn": "Teaching sustainability:\n• Lead by example\n• Start a family garden\n• Make recycling fun\n• Explore nature together\n• Use age-appropriate resources",
    r"cost|money|save|cheap|expensive|budget|afford": "Going green saves money!\n• LEDs save ~$75/year\n• Less meat = lower grocery bills\n• Public transit < car ownership\n• Efficient appliances lower bills\n• Buy less, repair more",
}

_DEFAULT_RESPONSE = "Great question! Key areas to reduce your footprint:\n1. Transportation – choose low-carbon options\n2. Energy – conserve and use renewables\n3. Diet – eat more plant-based meals\n4. Waste – reduce, reuse, recycle\n5. Water – conserve and avoid waste\n\nAsk about any of these!"


def _local_fallback(messages):
    last_msg = next((m["content"].lower() for m in reversed(messages) if m.get("role") == "user" and m.get("content")), "")
    for pattern, answer in _LOCAL_RESPONSES.items():
        if re.search(pattern, last_msg):
            return {"reply": answer, "model": "local-fallback", "usage": None}
    return {"reply": _DEFAULT_RESPONSE, "model": "local-fallback", "usage": None}


def _to_gemini_contents(messages):
    contents = []
    for m in messages:
        role = m.get("role", "user")
        if role == "assistant":
            role = "model"
        elif role == "system":
            role = "user"
        text = m.get("content", "")
        if not text:
            continue
        contents.append({"role": role, "parts": [{"text": text}]})
    return contents


def chat_completion(messages, model=None, temperature=0.7, max_tokens=300):
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")
    return _gemini_call(messages, model, temperature, max_tokens)


def _safe_slice(items, limit=5):
    if not items:
        return []
    return items[:limit]


def _format_context(title, lines):
    if not lines:
        return f"{title}: none"
    return f"{title}:\n" + "\n".join(lines)


async def _build_user_context(user_id: str) -> str:
    goals = await get_user_goals(user_id)
    emissions = await get_user_emissions(user_id)
    energy_logs = await get_user_energy_logs(user_id)
    stats = await get_emission_stats(user_id)

    goal_lines = []
    for g in _safe_slice(goals, 5):
        goal_lines.append(
            f"- {g.get('category', 'General')}: target {g.get('target_value', 'n/a')} by {g.get('target_date', 'n/a')} (active: {g.get('is_active', True)})"
        )

    emission_lines = []
    for e in _safe_slice(emissions, 5):
        emission_lines.append(
            f"- {e.get('category', 'General')} {e.get('value', 'n/a')} {e.get('unit', '')} on {e.get('date', 'n/a')}"
        )

    energy_lines = []
    for e in _safe_slice(energy_logs, 5):
        energy_lines.append(
            f"- {e.get('type', 'Energy')} {e.get('value', 'n/a')} {e.get('unit', '')} on {e.get('date', 'n/a')}"
        )

    stats_summary = "n/a"
    if isinstance(stats, dict) and stats:
        stats_summary = ", ".join([f"{k}={v}" for k, v in stats.items()])

    sections = [
        _format_context("Goals", goal_lines),
        _format_context("Recent emissions", emission_lines),
        _format_context("Recent energy logs", energy_lines),
        f"Emission stats: {stats_summary}",
    ]
    return "\n\n".join(sections)


async def chat_completion_with_context(messages, user_id: str | None, model=None, temperature=0.7, max_tokens=300):
    system_prompt = (
        "You are the Eco Assistant. Provide concise, actionable sustainability guidance. "
        "Use the user context when it is available. If user data is missing, ask a short follow-up question "
        "to personalize the advice."
    )
    context_text = "User context: none"
    if user_id:
        context_text = await _build_user_context(user_id)

    enriched_messages = [
        {"role": "system", "content": system_prompt + "\n\n" + context_text},
        *messages,
    ]

    # Try Gemini first, fall back to local responses if quota is exhausted
    if settings.GEMINI_API_KEY:
        try:
            return _gemini_call(enriched_messages, model, temperature, max_tokens)
        except Exception as exc:
            LOGGER.warning("Gemini call failed, using local fallback: %s", exc)
    return _local_fallback(messages)


def _gemini_call(messages, model, temperature, max_tokens):
    url = GEMINI_CHAT_URL.format(model=(model or settings.GEMINI_MODEL))
    payload = {"contents": _to_gemini_contents(messages), "generationConfig": {"temperature": float(temperature), "maxOutputTokens": int(max_tokens)}}
    resp = None
    for attempt in range(MAX_RETRIES + 1):
        resp = requests.post(url, params={"key": settings.GEMINI_API_KEY}, json=payload, timeout=30)
        if resp.status_code != 429 or attempt == MAX_RETRIES:
            break
        time.sleep(RETRY_DELAY)
    if resp.status_code >= 400:
        raise ValueError(f"Gemini {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    reply = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
    if not reply:
        raise ValueError("Gemini empty reply")
    return {"reply": reply, "model": model or settings.GEMINI_MODEL, "usage": data.get("usageMetadata")}


def _openai_call(messages, model, temperature, max_tokens):
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model or settings.OPENAI_MODEL, "messages": messages, "temperature": float(temperature), "max_tokens": int(max_tokens)}
    resp = requests.post(OPENAI_CHAT_URL, json=payload, headers=headers, timeout=30)
    if resp.status_code >= 400:
        raise ValueError(f"OpenAI {resp.status_code}")
    data = resp.json()
    reply = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    return {"reply": reply, "model": data.get("model"), "usage": data.get("usage")}
