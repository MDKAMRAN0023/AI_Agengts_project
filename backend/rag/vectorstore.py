from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()


INDEX_NAME = "agentic-rag-copilot"


def get_pinecone_index():

    api_key = os.getenv("PINECONE_API_KEY")

    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in .env")

    pc = Pinecone(api_key=api_key)

    index = pc.Index(INDEX_NAME)

    return index


def create_vectorstore(chunks, embeddings):

    index = get_pinecone_index()

    vectors = []

    for i, chunk in enumerate(chunks):

        embedding = embeddings.embed_query(
            chunk.page_content
        )

        vectors.append({
            "id": f"chunk-{i}",
            "values": embedding,
            "metadata": {
                "text": chunk.page_content
            }
        })

    index.upsert(vectors=vectors)

    print(f"{len(vectors)} chunks uploaded to Pinecone.")

    return index


def load_vectorstore(embeddings):

    index = get_pinecone_index()

    return index
