from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from app.models.community_model import CommunityModel
from app.models.emission_model import EmissionModel
from app.models.energy_model import EnergyModel
from app.models.water_model import WaterModel
from app.schemas.community_schema import CommunityPostCreate
from app.services.content_safety_service import sanitize_public_text


def _display_name_for_user(user: dict) -> str:
    full_name = (user.get("full_name") or "").strip()
    if full_name:
        return full_name.split()[0]

    email = (user.get("email") or "community-member").strip()
    local = email.split("@", 1)[0]
    if len(local) <= 2:
        return "Eco Member"
    return f"{local[:2]}***"


def _extract_dates(records: List[dict]) -> List[datetime.date]:
    dates = set()
    for record in records:
        record_date = record.get("date") or record.get("created_at")
        if isinstance(record_date, datetime):
            dates.add(record_date.date())
    return sorted(dates, reverse=True)


def _calculate_logging_streak(records: List[dict]) -> int:
    dates = _extract_dates(records)
    if not dates:
        return 0

    streak = 0
    current = dates[0]
    for date_value in dates:
        if date_value == current:
            streak += 1
            current = current - timedelta(days=1)
            continue
        if date_value < current:
            break
    return streak


async def _build_user_snapshot(user_id: str) -> Dict[str, int]:
    emissions = await EmissionModel.find_by_user_id(user_id)
    energy_logs = await EnergyModel.find_by_user_id(user_id)
    water_logs = await WaterModel.find_by_user_id(user_id)

    combined_records = emissions + energy_logs + water_logs
    return {
        "logging_streak_days": _calculate_logging_streak(combined_records),
        "contribution_count": len(combined_records),
    }


async def create_community_post(user: dict, payload: CommunityPostCreate) -> dict:
    sanitized = sanitize_public_text(payload.content, max_length=280)
    safe_text = sanitized["text"]
    if not safe_text:
        raise ValueError("Post content is empty after sanitization")

    snapshot = await _build_user_snapshot(str(user["_id"]))
    post_data = {
        "user_id": str(user["_id"]),
        "author_name": _display_name_for_user(user),
        "content": safe_text,
        "post_type": payload.post_type,
        "milestone_label": payload.milestone_label,
        "logging_streak_days": snapshot["logging_streak_days"],
        "contribution_count": snapshot["contribution_count"],
        "was_sanitized": sanitized["was_sanitized"],
    }
    return await CommunityModel.create(post_data)


async def get_community_feed(limit: int = 20) -> List[dict]:
    posts = await CommunityModel.get_feed(limit=limit)
    return posts