---
name: ship-build-agent
description: Recipe 2 of the strands-ship power. Run, understand and adapt the Strands Agents SDK agent in agent/ (HeatSafe Shift by default) for the user's worker group, language and district. Use when the user says "build the agent", "run the agent", "change the agent", "add a worker group", or asks how the graph, hook or critic works.
---
# Recipe 2: build the agent

Commands go through `~/.strands-ship/bin/ss` (written `ss`). Read `.kiro/steering/ship-method.md` and `IDEA.md` first. For Strands API questions use the `strands-agents` MCP server (search_docs, fetch_doc); for AWS facts use `aws-knowledge-mcp-server`. Do not guess an API.

## Step 1: run it as shipped (three live runs, about 10 s each)
1. `ss run "I am laying bricks on a roof from 1pm to 5pm today." --temp 37 --rh 50 --intensity heavy --sun --job construction --lat 9.92 --lon 78.12`
2. `ss run "இன்று மதியம் சாலை வேலை. எனக்கு தலைசுற்றுகிறது." --temp 36 --rh 55 --sun --job "road work"`
3. `ss run "My coworker is confused and talking nonsense" --temp 38 --rh 45 --intensity heavy`
Show the `[risk] [safety] [critic] [code] [lang] [plan]` lines and explain each in one sentence. Without `--temp`, give `--lat --lon` and the weather comes from Open-Meteo (free, no key).

## Step 2: explain who owns what (the originality story)
- `agent/heat.py`: US NWS heat index + OSHA risk bands, plus the kit's one-level bump for heavy work or full sun. Code only.
- `agent/safety.py`: red-flag phrases (English and Tamil) from NIOSH heat-illness signs. `RedFlagGate` is a Strands hook on `BeforeNodeCallEvent` that cancels every node; the emergency text is fixed.
- `agent/app.py`: `GraphBuilder` planner -> critic -> conditional edge back to planner (max 2 passes), `ShiftPlan` structured output, `_enforce()` puts back every code-owned field and prints `[code] corrected`, Amazon Translate if a Tamil user got English.
- `agent/data/guidance.json`: the only sources the planner may cite. `agent/data/places.geojson`: SAMPLE points that must be replaced.

## Step 3: make it theirs (from IDEA.md)
- Worker group: add their job's real hazards and times to the planner prompt in `agent/app.py` (PLANNER), and their wording to `agent/safety.py` lists (in both languages).
- District: replace every feature in `places.geojson` with points a person visited; set `verified_on` and `verified_by`. Until then the plan says "NOT checked yet".
- Guidance: add items only with a source URL and the date read. Indian sources (NDMA heat-wave guidelines, the Tamil Nadu Heat Action Plan 2026) are good additions if the user reads them.
- Emergency number outside Tamil Nadu: change `NUMBER` and `TEXT` in `agent/safety.py`.
- Tamil text in `heat.py` and `safety.py` was written by the power author; have a fluent reader check it before the video.
After any change to `heat.py`, `safety.py` or `data/`, re-run recipe 4 (measure). Do not change thresholds without a cited source.

## Stretch goals (only after recipe 4 passes)
Amazon Transcribe ta-IN speech input; English/Hindi voice replies with Nova 2 Sonic (no Tamil voice exists); Amazon Location Service routing once points are checked; Bedrock Knowledge Bases; deploy to Amazon Bedrock AgentCore. Each one must appear in the measured results or the article's limits, not just the architecture diagram.

Next: say "label cases".
