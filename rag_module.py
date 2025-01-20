from semantic_router.encoders import HuggingFaceEncoder
from pinecone import Pinecone, ServerlessSpec

# Global variables
encoder = None
index = None

def rag_initialize():
    global encoder, index
    
    # Initialize encoder
    encoder = HuggingFaceEncoder(name="dwzhu/e5-base-4k")

    # Initialize Pinecone
    pc = Pinecone(api_key='')    
    
    # Setup index specification
    spec = ServerlessSpec(cloud="aws", region="us-east-1")
    index_name = "therapist"
    dims = 768
    
    # Connect to index
    index = pc.Index(index_name)

def get_docs(query: str, top_k: int) -> list[str]:
    if encoder is None or index is None:
        raise RuntimeError("Please call initialize() first")
    
    xq = encoder([query])
    res = index.query(vector=xq, top_k=top_k, include_metadata=True)
    docs = [x["metadata"]['context'] for x in res["matches"]]
    print(docs)
    return docs
