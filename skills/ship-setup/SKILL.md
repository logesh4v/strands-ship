---
name: ship-setup
description: Recipe 0 of the strands-ship power. Install the Strands Agents SDK kit on this machine (once, about 400 MB) and set up a project folder for the Strands SDK Workshop to Ship hackathon. Use when the user says "set up strands ship", "strands ship", "workshop to ship", "start my Strands hackathon project", or when ~/.strands-ship/bin/ss is missing.
---
# Recipe 0: set up

The setup script ships inside the installed power at `~/.kiro/powers/installed/strands-ship/skills/ship-setup/scripts/ship.py` (written `ship.py` below). Run it by that full path; do not search for it. Only if that file does not exist, use `scripts/ship.py` inside the folder holding this SKILL.md. Everything else runs in the user's project folder. Run one command at a time and show the user its last lines. Nothing here leaves a process running.

## Step 1: check the machine (installs nothing)
`python3 ~/.kiro/powers/installed/strands-ship/skills/ship-setup/scripts/ship.py doctor`
- `RESULT BLOCKED`: show the BLOCK lines and their fixes, and stop. Typical: native Windows (use WSL2 Ubuntu), Python 3.14 only (install 3.12), no git.
- `WARN` lines: read them out. No `uvx` means the Strands docs MCP server in this power will not start (install uv). No `ffmpeg` means the video stays `.webm`. AWS credentials not working: the user runs `aws configure` or `aws sso login` in their own terminal. Never ask for keys in chat.

## Step 2: install (once per machine, 2-5 minutes)
`python3 ~/.kiro/powers/installed/strands-ship/skills/ship-setup/scripts/ship.py setup`
It creates `~/.strands-ship/` with a venv and pinned Strands Agents 1.62.0, Strands Evals 1.7.0, boto3 and Playwright, copies the kit, writes the launcher `~/.strands-ship/bin/ss`, and downloads headless Chromium for the video. It must end with `SETUP OK`. Safe to re-run; re-running after a power update refreshes the kit.

## Step 3: the project folder
In the project folder (an empty folder is fine): `~/.strands-ship/bin/ss init` (default path HeatSafe Shift; use `--path padippu|marundhu|floodready` only after recipe 1 picked another path). It never overwrites a file; show the kept list. It copies `agent/`, `cases.jsonl` (31 starter cases, unsigned), `ship_kit/` (Apache-2.0, so the repo runs without the power), `requirements.txt`, `video.json`, `FAILURES.md`, `.kiro/steering/`, `.kiro/hooks/strands-ship.json`, `.kiro/agents/ship-builder.json`.
If the folder is not a git repo: `git init`. Keep the GitHub repo **private until the window opens (28 Oct 2026)**; the agent must not be published before.

## Step 4: check Bedrock
`~/.strands-ship/bin/ss bedrock` makes one Bedrock call and one Amazon Translate call.
- Model access denied or a payment/Marketplace error: Anthropic models need an AWS Marketplace subscription; the default `us.amazon.nova-2-lite-v1:0` does not. Enable Amazon Nova in the Bedrock console (Model access) for us-east-1, or set `SHIP_MODEL` / `AWS_REGION`.
- Credentials: `aws configure` or `aws sso login` in their own terminal; `AWS_PROFILE` if not default.

## Done when
`ss bedrock` prints `Bedrock OK` and `Translate OK`. Then tell the user:
1. Start a **new chat session** in this folder: Kiro loads a project's hooks and agents only when a session starts, and runs no hooks in an untrusted folder ("Restricted Mode": click Manage, then Trust). The hooks are reminders only.
2. Complete the required Builder Center workshop "Building AI Agents with Strands SDK: From Simple Loops to Multi-Agent Swarms" inside the window (28 Oct - 4 Nov). Without it the entry does not qualify.
3. Next: say "pick my idea".
