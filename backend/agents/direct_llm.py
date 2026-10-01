from backend.rag.llm import get_llm


llm = get_llm()


def direct_answer(question, history):

    conversation_history = "\n".join(history)

    prompt = f"""
You are a helpful AI assistant.

Previous Conversation:
{conversation_history}

Current Question:
{question}

IMPORTANT:
Answer ONLY using the Previous Conversation.
Do NOT invent or assume anything.
If the answer is not present in the Previous Conversation,
say exactly:
I don't know based on the conversation history.

Answer the current question clearly and concisely.

Answer:
"""

    response = llm(
        prompt,
        max_new_tokens=50,
        do_sample=False,
        temperature=None
    )

    answer = response[0]["generated_text"].strip()

    if answer.startswith("Answer:"):
        answer = answer[len("Answer:"):].strip()

    stop_phrases = [
        "\nCurrent Question:",
        "\nAnswer:",
        "\nPrevious Conversation:",
        "\nIMPORTANT:"
    ]

    for phrase in stop_phrases:

        if phrase in answer:
            answer = answer.split(phrase)[0].strip()

    return answer