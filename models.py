import enum
from pydantic import BaseModel
import typing_extensions as typing
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import json
from prompts import ABC_chat_prompt, generate_ABC_template, brain_model, should_rag
from guardrails import moderate_content
import os

from rag_module import get_docs, rag_initialize

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=os.environ.get("GEMINI_KEY"))
        self.chat_abc = genai.GenerativeModel('gemini-1.5-flash', system_instruction=ABC_chat_prompt)
        self.brain = genai.GenerativeModel(model_name='gemini-2.0-flash-exp', system_instruction=brain_model)
        self.gen_abc = genai.GenerativeModel(model_name='gemini-1.5-pro', system_instruction=generate_ABC_template)       
        self.rag_decision = genai.GenerativeModel(model_name='gemini-1.5-flash-8b-001', system_instruction=should_rag)
        rag_initialize()

    def set_chat(self, chat_history: list[dict]) -> None: 
        self.chat = self.chat_abc.start_chat(history=chat_history)

    async def chat_with_system(self, 
                             prompt: str, 
                             temperature: float = 0.7) -> str:
        try:
            mod = await moderate_content(prompt)
            advice = await self.get_brain_decision(mod, prompt)
            prompt = f"{{{advice}}}" + prompt
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            return f"Error in chat: {str(e)}"

    async def end_session(self) -> str:
        try:
            session_chat = get_chat(self.chat)
            response = self.gen_abc.generate_content(
                session_chat, 
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1,  # Lower temperature for more structured output
                    candidate_count=1
                )
            )
            # Extract the text first, then parse JSON
            response_text = response.text
            if not response_text:
                return []
                
            # Ensure the response is valid JSON array
            if not response_text.startswith('['):
                response_text = f'[{response_text}]'
                
            abc_entries = json.loads(response_text)
            return abc_entries
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {response_text}")
            return []
        except Exception as e:
            print(f"General error: {str(e)}")
            return []
        
    async def get_brain_decision(self, mod, prompt) -> str:
        try:
            if mod["status"] == "blocked":
                chat += "\n Guardrail blocked user message due to reason - " + mod["message"] + "\n Tell user to follow the guardrail"
                response = self.brain.generate_content(chat)
                print(response.text)
                return response.text
            chat = "Last message:\n" + get_chat_str(self.chat) + "\nUser: " + prompt 
            rag = await self.get_rag_decision(prompt)
            if rag == "RAG":
                rag = await get_docs(chat, 3)    
            chat += "\nRag Results :\n" + rag
            print(chat)
            response = self.brain.generate_content(chat)
            print(response.text)
            return response.text
        except Exception as e:
            return {"error": str(e)}
        
    async def get_rag_decision(self, chat: str) -> str:
        try:
            response = self.rag_decision.generate_content(chat, generation_config=genai.GenerationConfig(response_mime_type="text/x.enum", response_schema=Decison))
            return response.text
        except Exception as e:
            return {"error": str(e)}
        
def get_chat_str(model: genai.ChatSession) -> str:
    chat_str = ""
    if len(model.history) >= 2:  # Check if there's at least one pair
        # Get last user message and response
        last_messages = model.history[-2:]  # Get last 2 messages
        for message in last_messages:
            if message.role == "user":
                text = message.parts[0].text
                if text.startswith('{'):
                    text = text[text.find('}')+1:]
                chat_str += f"User: {text}\n"
            else:
                chat_str += f"Therapist: {message.parts[0].text}\n"
    return chat_str

def get_chat(model: genai.ChatSession) -> str:
    chat_str = ""
    for message in model.history:
        if message.role == "user":
            text = message.parts[0].text
            if text.startswith('{'):
                text = text[text.find('}')+1:]
            chat_str += f"User: {text}\n"
        else:
            chat_str += f"Therapist: {message.parts[0].text}\n"
    return chat_str

class ABC(typing.TypedDict):
    activatingEvent: str
    belief: str
    consequence: str

class Decison(enum.Enum):
    RAG = "RAG"
    Continue = "Continue"

class brain_output(typing.TypedDict):
    decision: Decison
    text: str

