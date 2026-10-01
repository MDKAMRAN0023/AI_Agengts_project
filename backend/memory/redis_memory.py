import os
import redis


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True
)


def save_message(session_id, role, message):

    key = f"conversation:{session_id}"

    redis_client.rpush(
        key,
        f"{role}: {message}"
    )


def get_messages(session_id):

    key = f"conversation:{session_id}"

    messages = redis_client.lrange(
        key,
        0,
        -1
    )

    return messages