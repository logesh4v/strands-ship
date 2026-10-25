---
name: ship-design
description: Recipe 2 of the strands-ship power. Turn the builder's IDEA.md into an agent design using the whole Strands toolbox - Strands Agents SDK (tools, MCP, hooks, interventions, graph, swarm, agents-as-tools, sessions, guardrails, voice), Strands harness, Strands Shell, Strands Box, Strands Evals and Strands Labs (Decider) - plus AWS services, and run the chosen blocks live. Use when the user says "design my agent", "which Strands features", "what should I use", "show me the blocks", or asks about harness, box, shell, decider, swarm or graph.
---
# Recipe 2: design the agent

Read `IDEA.md` and `references/strands-catalogue.md` (next to this file) first. For any API detail, ask the `strands-agents` MCP server (search_docs / fetch_doc); for AWS facts, `aws-knowledge-mcp-server`. Never guess an API or a model's language support.

## Step 1: show the toolbox, then narrow it
`ss blocks` lists the 14 runnable blocks with their status (LIVE / KEY / DOC). Do not walk the user through all of them. From IDEA.md, pick the **spine** (one pattern from catalogue section 7) and **3-5 blocks** that each do a visible job for this user group. For each pick, say in one line: the job it does, the rubric quarter it helps, and how it will show up in the measured results or the video.
Push back on blocks that do no job ("Box because it is new" is not a reason; Box is for sandboxing your coding agent while you build).

## Step 2: run the chosen blocks live
`ss block <name>` for each pick (about 5-20 s each on Nova 2 Lite). Show the evidence lines. If a block needs a key or resource (`decider` needs `DECIDER_API_KEY` from awsugmdu.in; `guardrails` needs a Bedrock guardrail), tell the user exactly what to set in their own terminal; never ask for the key in chat.

## Step 3: write DESIGN.md (with the user)
- **The decision that must never be wrong**, and which code owns it (a `@tool` with fixed thresholds, a hook, Decider above a calibrated threshold). Name the source for every threshold or number.
- **The flow**: a 5-line diagram (input -> gate -> agents -> checks -> output).
- **Blocks used**, each with its job and the file it will live in under `agent/`.
- **AWS services**, each with its job (catalogue section 6).
- **What is measured**: the case fields and the metrics `agent/score.py` will compute, and the one-prompt baseline it must beat.
- **What is out of scope** for one week (stretch goals).
- **Beyond the workshop**: one sentence on what goes past a plain swarm.

## Step 4: sanity check against the rubric
Score the design 1-10 on the four rubric quarters plus "buildable in the days left". If any is under 6, change the design, not the score. Then: say "build the agent".
