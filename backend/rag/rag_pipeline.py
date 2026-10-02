
from backend.rag.embeddings import get_embedding_model
from backend.rag.vectorstore import load_vectorstore
from backend.rag.retriever import get_retriever
from backend.rag.llm import get_llm

from backend.agents.grader import grade_evidence
from backend.agents.web_fallback import web_fallback


# ============================================================
# Lazy-loaded RAG components
# ============================================================

_embeddings = None
_index = None
_retriever = None
_llm = None


def get_rag_components():

    global _embeddings
    global _index
    global _retriever
    global _llm

    # Load embedding model only when needed
    if _embeddings is None:
        _embeddings = get_embedding_model()

    # Connect to Pinecone only when needed
    if _index is None:
        _index = load_vectorstore(_embeddings)

    # Create retriever only when needed
    if _retriever is None:
        _retriever = get_retriever(
            _index,
            _embeddings
        )

    # Load LLM only when needed
    if _llm is None:
        _llm = get_llm()

    return _retriever, _llm


# ============================================================
# Retrieve Evidence
# ============================================================

def retrieve_evidence(question):

    retriever, _ = get_rag_components()

    results = retriever(question)

    if not results:
        return {
            "context": "",
            "score": 0
        }

    best_result = results[0]

    context = best_result["text"]
    score = best_result["score"]

    print("Similarity score:", score)

    print("\nRetrieved Context:")
    print(context)

    return {
        "context": context,
        "score": score
    }


# ============================================================
# Ask Question
# ============================================================

def ask_question(question):

    retriever, llm = get_rag_components()

    # --------------------------------------------------------
    # 1. Retrieve relevant documents
    # --------------------------------------------------------

    results = retriever(question)

    if not results:
        return "I don't know based on the provided document."

    # --------------------------------------------------------
    # 2. Get best result
    # --------------------------------------------------------

    best_result = results[0]

    context = best_result["text"]
    score = best_result["score"]

    print("Similarity score:", score)

    print("\nRetrieved Context:")
    print(context)

    # --------------------------------------------------------
    # 3. Grade retrieved evidence
    # --------------------------------------------------------

    grade = grade_evidence(
        question,
        context
    )

    print("\nEvidence Grade:", grade)

    # --------------------------------------------------------
    # 4. If evidence is weak, use Tavily web search
    # --------------------------------------------------------

    if grade == "weak":

        print("\nUsing Tavily web search...")

        return web_fallback(question)

    # --------------------------------------------------------
    # 5. Guard for questions asking about a person
    # --------------------------------------------------------

    question_lower = question.lower()

    if question_lower.startswith(("who ", "whose ")):

        person_words = [
            "invented",
            "created",
            "founded",
            "developed",
            "written",
            "authored",
            "researcher",
            "author",
            "scientist"
        ]

        has_person_information = any(
            word in context.lower()
            for word in person_words
        )

        if not has_person_information:
            return "I don't know based on the provided document."

    # --------------------------------------------------------
    # 6. Create grounded prompt
    # --------------------------------------------------------

    prompt = (
        "Answer ONLY from this context.\n\n"
        f"Context: {context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )

    # --------------------------------------------------------
    # 7. Generate answer
    # --------------------------------------------------------

    response = llm(
        prompt,
        max_new_tokens=100,
        do_sample=False,
        temperature=None
    )

    # --------------------------------------------------------
    # 8. Extract answer
    # --------------------------------------------------------

    answer = response[0]["generated_text"].strip()

    # --------------------------------------------------------
    # 9. Stop unwanted continuation
    # --------------------------------------------------------

    stop_phrases = [
        "\nContext:",
        "\nQuestion:",
        "\nAnswer:",
        "\nRelevant Information",
        "\nUser:",
        "\nHuman:",
        "\nAssistant:"
    ]

    for phrase in stop_phrases:

        if phrase in answer:
            answer = answer.split(phrase)[0].strip()

    # --------------------------------------------------------
    # 10. Empty answer protection
    # --------------------------------------------------------

    if not answer:
        return "I don't know based on the provided document."

    return answer


   

   