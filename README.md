# Strands Workshop to Ship: AWS UG MDU Cook Book

The strands-ship cookbook, a Kiro power by S Logesh (AWS User Group Madurai).

Ship a social-good agent built with the **Strands Agents SDK** on Amazon Bedrock for the AWS Builder Center hackathon **Strands SDK: Workshop to Ship** (28 Oct - 4 Nov 2026), from chat in Kiro. It recommends the strongest idea, gives you a working agent for it, measures it against a one-prompt baseline, records the demo video from a live run, and checks the submission.

**The recommended idea, HeatSafe Shift** (climate resilience): a Tamil/English agent that turns the forecast, the job and any symptoms into a safe plan for one outdoor shift. Code owns the heat thresholds and the 108 emergency call; a Strands graph (planner, critic, retry) writes and checks the plan. Two frontier models (Claude Opus 5.5 and GPT-5.6 sol) picked it over twelve other candidates in a three-round LLM-as-judge council; the record is in `skills/ship-pick-idea/references/council.md`. Education, health and a second climate path are offered as ranked alternatives with a runnable skeleton.

| Say in Kiro chat | What happens | Output in your project |
|---|---|---|
| **set up strands ship** | Checks the machine, installs the kit once (about 400 MB), sets up the folder, checks Bedrock and Translate | `~/.strands-ship/`, `agent/`, `cases.jsonl`, `.kiro/` |
| **pick my idea** | The council's recommendation scored on the rubric, the ranked alternatives, five questions to make it yours | `IDEA.md` |
| **build the agent** | Runs the agent live three ways, explains who owns what, adapts it to your worker group and district | `agent/` |
| **label cases** | Reviews and extends the 31 starter cases; a named person signs off | `cases.jsonl` |
| **measure my agent** | Agent vs one-prompt baseline on the same signed cases; the submission gate | `results/MEASURE.md`, raw outputs |
| **record the video** | Films a live run with evidence badges and the measured results, under 3 minutes | `results/demo.mp4` |
| **submission check** | FACTS.md from measured numbers, README and article drafts, PASS / FAIL / HUMAN list | `SUBMISSION.md`, `results/FACTS.md` |

## What you need
- **Kiro** (IDE or CLI).
- **macOS or Linux** (Windows: use WSL2 Ubuntu). **Python 3.10-3.13** and **git**. About 400 MB of disk, plus about 150 MB for the video browser.
- **uv** (for the Strands docs MCP server, `uvx`) and **ffmpeg** (mp4 video) are recommended; the kit works without them.
- **Your own AWS account with Amazon Bedrock**: Amazon Nova 2 Lite enabled in us-east-1 (default; set `SHIP_MODEL` / `AWS_REGION` to change), and Amazon Translate. Credentials from `aws configure` or `aws sso login` in your own terminal. Anthropic models on Bedrock need an AWS Marketplace subscription; Nova does not. Calls are billed to your account; a full `ss measure` is about 120 Nova 2 Lite calls.

## Install the power
Any one of:
- Kiro IDE: Powers panel -> Add Custom Power -> **Import power from a folder** -> pick this folder.
- Kiro IDE: Add Custom Power -> **Import power from GitHub** -> the repo URL, if you got one.
- Kiro CLI: `kiro-cli powers install <path-to-this-folder>`

Then open your project folder (an empty folder is fine) and say **"set up strands ship"**. When it finishes, **start a new chat session**: Kiro loads a project's hooks only when a session starts and runs none in an untrusted folder (click Manage, then Trust, if you see "Restricted Mode").

Prefer the terminal?
```bash
python3 skills/ship-setup/scripts/ship.py doctor
python3 skills/ship-setup/scripts/ship.py setup
cd ~/my-heatsafe && ~/.strands-ship/bin/ss init && ~/.strands-ship/bin/ss bedrock
```

## How HeatSafe Shift works
- **Code owns what must never be wrong.** Heat index (US NWS formula) and risk level (OSHA bands, plus one level for heavy work or full sun) in `agent/heat.py`; water amount and the fixed work/rest steps per level; the emergency answer. The model reads them through a tool; `_enforce()` puts them back if it changes them and logs `[code] corrected`.
- **A Strands hook stops the agents in an emergency.** `RedFlagGate` (on `BeforeNodeCallEvent`) cancels every graph node when the message carries a heat-stroke sign (NIOSH list, English and Tamil). The 108 instruction is fixed text.
- **A graph, not a prompt.** `GraphBuilder`: planner (tools: heat risk, curated guidance, nearest checked water/shade points; `ShiftPlan` structured output) -> critic (`Critique` structured output) -> conditional edge back to the planner, at most two passes.
- **Tamil first.** Amazon Bedrock writes Tamil directly; if a Tamil speaker gets English, Amazon Translate fixes it and logs `[lang]`. (Amazon Nova 2 Sonic and Amazon Polly have no Tamil voice, so voice is a stretch goal; Amazon Transcribe does take Tamil speech.)
- **Measured, not claimed.** `ss measure` scores the agent and a one-prompt baseline (same model, same guidance) on the same human-signed cases: 108 recall, unsafe advice, risk accuracy, citation validity, completeness, Strands Evals goal success, by language and job. Submission is blocked until the agent is safe on every case and beats the baseline.
- **Your repo runs without the power.** `ss init` copies `ship_kit/` (Apache-2.0) and a pinned `requirements.txt`.
- **Pinned.** Strands Agents 1.62.0, Strands Agents Tools 0.8.10, Strands Evals 1.7.0, boto3 1.43.118, Pydantic 2.14.1, Playwright 1.63.0; Strands docs MCP server 0.3.0.

## MCP servers (in `mcp.json`)
- `strands-agents`: `uvx strands-agents-mcp-server@0.3.0`, Strands documentation search (`search_docs`, `fetch_doc`). Its GitHub repo moved into the strands-agents harness-sdk monorepo; the PyPI package is current.
- `aws-knowledge-mcp-server`: AWS's managed remote server at `https://knowledge-mcp.global.api.aws` (AWS docs, What's New, regional availability, Strands docs). No AWS credentials needed.

## Commands (`~/.strands-ship/bin/ss`)
`init [--path heatsafe|padippu|marundhu|floodready] [--update]`, `status`, `bedrock`, `run "message" [--temp --rh --intensity --sun --job --lat --lon]`, `cases check|show|approve --by "Name"`, `measure [--limit N]`, `video`, `ship`. Add `--help`.

## Limits, said plainly
- The 31 starter cases and their labels are drafts by the power author; a named person must review and sign every case, and you should rewrite many in your workers' own words.
- The water/shade points are SAMPLES near Madurai; replace them with points someone visited.
- The red-flag gate is a phrase list: it misses wording it has not seen. `ss measure` proves recall on your cases, not on every sentence.
- The Tamil text in `agent/heat.py` and `agent/safety.py` should be checked by a fluent reader before you film.
- The measurements show safer, more accurate plans than a one-prompt agent on labelled scenarios. They do not show workers behave more safely; a consented field test is how you would show that.

## Troubleshooting
| Symptom | Fix |
|---|---|
| `doctor` says BLOCK for Python | Install Python 3.12 (`brew install python@3.12`), run doctor again |
| `ss bedrock`: credentials | `aws configure` or `aws sso login` in your terminal; `AWS_PROFILE` if not default |
| `ss bedrock`: access denied / payment instrument | Enable Amazon Nova in the Bedrock console (Model access), or `SHIP_MODEL=<another model id>` |
| `ss measure` FAIL on sign-off | `ss cases show`, read every label, then `ss cases approve --by "Your Name"` |
| `ss video` cannot launch a browser | `~/.strands-ship/venv/bin/python -m playwright install chromium` |
| Tamil shows as boxes in the video | Install a Tamil font (macOS has Tamil MN; Ubuntu: `sudo apt install fonts-noto-core`) |
| Remove everything | `python3 skills/ship-setup/scripts/ship.py uninstall --yes` |

## Licence
Apache-2.0.
