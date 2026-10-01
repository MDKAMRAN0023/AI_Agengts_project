import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


server_params = StdioServerParameters(
    command="python",
    args=["backend/mcp/server.py"]
)


async def main():

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                "get_conversations",
                arguments={
                    "limit": 5
                }
            )

            print("\nPostgreSQL conversations:")
            print(result)


asyncio.run(main())