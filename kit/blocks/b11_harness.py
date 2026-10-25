"""11 Strands harness: a fully assembled agent in one call (prompt, context management, caching,
memory, skills, todos, interventions), built on the Strands Harness SDK. It returns a plain Agent.

Use it when: your agent is a capable generalist with a domain identity (a scheme-finder that reads
pages and keeps notes) and you would rather tune defaults than wire everything. Turn off the built-in
shell/file tools for end users: they are for coding agents.
Run: ss block harness
"""
import os
import tempfile

from strands import tool
from strands_harness import create_harness

from _common import MODEL_ID, say

SCHEMES = {"pm-kisan": "Income support of Rs 6,000 a year for landholding farmer families, paid in three instalments."}


@tool
def scheme_info(name: str) -> str:
    """Look up a government scheme from the curated list (pm-kisan only in this demo).

    Args:
        name: scheme id, e.g. pm-kisan
    """
    return SCHEMES.get(name.lower(), "not in the curated list")


work = tempfile.mkdtemp(prefix="ship-harness-")
os.chdir(work)  # the harness keeps sessions/memory under ./.agent
agent = create_harness(model=f"bedrock/{MODEL_ID}", instructions="You help farmers understand government schemes. "
                       "Only state what scheme_info returns. Two sentences.", tools=[scheme_info],
                       builtin_tools=[], builtin_plugins=[], background_tasks=False, memory=False, skills=False,
                       effort="off", callback_handler=None)
out = agent("What does PM-KISAN give a farmer?")
say("harness", f"plain Agent with tools {agent.tool_names}")
say("plan", str(out).strip()[:300])
