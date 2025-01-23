from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import uvicorn
from firebase import FirebaseChat
from models import GeminiClient
import os

app = FastAPI()
fb = FirebaseChat()

# Store chat sessions
sessions: Dict[str, GeminiClient] = {}

class PromptRequest(BaseModel):
    phone_no: str
    session_id: str
    prompt: str

class HistoryRequest(BaseModel):
    phone_no: str
    session_id: str

@app.post("/send_prompt")
async def send_prompt(request: PromptRequest):
    session_key = f"{request.phone_no}_{request.session_id}"
    
    if session_key not in sessions:
        sessions[session_key] = GeminiClient()
        sessions[session_key].set_chat(fb.fetch_chats(request.phone_no, request.session_id))
        print(sessions[session_key].chat.history)
    try:
        response = await sessions[session_key].chat_with_system(request.prompt)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing prompt: {str(e)}")

@app.post("/get_session_history")
async def get_session_history(request: HistoryRequest):
    try:
        # Directly fetch chat history from Firebase
        chat_history = fb.fetch_chats(request.phone_no, request.session_id)
        if not chat_history:
            raise HTTPException(status_code=404, detail="No chat history found")
            
        return {"history": chat_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
