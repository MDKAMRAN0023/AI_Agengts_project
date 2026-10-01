from dotenv import load_dotenv
from pinecone import Pinecone
import os

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "agentic-rag-copilot"

if not pc.has_index(index_name):

    print("Creating Pinecone index...")

    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec={
            "serverless": {
                "cloud": "aws",
                "region": "us-east-1"
            }
        }
    )

    print("Pinecone index created successfully!")

else:
    print("Pinecone index already exists!")


print("\nAvailable indexes:")

for index in pc.list_indexes():
    print(index["name"])