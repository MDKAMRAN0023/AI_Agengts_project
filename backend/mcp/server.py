from mcp.server.mcpserver import MCPServer

import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )
)

from backend.database.connection import get_connection


mcp = MCPServer("Agentic RAG Copilot")


# =========================
# CALCULATOR TOOL
# =========================

@mcp.tool()
def calculator(a: float, b: float) -> float:
    """
    Add two numbers.
    """

    return a + b


# =========================
# POSTGRESQL TOOL
# =========================

@mcp.tool()
def get_conversations(limit: int = 5) -> list:
    """
    Get recent conversations from PostgreSQL.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, question, answer, route, created_at
        FROM conversations
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (limit,)
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    conversations = []

    for row in rows:

        conversations.append({
            "id": row[0],
            "question": row[1],
            "answer": row[2],
            "route": row[3],
            "created_at": str(row[4])
        })

    return conversations


# =========================
# START MCP SERVER
# =========================

if __name__ == "__main__":

    mcp.run()