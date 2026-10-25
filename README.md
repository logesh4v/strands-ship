# Strands Workshop to Ship: AWS UG MDU Cook Book

A Kiro power by **Logesh** (AWS User Group Madurai) for the AWS Builder Center hackathon **[Strands SDK: Workshop to Ship](https://builder.aws.com)** (28 Oct - 4 Nov 2026).

You get a working social-good agent built with the **Strands Agents SDK** on Amazon Bedrock, a way to prove it beats a plain prompt, a demo video recorded from a live run, and a submission checklist. Everything runs from Kiro chat, one sentence at a time.

## The agent it gives you: HeatSafe Shift

Outdoor workers in Tamil Nadu (construction, road, sanitation, farm, kiln, salt pan, delivery, street vending) work through the hottest hours. HeatSafe Shift turns the weather, the job and any symptoms into a safe plan for one shift, in **Tamil or English**.

- **Code owns what must never be wrong**: the heat index, the risk level, how much water, the warning signs and the 108 emergency call.
- **A Strands graph writes the plan**: a planner agent, a critic agent that checks it, and a loop back to the planner.
- **A Strands hook stops the agents** the moment someone describes heat-stroke signs, and sends the fixed 108 instruction instead.

### Measured, not claimed

31 labelled cases (8 emergencies, 11 in Tamil, 8 job types), the same Amazon Nova 2 Lite model for both sides. The baseline is one agent with one prompt and the same guidance pasted in.

| | HeatSafe Shift | One-prompt baseline |
|---|---|---|
| Emergencies sent to 108 | **100%** | 88% |
| Plans with unsafe advice | **0** | 21 |
| Risk level correct | **100%** | 32% |
| Plan complete, in the worker's language | **100%** | 73% |
| Goal success (Strands Evals judge, 0-1) | **1.0** | 0.76 |

Measured 26 Oct 2026 on a clean install. Across three full runs the baseline had 21-24 unsafe plans; HeatSafe Shift had 0 every time. These are the author's draft cases: your numbers come from your own signed cases (`ss measure`).

### Why this idea

Two frontier models, Claude Opus 5.5 and GPT-5.6 sol, judged six candidate ideas against the hackathon rubric in a three-round LLM-as-judge council: independent proposals, a blind cross-critique, then a final judge. Both ended on HeatSafe Shift (final confidence 88/100). The full record, including where they disagreed and how it was settled, is in [`skills/ship-pick-idea/references/council.md`](skills/ship-pick-idea/references/council.md).

Prefer another focus area? The power ranks three alternatives and gives you a runnable skeleton for each: **Padippu** (education: cited Tamil/English practice from textbooks), **Marundhu Clear** (health: plain-language prescriptions with pharmacist hand-off), **FloodReady** (climate: a household flood plan that is stress-tested).

## Install

**You need:** Kiro (IDE or CLI); macOS or Linux (Windows: WSL2); Python 3.10-3.13; git; an AWS account with Amazon Bedrock (Amazon Nova enabled in us-east-1) and Amazon Translate. `uv` and `ffmpeg` are recommended. About 400 MB of disk, plus about 150 MB for the video browser.

Install the power, any one of:
- Kiro IDE: Powers panel -> Add Custom Power -> **Import power from GitHub** -> `https://github.com/logesh4v/strands-ship`
- Kiro IDE: clone this repo, then Add Custom Power -> **Import power from a folder**
- Kiro CLI: `kiro-cli powers install <path-to-clone>`

Open an empty project folder and say **"set up strands ship"**. When it finishes, start a **new chat session** (Kiro loads a project's hooks only when a session starts; click Manage -> Trust if you see "Restricted Mode").

AWS credentials stay in your own terminal (`aws configure` or `aws sso login`). Never paste keys into chat.

## The recipes

| Say in Kiro chat | What happens | You get |
|---|---|---|
| **set up strands ship** | Checks the machine, installs the kit once, sets up the folder, tests Bedrock and Translate | `agent/`, `cases.jsonl`, `.kiro/` |
| **pick my idea** | The recommendation scored on the rubric, the ranked alternatives, five questions that make it yours | `IDEA.md` |
| **build the agent** | Runs the agent live three ways, explains who owns what, adapts it to your workers and district | `agent/` |
| **label cases** | Review and extend the starter cases; a named person signs off | `cases.jsonl` |
| **measure my agent** | Agent vs one-prompt baseline on the same signed cases, plus the submission gate | `results/MEASURE.md` |
| **record the video** | Films a live run with evidence badges and your measured numbers, under 3 minutes | `results/demo.mp4` |
| **submission check** | Facts for the article, README and article drafts, a PASS / FAIL / HUMAN list | `SUBMISSION.md` |

Prefer the terminal?
```bash
python3 skills/ship-setup/scripts/ship.py setup
cd ~/my-heatsafe && ~/.strands-ship/bin/ss init && ~/.strands-ship/bin/ss bedrock
~/.strands-ship/bin/ss run "I am laying bricks on a roof from 1pm to 5pm" --temp 37 --rh 50 --intensity heavy --sun
```

## How it works

```
worker message ─► [risk]  code: NWS heat index + OSHA bands ─────────────┐
                  [safety] Strands hook: heat-stroke signs? ─► cancel all agents ─► fixed "call 108"
                  Strands GraphBuilder:  planner ─► critic ─(revise, max 2)─► planner
                  [code]  put back every code-owned field; critic never passed -> fixed text only
                  [lang]  Tamil speaker got English? -> Amazon Translate
                  ShiftPlan (structured output) ─► the worker
```

| Piece | File | What it does |
|---|---|---|
| Heat risk | `agent/heat.py` | US NWS heat index; OSHA bands (below 91 F lower, 91-103 moderate, 103-115 high, above 115 extreme); one level up for heavy work or full sun |
| Red-flag gate | `agent/safety.py` | NIOSH heat-illness signs in English and Tamil; a hook on `BeforeNodeCallEvent` cancels every graph node |
| Graph | `agent/app.py` | Planner (tools: heat risk, curated guidance, nearest checked water points) and critic, both with Pydantic structured output |
| Guidance | `agent/data/guidance.json` | The only sources the agent may cite (OSHA, NIOSH, NWS, TN 108), each with a date |
| Baseline | `agent/baseline.py` | One agent, one prompt, same model, same guidance |
| Measurement | `ship_kit/measure.py` | Deterministic safety scoring plus a Strands Evals judge, by language and job; blocks submission until the agent is safe on every case and beats the baseline |
| Video | `ship_kit/video.py` | A headless browser films a studio page while the real commands run |

Your project repo runs without the power: `ss init` copies `ship_kit/` (Apache-2.0) and a pinned `requirements.txt`.

**Pinned and tested:** Strands Agents 1.62.0, Strands Agents Tools 0.8.10, Strands Evals 1.7.0, boto3 1.43.118, Pydantic 2.14.1, Playwright 1.63.0; Python 3.12 and 3.13 on macOS.

## MCP servers

Configured in `mcp.json`, both live-tested:
- **strands-agents** (`uvx strands-agents-mcp-server@0.3.0`): search and read the Strands docs.
- **aws-knowledge-mcp-server** (`https://knowledge-mcp.global.api.aws`): AWS docs, What's New, regional availability. No credentials needed.

## Limits, said plainly

- The 31 starter cases and labels are drafts. Rewrite many in your workers' own words, and have a named person read and sign every case.
- The water and shade points are samples near Madurai. Replace them with places someone visited.
- The red-flag gate is a phrase list. It misses wording it has never seen; `ss measure` proves recall on your cases, not on every sentence.
- Have a fluent reader check the Tamil in `agent/heat.py` and `agent/safety.py` before you film.
- The numbers show safer, more accurate plans than a one-prompt agent on labelled scenarios. They do not show that workers behave more safely; a consented field test would.
- No Tamil voice: Amazon Nova 2 Sonic and Amazon Polly do not speak Tamil. Amazon Transcribe does take Tamil speech, which is a stretch goal.
- Many teams from one user group should not ship the same agent. Pick your own worker group and district.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `doctor` blocks on Python | Install Python 3.12 (`brew install python@3.12`) |
| `ss bedrock`: credentials | `aws configure` or `aws sso login` in your terminal; set `AWS_PROFILE` if not default |
| `ss bedrock`: access denied or payment instrument | Enable Amazon Nova in Bedrock Model access, or choose another model with `SHIP_MODEL` |
| Gate fails on sign-off | `ss cases show`, read every label, then `ss cases approve --by "Your Name"` |
| `ss video` cannot start a browser | `~/.strands-ship/venv/bin/python -m playwright install chromium` |
| Tamil shows as boxes | Install a Tamil font (Ubuntu: `sudo apt install fonts-noto-core`) |
| Remove everything | `python3 skills/ship-setup/scripts/ship.py uninstall --yes` |

## Licence

Apache-2.0. Built by Logesh for the AWS User Group Madurai community.
