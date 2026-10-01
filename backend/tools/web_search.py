from tavily import TavilyClient
from dotenv import load_dotenv
import os


load_dotenv()


def web_search(query):

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in .env")

    client = TavilyClient(api_key=api_key)

    results = client.search(
        query,
        max_results=3
    )

    return results["results"]