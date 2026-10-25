# Strands Workshop to Ship: AWS UG MDU Cook Book

A Kiro power by **Logesh** (AWS User Group Madurai) for the AWS Builder Center hackathon **Strands SDK: Workshop to Ship** (28 Oct - 4 Nov 2026).

Bring **your own** social-good idea. The power helps your team brainstorm it from the people you can actually reach, design it from the whole Strands toolbox, build it on Amazon Bedrock, prove it beats a plain prompt, record the demo from a live run, and check the submission. Everything runs from Kiro chat, one sentence at a time.

There is no default project. When a whole community ships the same agent, every team loses originality points, so each team starts from its own users and problem. One fully built agent, **HeatSafe Shift**, is included as a worked example to learn from.

## The recipes

| Say in Kiro chat | What happens | You get |
|---|---|---|
| **set up strands ship** | Checks the machine, installs the kit once, sets up a generic starter, tests Bedrock and Translate | `agent/`, `cases.jsonl`, `.kiro/` |
| **brainstorm** | Starts from people you reach and a real story; three ideas scored on the rubric; argued for and against; kept distinct from other teams | `IDEA.md` |
| **design my agent** | Picks the 3-5 Strands blocks that each do a visible job for your users, runs them live, writes the design | `DESIGN.md` |
| **build the agent** | Composes your agent from the blocks, safety in code, fail-closed | `agent/` |
| **label cases** | Your user group's real messages, labelled and signed by a named person | `cases.jsonl` |
| **measure my agent** | Your agent vs a one-prompt baseline on the same signed cases, plus the submission gate | `results/MEASURE.md` |
| **record the video** | Films a live run with evidence badges and your measured numbers, under 3 minutes | `results/demo.mp4` |
| **submission check** | Facts for the article, README and article drafts, a PASS / FAIL / HUMAN list | `SUBMISSION.md` |

## The Strands toolbox: 14 runnable blocks

`ss blocks` lists them; `ss block <name>` runs one live. Each is one short, working file in `kit/blocks/`, written from the official docs and run against Amazon Bedrock (Nova 2 Lite) on 26 Oct 2026. The full map, with when each one earns its place in a social-good agent, is [`skills/ship-design/references/strands-catalogue.md`](skills/ship-design/references/strands-catalogue.md).

| Block | Strands project | What it shows | Status |
|---|---|---|---|
| `tools` | Agents SDK | `@tool` + Pydantic structured output | Live-tested |
| `mcp` | Agents SDK | `MCPClient` on the AWS Knowledge MCP server | Live-tested |
| `hooks` | Agents SDK | A hook cancels the model call on crisis words, fixed helpline reply | Live-tested |
| `interventions` | Agents SDK | `Deny` without consent, `Guide` to shorten an SMS | Live-tested |
| `graph` | Agents SDK | `GraphBuilder` writer -> checker -> writer, counted loop | Live-tested |
| `swarm` | Agents SDK | `Swarm` triage handing off to specialists (the workshop's end point) | Live-tested |
| `agents-as-tools` | Agents SDK | `Agent.as_tool()`: simplifier then Tamil translator | Live-tested |
| `sessions` | Agents SDK | `FileSessionManager`: a new Agent remembers the student | Live-tested |
| `decider` | Labs: Strands Decider | Calibrated yes/no and choice answers via the UG Madurai hosted API | Needs `DECIDER_API_KEY` (endpoint checked) |
| `shell` | Strands Shell | Sandboxed data work; host files are not visible | Live-tested |
| `harness` | Strands harness | `create_harness` with your tool, coding tools off | Live-tested |
| `evals` | Strands Evals | `AdversarialCaseGenerator` red-team + rubric judge | Live-tested (6/6 attacks held) |
| `voice` | Agents SDK (BidiAgent) | Nova Sonic voice with tools and barge-in. Nova Sonic has no Tamil | From the official quickstart; needs a microphone |
| `guardrails` | Bedrock + Agents SDK | Bedrock Guardrails on the model, PII redaction | Needs a Bedrock guardrail id |

The catalogue also covers what has no block: Workflow and A2A, memory stores, plugins and skills, steering, Cedar authorization, **Strands Box** (a macOS policy sandbox for running your coding agent while you build), Strands Evals' trace evaluators, user simulation and chaos testing, the other Strands Labs projects, and the AWS services that read as a "novel use" when they do a real job (Translate, Transcribe ta-IN, Location Service, Bedrock AgentCore).

## Worked example: HeatSafe Shift

A Tamil/English agent that turns the weather, the job and any symptoms into a safe plan for one outdoor shift. Code owns the heat index (NWS formula), the risk level (OSHA bands), water, warning signs and the 108 call. A Strands hook stops every agent on heat-stroke signs. A planner -> critic graph writes and checks the plan, and fails closed when the critic never passes. See it with `ss init --example heatsafe` in a separate folder.

Measured on its 31 draft cases (8 emergencies, 11 in Tamil), the same Nova 2 Lite model on both sides:

| | HeatSafe Shift | One-prompt baseline |
|---|---|---|
| Emergencies sent to 108 | **100%** | 88% |
| Plans with unsafe advice | **0** | 21 |
| Risk level correct | **100%** | 32% |
| Goal success (Strands Evals judge, 0-1) | **1.0** | 0.76 |

Across three full runs the baseline had 21-24 unsafe plans; HeatSafe Shift had 0 each time. The cases are the author's drafts. Your own agent gets its numbers from your own signed cases. How two frontier models judged this and three other example ideas is in [`skills/ship-brainstorm/references/council.md`](skills/ship-brainstorm/references/council.md): reuse the method, not the idea.

## Install

**You need:** Kiro (IDE or CLI); macOS or Linux (Windows: WSL2); Python 3.10-3.13; git; an AWS account with Amazon Bedrock (Amazon Nova enabled in us-east-1) and Amazon Translate. `uv` and `ffmpeg` are recommended. About 400 MB of disk, plus about 150 MB for the video browser.

Install the power, any one of:
- Kiro IDE: Powers panel -> Add Custom Power -> **Import power from GitHub** -> `https://github.com/logesh4v/strands-ship`
- Kiro IDE: clone this repo, then Add Custom Power -> **Import power from a folder**
- Kiro CLI: `kiro-cli powers install <path-to-clone>`

Open an empty project folder and say **"set up strands ship"**. When it finishes, start a **new chat session**: Kiro loads a project's hooks only when a session starts (click Manage -> Trust if you see "Restricted Mode").

AWS credentials and the Decider key stay in your own terminal (`aws configure`, `aws sso login`, `export DECIDER_API_KEY=...`). Never paste them into chat.

Prefer the terminal?
```bash
python3 skills/ship-setup/scripts/ship.py setup
mkdir ~/my-agent && cd ~/my-agent && ~/.strands-ship/bin/ss init && ~/.strands-ship/bin/ss bedrock
~/.strands-ship/bin/ss blocks
~/.strands-ship/bin/ss block hooks
```

## Commands (`~/.strands-ship/bin/ss`)

`init [--example heatsafe] [--update]`, `blocks`, `block <name>`, `status`, `bedrock`, `run "message" [...]`, `cases check|show|approve --by "Name"`, `measure [--limit N]`, `video`, `ship`. Add `--help`.

## MCP servers

Configured in `mcp.json`, both live-tested:
- **strands-agents** (`uvx strands-agents-mcp-server@0.3.0`): search and read the Strands docs while you build.
- **aws-knowledge-mcp-server** (`https://knowledge-mcp.global.api.aws`): AWS docs, What's New, regional availability. No credentials needed.

**Pinned and tested:** Strands Agents 1.62.0, Strands Agents Tools 0.8.10, Strands Evals 1.7.0, Strands harness 0.3.2, Strands Shell 0.5.0, boto3 1.43.118, Pydantic 2.14.1, Playwright 1.63.0, on Python 3.12 and 3.13 (macOS). Your project repo runs without the power: `ss init` copies `ship_kit/` (Apache-2.0) and a pinned `requirements.txt`.

## Limits, said plainly

- Blocks marked "needs a key / id / microphone" were not run end to end by the author; their code follows the official docs and the parts that could be checked were (the Decider endpoint answers, the Bedrock guardrail parameters exist).
- Strands Box is pre-release (0.1.x) and macOS-only; the catalogue describes it from its docs.
- Model-written Tamil can be wrong. Keep safety text as fixed lists in code and have a fluent reader check them.
- Measured numbers show safer, more accurate answers than a one-prompt agent on labelled cases. They do not show that people behave differently; a consented field test would.
- Nova 2 Sonic and Amazon Polly do not speak Tamil. Amazon Transcribe accepts Tamil speech (ta-IN).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `doctor` blocks on Python | Install Python 3.12 (`brew install python@3.12`) |
| `ss bedrock`: credentials | `aws configure` or `aws sso login` in your terminal; set `AWS_PROFILE` if not default |
| `ss bedrock`: access denied or payment instrument | Enable Amazon Nova in Bedrock Model access, or choose another model with `SHIP_MODEL` (Anthropic models need an AWS Marketplace subscription) |
| `ss block decider` says no key | Get a free team key on [awsugmdu.in](https://www.awsugmdu.in), `export DECIDER_API_KEY=...` |
| `ss cases check`: EDIT ME | Replace the example lines with your own cases |
| Gate fails on sign-off | `ss cases show`, read every label, then `ss cases approve --by "Your Name"` |
| `ss video` cannot start a browser | `~/.strands-ship/venv/bin/python -m playwright install chromium` |
| Remove everything | `python3 skills/ship-setup/scripts/ship.py uninstall --yes` |

## Licence

Apache-2.0. Built by Logesh for the AWS User Group Madurai community.
