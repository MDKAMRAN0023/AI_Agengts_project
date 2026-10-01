from backend.tools.web_search import web_search
from backend.agents.web_grader import grade_web_evidence
from backend.rag.llm import get_llm


llm = get_llm()


def web_fallback(question):

    # 1. Search the web
    results = web_search(question)

    if not results:
        return "I don't know."

    # 2. Collect web evidence
    context = ""

    for result in results:

        context += (
            f"Title: {result['title']}\n"
            f"Content: {result['content']}\n\n"
        )

    # 3. Grade web evidence
    grade = grade_web_evidence(
        question,
        context
    )

    print("\nWeb Evidence Grade:", grade)

    # 4. If web evidence is weak
    if grade == "weak":
        return "I don't know based on the available web evidence."

    # 5. Generate answer using good web evidence
    prompt = f"""
Answer the user's question using ONLY the web evidence provided below.

Web Evidence:
{context}

Question:
{question}

Give a clear and concise answer.

Answer:
"""

    response = llm(
        prompt,
        max_new_tokens=50,
        do_sample=False,
        temperature=None
    )

    # 6. Extract answer
    answer = response[0]["generated_text"].strip()

    # 7. Remove unwanted continuation
    stop_phrases = [
        "\nQuestion:",
        "\nAnswer:",
        "\nContext:",
        "\nWeb Evidence:",
        "\nUser:",
        "\nHuman:",
        "\nAssistant:"
    ]

    for phrase in stop_phrases:

        if phrase in answer:
            answer = answer.split(phrase)[0].strip()

    # 8. Empty answer protection
    if not answer:
        return "I don't know."

    return answer