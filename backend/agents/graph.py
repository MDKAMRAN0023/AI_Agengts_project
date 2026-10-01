
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
import re
import asyncio

from backend.agents.router import route_question
from backend.rag.rag_pipeline import retrieve_evidence
from backend.agents.direct_llm import direct_answer
from backend.agents.grader import grade_evidence
from backend.tools.web_search import web_search
from backend.agents.web_grader import grade_web_evidence
from backend.rag.llm import get_llm
from backend.database.queries import save_conversation
from backend.memory.redis_memory import save_message, get_messages

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client





# =========================
# STATE
# =========================

class AgentState(TypedDict):
    question: str
    route: str
    context: str
    score: float
    answer: str
    evidence_grade: str
    session_id: str
    history: list[str]


# =========================
# MCP CALCULATOR
# =========================

async def call_mcp_calculator(a, b):

    server_params = StdioServerParameters(
        command="python",
        args=["backend/mcp/server.py"]
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                "calculator",
                arguments={
                    "a": a,
                    "b": b
                }
            )

            return result.structured_content["result"]


# =========================
# MCP POSTGRESQL
# =========================

async def call_mcp_get_conversations(limit):

    server_params = StdioServerParameters(
        command="python",
        args=["backend/mcp/server.py"]
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                "get_conversations",
                arguments={
                    "limit": limit
                }
            )

            return result


# =========================
# MEMORY NODES
# =========================

def memory_load_node(state: AgentState):

    session_id = state["session_id"]

    messages = get_messages(session_id)

    if messages:

        print("\nPrevious Conversation:")

        for message in messages:
            print(message)

    else:

        print("\nNo previous conversation found.")

    return {
        "history": messages
    }


def memory_answer_node(state: AgentState):

    history = state["history"]

    current_question = state["question"].strip().lower()

    if not history:

        return {
            "answer": "You don't have any previous conversation yet."
        }

    questions = []

    for message in history:

        if message.startswith("user:"):

            question = message.replace(
                "user:",
                "",
                1
            ).strip()

            # Current question ko exclude karo
            if question.lower() == current_question:
                continue

            if question:
                questions.append(question)

    if not questions:

        return {
            "answer": "I couldn't find any previous questions."
        }

    # Duplicate questions remove karo
    unique_questions = []

    for question in questions:

        if question not in unique_questions:
            unique_questions.append(question)

    # Latest 5 previous questions
    recent_questions = unique_questions[-5:]

    answer = "Your recent questions were:\n\n"

    for question in recent_questions:

        answer += f"• {question}\n"

    return {
        "answer": answer
    }


# =========================
# CASUAL NODE
# =========================

def casual_node(state: AgentState):

    question = state["question"].lower()

    if any(word in question for word in [
        "hi",
        "hii",
        "hiii",
        "hello",
        "hey"
    ]):

        answer = "Hello! How can I help you?"

    elif "how are you" in question or "kaise ho" in question:

        answer = "I'm doing great! How can I help you?"

    elif "thanks" in question or "thank you" in question:

        answer = "You're welcome! 😊"

    else:

        answer = "Hello! How can I help you?"

    return {
        "answer": answer
    }


# =========================
# MCP CALCULATOR NODE
# =========================

def mcp_calculator_node(state: AgentState):

    question = state["question"]

    numbers = re.findall(
        r"\d+(?:\.\d+)?",
        question
    )

    if len(numbers) < 2:

        return {
            "answer": "Please provide two numbers to calculate."
        }

    a = float(numbers[0])
    b = float(numbers[1])

    result = asyncio.run(
        call_mcp_calculator(a, b)
    )

    answer = f"MCP Calculator Result: {result}"

    print(answer)

    return {
        "answer": answer
    }


# =========================
# MCP DATABASE NODE
# =========================

def mcp_database_node(state: AgentState):

    result = asyncio.run(
        call_mcp_get_conversations(5)
    )

    print("\nMCP PostgreSQL Result:")

    conversations = []

    for item in result.content:

        if hasattr(item, "text"):

            conversations.append(item.text)

    answer = "\n\n".join(conversations)

    print(answer)

    return {
        "answer": answer
    }


# =========================
# MCP ROUTER NODE
# =========================

def mcp_router_node(state: AgentState):

    return {}


# =========================
# MCP DECISION
# =========================

def mcp_decision(state: AgentState):

    question = state["question"].lower()

    database_keywords = [
        "conversation",
        "conversations",
        "history",
        "previous",
        "database",
        "postgresql",
        "postgres",
        "records"
    ]

    for keyword in database_keywords:

        if keyword in question:

            return "database"

    return "calculator"


# =========================
# ROUTER NODE
# =========================

def router_node(state: AgentState):

    question = state["question"]

    route = route_question(question)

    print("Router selected:", route)

    return {
        "route": route
    }


# =========================
# RAG NODE
# =========================

def rag_node(state: AgentState):

    question = state["question"]

    evidence = retrieve_evidence(question)

    return {
        "context": evidence["context"],
        "score": evidence["score"]
    }


# =========================
# EVIDENCE GRADER
# =========================

def grader_node(state: AgentState):

    question = state["question"]

    context = state["context"]

    grade = grade_evidence(
        question,
        context
    )

    print("Evidence Grade:", grade)

    return {
        "evidence_grade": grade
    }


# =========================
# DIRECT LLM
# =========================

def direct_node(state: AgentState):

    question = state["question"]

    history = state["history"]

    answer = direct_answer(
        question,
        history
    )

    return {
        "answer": answer
    }


# =========================
# WEB SEARCH
# =========================

def web_search_node(state: AgentState):

    question = state["question"]

    results = web_search(question)

    context = ""

    for result in results:

        context += (
            f"Title: {result['title']}\n"
            f"Content: {result['content']}\n\n"
        )

    print("\nWeb Search completed.")

    return {
        "context": context
    }


# =========================
# WEB GRADER
# =========================

def web_grader_node(state: AgentState):

    question = state["question"]

    context = state["context"]

    grade = grade_web_evidence(
        question,
        context
    )

    print("Web Evidence Grade:", grade)

    return {
        "evidence_grade": grade
    }


# =========================
# GENERATE ANSWER
# =========================

def generate_answer_node(state: AgentState):
    llm = get_llm()

    question = state["question"]

    context = state["context"]

    prompt = f"""
Answer the user's question using ONLY the evidence provided below.

Evidence:

{context}

Question:

{question}

Give ONLY the direct answer in 1-2 sentences.

Do not write headings.

Do not explain the evidence.

Do not repeat the question.

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
        "\nQuestion:",
        "\nAnswer:",
        "\n##",
        "\n###",
        "\nEvidence:",
        "\nContext:"
    ]

    for phrase in stop_phrases:

        if phrase in answer:

            answer = answer.split(
                phrase
            )[0].strip()

    return {
        "answer": answer
    }


# =========================
# SAVE CONVERSATION
# =========================

def save_conversation_node(state: AgentState):

    question = state["question"]

    answer = state["answer"]

    route = state["route"]

    session_id = state["session_id"]

    # Always save permanent conversation to PostgreSQL

    save_conversation(
        question,
        answer,
        route
    )

    # Do not save memory queries into Redis

    if route != "memory":

        save_message(
            session_id,
            "user",
            question
        )

        save_message(
            session_id,
            "assistant",
            answer
        )

    return {}


# =========================
# DECISION FUNCTIONS
# =========================

def route_decision(state: AgentState):

    return state["route"]


def evidence_decision(state: AgentState):

    return state["evidence_grade"]


def web_evidence_decision(state: AgentState):

    return state["evidence_grade"]


# =========================
# GRAPH
# =========================

graph_builder = StateGraph(AgentState)


# =========================
# NODES
# =========================

graph_builder.add_node(
    "memory_load",
    memory_load_node
)

graph_builder.add_node(
    "memory_answer",
    memory_answer_node
)

graph_builder.add_node(
    "casual",
    casual_node
)

graph_builder.add_node(
    "router",
    router_node
)

graph_builder.add_node(
    "rag",
    rag_node
)

graph_builder.add_node(
    "grader",
    grader_node
)

graph_builder.add_node(
    "direct",
    direct_node
)

graph_builder.add_node(
    "mcp_router",
    mcp_router_node
)

graph_builder.add_node(
    "mcp_calculator",
    mcp_calculator_node
)

graph_builder.add_node(
    "mcp_database",
    mcp_database_node
)

graph_builder.add_node(
    "web_search",
    web_search_node
)

graph_builder.add_node(
    "web_grader",
    web_grader_node
)

graph_builder.add_node(
    "generate_answer",
    generate_answer_node
)

graph_builder.add_node(
    "save_conversation",
    save_conversation_node
)


# =========================
# EDGES
# =========================

# START → Memory Load

graph_builder.add_edge(
    START,
    "memory_load"
)


# Memory Load → Router

graph_builder.add_edge(
    "memory_load",
    "router"
)


# =========================
# ROUTER → ROUTE
# =========================

graph_builder.add_conditional_edges(
    "router",
    route_decision,
    {
        "rag": "rag",
        "direct": "direct",
        "memory": "memory_answer",
        "mcp": "mcp_router",
        "casual": "casual"
    }
)


# =========================
# MCP ROUTER → MCP TOOL
# =========================

graph_builder.add_conditional_edges(
    "mcp_router",
    mcp_decision,
    {
        "calculator": "mcp_calculator",
        "database": "mcp_database"
    }
)


# =========================
# RAG → EVIDENCE GRADER
# =========================

graph_builder.add_edge(
    "rag",
    "grader"
)


# =========================
# KB EVIDENCE DECISION
# =========================

graph_builder.add_conditional_edges(
    "grader",
    evidence_decision,
    {
        "good": "generate_answer",
        "weak": "web_search"
    }
)


# =========================
# WEB SEARCH → WEB GRADER
# =========================

graph_builder.add_edge(
    "web_search",
    "web_grader"
)


# =========================
# WEB EVIDENCE DECISION
# =========================

graph_builder.add_conditional_edges(
    "web_grader",
    web_evidence_decision,
    {
        "good": "generate_answer",
        "weak": END
    }
)


# =========================
# GENERATE ANSWER → SAVE
# =========================

graph_builder.add_edge(
    "generate_answer",
    "save_conversation"
)


# =========================
# DIRECT → SAVE
# =========================

graph_builder.add_edge(
    "direct",
    "save_conversation"
)


# =========================
# MCP CALCULATOR → SAVE
# =========================

graph_builder.add_edge(
    "mcp_calculator",
    "save_conversation"
)


# =========================
# MCP DATABASE → END
# =========================

graph_builder.add_edge(
    "mcp_database",
    END
)


# =========================
# MEMORY → SAVE
# =========================

graph_builder.add_edge(
    "memory_answer",
    "save_conversation"
)


# =========================
# CASUAL → SAVE
# =========================

graph_builder.add_edge(
    "casual",
    "save_conversation"
)


# =========================
# SAVE → END
# =========================

graph_builder.add_edge(
    "save_conversation",
    END
)


# =========================
# COMPILE
# =========================

graph = graph_builder.compile()


# =========================
# TEST
# =========================

if __name__ == "__main__":

    result = graph.invoke({
        "question": "What is 100 + 250?",
        "session_id": "test-session"
    })

    print("\nFinal Result:")

    print(result)

