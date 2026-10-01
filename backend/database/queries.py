from backend.database.connection import get_connection


def save_conversation(question, answer, route):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO conversations
        (question, answer, route)
        VALUES (%s, %s, %s)
        """,
        (question, answer, route)
    )

    connection.commit()

    cursor.close()
    connection.close()

    print("Conversation saved successfully!")