---
name: ship-build-agent
description: Recipe 3 of the strands-ship power. Build the builder's own Strands Agents SDK agent in agent/ from IDEA.md and DESIGN.md, composing the runnable Strands blocks (tools, MCP, hooks, interventions, graph, swarm, agents-as-tools, sessions, Decider, Shell, harness, guardrails, voice) and keeping safety in code. Use when the user says "build the agent", "write the agent", "add a block", "run the agent", "change the agent", or asks how the graph, hook or critic works.
---
# Recipe 3: build the agent

Commands go through `~/.strands-ship/bin/ss` (written `ss`). Read `IDEA.md`, `DESIGN.md` and `.kiro/steering/ship-method.md` first. Code for every block is in `~/.strands-ship/kit/blocks/` (a working, live-tested file each); the full worked example is `~/.strands-ship/kit/examples/heatsafe/agent/`. For any API question use the `strands-agents` MCP server; do not guess. If DESIGN.md does not exist, run recipe 2 first.

## Step 1: run the starter as it is
`ss run "a real message from your user group"`. The starter (`agent/app.py`) is a planner -> critic graph with a red-flag hook and structured output. Show the `[safety] [critic] [plan]` lines and explain them in one sentence each.

## Step 2: make the domain real (in this order)
1. **The decision that must never be wrong** (from DESIGN.md) goes in plain Python: a `@tool` with sourced thresholds, or a hook, or Decider above a calibrated threshold. The model reads it; code puts it back if the model changes it (see `_enforce()` in the HeatSafe example) and prints `[code] corrected`.
2. **Red flags**: replace `RED_FLAGS` and `HANDOFF` in `agent/app.py` with the user group's real danger signs and the real number or person to hand off to, in every language they use. Cite the source for each number in a comment.
3. **Sources**: replace `agent/data/guidance.json`. Every item needs a source and the date someone read it. The planner may cite only these ids.
4. **Output fields**: edit `Answer` in `agent/plan.py` so every field can be checked by `agent/score.py`.

## Step 3: add the blocks DESIGN.md chose
Open each block file and copy the pattern, not the demo data: `b01_tools` (tools + structured output), `b02_mcp` (MCP servers), `b03_hooks` (hard stop), `b04_interventions` (Deny / Guide / Confirm), `b05_graph` (counted loop), `b06_swarm` (handoffs), `b07_agents_as_tools`, `b08_sessions` (remember a person), `b09_decider` (fast calibrated decision), `b10_shell` (sandboxed data work; one Shell per thread), `b11_harness` (assembled agent), `b12_evals` (red-team), `b13_voice` (Nova Sonic: no Tamil), `b14_guardrails` (Bedrock Guardrails). After each addition run `ss run "..."` and show the new evidence line. Keep `baseline.py` as one agent with one prompt and the same sources: it is what you must beat.

## Step 4: fail closed
If a checker never passes, ship only fixed, sourced text (HeatSafe's `_enforce(..., critic_ok=False)` shows how). If Decider's confidence is below your threshold, ask a person. If a tool errors, say so plainly. Never let the model fill a gap in a safety answer.

## Step 5: Tamil and other languages
Tamil text from the model can be wrong; keep warning signs, emergency text and first-aid steps as fixed lists in code (the HeatSafe example does), and have a fluent reader check them. Amazon Translate is a fallback, not a reviewer.

After any change to safety code or `agent/data/`, re-run recipe 5 (measure). Next: say "label cases".
