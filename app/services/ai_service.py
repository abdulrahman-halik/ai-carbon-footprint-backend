import google.generativeai as genai
from app.core.config import settings
from fastapi import HTTPException
from typing import List, Dict

# Model version selection
MODEL_NAME = "gemini-2.5-flash" 

def chat_with_ai(messages: List[Dict[str, str]]) -> str:
    """
    Takes a conversation history (list of dicts with 'role' and 'parts')
    and returns a response from Gemini.
    """
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Missing API key. Please configure GEMINI_API_KEY to use the conversational AI.")
    
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            MODEL_NAME,
            system_instruction="You are a helpful Eco-Assistant sustainability chatbot. Provide clear, helpful, and concise sustainability tips and carbon footprint advice to users based on our chat history."
        )

        history = []
        last_message = ""

        # Format to Gemini requirements if necessary, assuming messages are [{'role': 'user'|'model', 'parts': ['text...']}]
        # Gemini takes 'user' and 'model'
        for i, msg in enumerate(messages):
            # The last message should be passed to send_message or generate_content
            if i == len(messages) - 1:
                last_message = msg.get("parts", [""])[0] if isinstance(msg.get("parts"), list) else msg.get("parts", "")
            else:
                history.append(msg)
                
        # We use start_chat(history) so the model retains context
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(last_message)
        
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        raise HTTPException(status_code=500, detail="Sorry, the AI service encountered an error processing your request.")
