import google.generativeai as genai
from typing import Dict, Any, List, Optional
import json
from prompts import ABC_chat_prompt, generate_ABC_template

class GeminiService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.chat_model = genai.GenerativeModel('gemini-1.5-flash')
        self.chat_2 = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.chat_pro = genai.GenerativeModel('gemini-1.5-pro')
        
    async def chat_with_system(self, 
                             prompt: str, 
                             temperature: float = 0.7) -> str:
        try:
            chat = self.chat_2.start_chat(history=[])
            system_message = {"role": "system", "parts": [ABC_chat_prompt]}
            chat.send_message(system_message)
            response = chat.send_message(prompt, temperature=temperature)
            return response.text
        except Exception as e:
            return f"Error in chat: {str(e)}"

    async def get_abc_chart(self) :
        try:
            chat = self.chat_pro.start_chat(history=[])
            system_message = {"role": "system", "parts": [ABC_chat_prompt]}
            chat.send_message(system_message)
            response = chat.send_message(prompt, temperature=temperature)
            return response.text
        except Exception as e:
            return f"Error in chat: {str(e)}"

    
        
def get_chat_str(model: genai.ChatSession) -> str:
    chat_str = ""
    for message in model.history:
        if message.role == "user":
            chat_str += f"User: {message.text}\n"
        else:
            chat_str += f"Therapist: {message.text}\n"
    return chat_str