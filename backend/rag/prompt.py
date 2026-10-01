def create_prompt(context, question):

    messages = [
        {
            "role": "system",
            "content": (
                "You are a document question-answering assistant. "
                "Answer the user's question using ONLY the provided context. "
                "If the answer is not present in the context, say: "
                "I don't know based on the provided document. "
                "Do not add information from your own knowledge."
            )
        },
        {
            "role": "user",
            "content": (
                f"Context:\n{context}\n\n"
                f"Question:\n{question}"
            )
        }
    ]

    return messages