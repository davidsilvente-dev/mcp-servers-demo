"""Prueba de extremo a extremo: lanza server.py por stdio y llama a la herramienta."""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=["-m", "mcp_boe.server"], env={"PYTHONPATH": "src"})
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("herramientas:", [t.name for t in tools.tools])
            res = await session.call_tool("sumario_boe", {"fecha": "20261030"})
            print("bloques devueltos:", len(res.content), "| error:", res.isError)


asyncio.run(main())
