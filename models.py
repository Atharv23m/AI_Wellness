import google.generativeai as genai
from typing import Dict, Any, List, Optional
import json
from prompts import ABC_chat_prompt, generate_ABC_template
import os

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=os.environ.get("GEMINI_KEY"))
        self.chat_model = genai.GenerativeModel('gemini-1.5-flash')
        self.chat_abc = genai.GenerativeModel(model_name='gemini-2.0-flash-exp', system_instruction=ABC_chat_prompt)
        self.gen_abc = genai.GenerativeModel(model_name='gemini-1.5-pro', system_instruction=generate_ABC_template)       

    def set_chat(self, chat_history: list[dict]) -> None: 
        self.chat = self.chat_abc.start_chat(history=chat_history)

    async def chat_with_system(self, 
                             prompt: str, 
                             temperature: float = 0.7) -> str:
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            return f"Error in chat: {str(e)}"

    async def get_abc_chart(self) :
        try:
            print("Getting ABC")
            session_chat = get_chat_str(self.chat)
            print(session_chat)
            response = self.gen_abc.generate_content(session_chat)
            return response.text
        except Exception as e:
            return f"Error in chat: {str(e)}"

    
        
def get_chat_str(model: genai.ChatSession) -> str:
    chat_str = ""
    for message in model.history:
        if message.role == "user":
            chat_str += f"User: {message.parts[0].text}\n"
        else:
            chat_str += f"Therapist: {message.parts[0].text}\n"
    return chat_str