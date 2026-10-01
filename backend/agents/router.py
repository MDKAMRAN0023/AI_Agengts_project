from typing import Literal
from pydantic import BaseModel


class RouterDecision(BaseModel):
    route: Literal["rag", "direct", "memory", "mcp", "casual"]


def route_question(question):

    question_lower = question.lower()

    # Casual conversation
    casual_keywords = [
        "hi",
        "hii",
        "hiii",
        "hello",
        "hey",
        "how are you",
        "kaise ho",
        "good morning",
        "good afternoon",
        "good evening",
        "good night",
        "thanks",
        "thank you"
    ]

    for keyword in casual_keywords:
        if keyword in question_lower:
            return "casual"

    # Memory questions
    memory_keywords = [
        "what did i ask before",
        "what did i ask you before",
        "previous question",
        "previous questions",
        "what did we discuss",
        "what did we talk about",
        "earlier conversation",
        "previous conversation",
        "conversation history",
        "what was my last question"
    ]

    for keyword in memory_keywords:
        if keyword in question_lower:
            return "memory"

    # MCP questions
    mcp_keywords = [
        "calculate",
        "add",
        "sum",
        "plus",
        "subtract",
        "minus",
        "multiply",
        "times",
        "divide",
        "addition",
        "subtraction",
        "multiplication",
        "division",
        "database",
        "postgresql",
        "postgres",
        "records"
    ]

    for keyword in mcp_keywords:
        if keyword in question_lower:
            return "mcp"

    # Arithmetic operators → MCP Calculator
    if any(operator in question_lower for operator in ["+", "-", "*", "/"]):
        return "mcp"

    # Direct questions
    direct_keywords = [
        "what is python",
        "what is ai",
        "what is machine learning",
        "what is deep learning",
        "what is artificial intelligence",
        "define",
        "meaning of"
    ]

    for keyword in direct_keywords:
        if keyword in question_lower:
            return "direct"

    # Document/file questions → RAG
    rag_keywords = [
        "document",
        "documents",
        "file",
        "files",
        "pdf",
        "according to",
        "provided",
        "based on",
        "in the document",
        "from the document",
        "from my file"
    ]

    for keyword in rag_keywords:
        if keyword in question_lower:
            return "rag"

    # Default → RAG
    return "rag"