from dotenv import load_dotenv
from pinecone import Pinecone
from backend.rag.embeddings import get_embedding_model
from backend.rag.retriever import get_retriever
import os

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index = pc.Index("agentic-rag-copilot")

embeddings = get_embedding_model()

retriever = get_retriever(index, embeddings)

results = retriever("What can Agentic RAG do?")

print("\nRetrieved Results:")

for result in results:
    print("\nText:", result["text"])
    print("Score:", result["score"])