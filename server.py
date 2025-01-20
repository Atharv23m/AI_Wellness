from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import uvicorn
from rag_module import rag_initialize, get_docs

import google.generativeai as genai

app = FastAPI()
# Initialize RAG components
rag_initialize()

# Configure API key
API_KEY = ""
genai.configure(api_key=API_KEY)

# Store chat sessions
sessions: Dict[str, genai.GenerativeModel] = {}

class PromptRequest(BaseModel):
    phone_no: str
    session_id: str
    prompt: str

class HistoryRequest(BaseModel):
    phone_no: str
    session_id: str

@app.post("/send_prompt")
async def send_prompt(request: PromptRequest):
    if API_KEY is None:
        raise HTTPException(status_code=400, detail="API key not set")

    session_key = f"{request.phone_no}_{request.session_id}"
    
    if session_key not in sessions:
        # Create new chat session
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        sessions[session_key] = model.start_chat()

    try:
        response = sessions[session_key].send_message(request.prompt)
        docs = get_docs(request.prompt, 3)
        return {"answer": response.text, "docs": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing prompt: {str(e)}")

@app.post("/get_session_history")
async def get_session_history(request: HistoryRequest):
    if API_KEY is None:
        raise HTTPException(status_code=400, detail="API key not set")

    session_key = f"{request.phone_no}_{request.session_id}"
    
    if session_key not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        chat_history = []
        for message in sessions[session_key].history:
            chat_history.append({
                "role": "user" if message.role == "user" else "model",
                "text": message.parts[0].text
            })
        return {"history": chat_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
