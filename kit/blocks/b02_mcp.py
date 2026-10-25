"""02 MCP tools: give the agent tools from any MCP server, here AWS's managed AWS Knowledge server.

Use it when: the agent needs an existing tool service (docs, a government data API wrapped in MCP,
Strands Shell's sandboxed shell via `uvx strands-shell --mcp`). No credentials for this one.
Rubric: originality (novel use of AWS services), technical execution.
Run: ss block mcp
"""
from mcp.client.streamable_http import streamable_http_client
from strands import Agent
from strands.tools.mcp import MCPClient

from _common import model, say

aws_knowledge = MCPClient(lambda: streamable_http_client("https://knowledge-mcp.global.api.aws"))
with aws_knowledge:
    tools = aws_knowledge.list_tools_sync()
    say("mcp", f"{len(tools)} tools: " + ", ".join(t.tool_name for t in tools))
    agent = Agent(model=model(), tools=tools, callback_handler=None,
                  system_prompt="Answer in two sentences. Use the AWS documentation tools; do not guess.")
    out = agent("Which languages can Amazon Transcribe stream for Tamil? Give the language code.")
    say("plan", str(out).strip()[:300])
