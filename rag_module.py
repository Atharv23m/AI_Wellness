import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec
import os

# Global variables
index = None

def rag_initialize():
    global index
    
    # Initialize Gemini
    genai.configure(api_key=os.environ.get("GEMINI_KEY"))

    # Initialize Pinecone
    pc = Pinecone(api_key=os.environ.get("PINECONE_KEY"))    
    
    # Setup index specification
    spec = ServerlessSpec(cloud="aws", region="us-east-1")
    index_name = "therapist-rag"
    dims = 768  # Make sure this matches Gemini's embedding dimension
    
    # Connect to index
    index = pc.Index(index_name)

async def get_docs(query: str, top_k: int) -> str:
    if index is None:
        raise RuntimeError("Please call initialize() first")
    
    # Get embeddings using Gemini
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=query
    )
    xq = result['embedding']
    
    res = index.query(vector=xq, top_k=top_k, include_metadata=True)
    chat_pairs = ""
    for match in res["matches"]:
        chat_pairs += f"User: {match['metadata']['context']}\nTherapist: {match['metadata']['response']}\n\n"  
    return chat_pairs
