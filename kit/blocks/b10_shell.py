"""10 Strands Shell: an in-process sandboxed shell. Only bound folders are visible; no host files,
no credentials, network by allowlist.

Use it when: the agent must crunch data (rainfall CSVs, attendance sheets, survey results) with real
commands but must not touch the rest of the laptop. Rubric: technical execution, originality.
MCP form for any agent: `uvx strands-shell --mcp` (tools: shell, read_file, write_file, list_dir).
Run: ss block shell
"""
import os
import tempfile
import threading

import strands_shell
from strands import Agent, tool

from _common import model, say

data = tempfile.mkdtemp(prefix="ship-data-")
with open(os.path.join(data, "rain_mm.csv"), "w") as f:
    f.write("district,june,july,august\nMadurai,32,41,88\nTheni,55,70,120\nVirudhunagar,12,18,40\n")
_local = threading.local()


def shell() -> strands_shell.Shell:
    """A Shell belongs to the thread that created it, and Strands runs tools on worker threads: one per thread."""
    if not hasattr(_local, "shell"):
        _local.shell = strands_shell.Shell(binds=[strands_shell.Bind(data, "/data", mode="copy")])
    return _local.shell


@tool
def run_in_sandbox(command: str) -> str:
    """Run a command in a sandbox that sees only /data (rainfall CSV). Has cut, sort, grep, head, wc, jq and lua (no awk, no python).

    Args:
        command: one shell command line
    """
    r = shell().run(command)
    say("shell", f"$ {command[:80]} -> exit {r.status}")
    return (r.stdout or r.stderr)[:2000]


PROMPT = ('The data is /data/rain_mm.csv (district,june,july,august). Answer by running commands with run_in_sandbox. '
          'For arithmetic use lua, for example: lua -e \'for l in io.lines("/data/rain_mm.csv") do print(l) end\'. '
          'Show the number you computed.')
agent = Agent(model=model(), tools=[run_in_sandbox], callback_handler=None, system_prompt=PROMPT)
out = agent("Which district had the lowest total rainfall from June to August, and what was the total?")
say("plan", str(out).strip()[:200])
probe = shell().run("ls /Users 2>&1; cat ~/.aws/credentials 2>&1 | head -1")
say("guard", f"host files visible from the sandbox: {'no' if 'logesh' not in probe.stdout.lower() else 'YES'}")
