# /// script
# dependencies = [
#   "mcp",
#   "pydantic_ai",
# ]
# ///

from mcp.server.fastmcp import Context, FastMCP
from pydantic_ai import Agent
from pydantic_ai.models.mcp_sampling import MCPSamplingModel

server = FastMCP("Pydantic AI Server with sampling")
server_agent = Agent(system_prompt="always reply in rhyme")


@server.tool()
async def poet(ctx: Context, theme: str) -> str:
    """Poem generator"""
    r = await server_agent.run(f"write a poem about {theme}", model=MCPSamplingModel(session=ctx.session))
    return r.output


if __name__ == "__main__":
    server.run()  # run the server over stdio


"""Learnings for the day

- Sampling worked very well with this server
- Investigate more/keep an eye on when it comes to Cursor and Claude Desktop
"""
