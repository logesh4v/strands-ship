# The Strands toolbox, for social-good agents

Every row says what the piece is, when it earns its place in a social-good agent, which rubric quarter it helps, and **how sure we are it works**: `LIVE` = a block in `~/.strands-ship/kit/blocks/` ran against Amazon Bedrock on 26 Oct 2026 with the pinned versions; `KEY` = live-tested code path, needs your key or resource to run; `DOC` = written from the official docs, not run by the power author. Run any block with `ss block <name>`; read its file for the code.

Pinned: strands-agents 1.62.0, strands-agents-tools 0.8.10, strands-agents-evals 1.7.0, strands-harness 0.3.2, strands-shell 0.5.0, strands-decider 0.2.0 (local, optional).

**How to choose.** Start from the problem, not the feature list. A judge rewards three or four pieces that each do a visible job (and show up in your measured results) over ten pieces bolted on. The workshop ends at multi-agent swarms, so "originality" means going past a plain swarm: something code-owned, a control layer, a measured decision, a novel AWS service.

## 1. Strands Agents SDK: the agent itself

| Block | What it is | Use it when | Rubric | Status |
|---|---|---|---|---|
| `tools` | `Agent` + `@tool` + `structured_output_model` (Pydantic) | Always. Tools look facts up; structured output gives every answer the same fields so you can score it | Technical | LIVE |
| `mcp` | `MCPClient` over stdio or streamable HTTP | You need an existing tool service: AWS Knowledge, a data API, Strands Shell (`uvx strands-shell --mcp`) | Technical, Originality | LIVE |
| `hooks` | `HookProvider` callbacks on loop events (`BeforeModelCallEvent.cancel`, `BeforeToolCallEvent.cancel_tool`, `BeforeNodeCallEvent.cancel_node`) | Something must never be left to the model: crisis words, a dose change, a child's name | Impact, Originality | LIVE |
| `interventions` | `InterventionHandler` returning `Proceed`, `Deny`, `Guide`, `Confirm`, `Transform` | Rules on tool calls: consent before an SMS (Deny), "shorter please" (Guide = steering), a person approves (Confirm, an interrupt you resume), redact before sending (Transform) | Technical, Impact | LIVE (Deny, Guide); DOC (Confirm, Transform) |
| `graph` | `GraphBuilder` with conditional edges, `set_max_node_executions`, `reset_on_revisit` | You know the steps and want a counted quality loop: writer -> checker -> writer | Technical, Originality | LIVE |
| `swarm` | `Swarm` of agents that hand off to each other | The path depends on the case (triage to the right specialist). This is the workshop's end point; pair it with something more | Technical | LIVE |
| `agents-as-tools` | `Agent.as_tool()` | One lead agent stays in charge and calls specialists (simplifier, translator, checker) | Technical | LIVE |
| Workflow, A2A | `strands.multiagent` Workflow; Agent2Agent protocol (`pip install "strands-agents[a2a]"`) | A fixed task DAG; or your agent talks to another team's agent over A2A | Originality | DOC |
| `sessions` | `FileSessionManager` / `S3SessionManager` + `SlidingWindowConversationManager` / `SummarizingConversationManager` | The same person comes back (daily check-in, a tutor tracking progress). It also gives you before/after data per person | Impact | LIVE |
| Memory | `memory_manager` on Agent; Bedrock Knowledge Base memory store | Durable facts across sessions (not the whole chat) | Technical | DOC |
| Plugins and skills | `strands.plugins` (Skills, Context Offloader, Context Injector, GoalLoop) | Long tasks, big tool results, loading Agent Skills folders | Technical | DOC |
| Steering | Python steering handlers are plugins; `Guide` is the lightweight form | Context-aware rules that appear only when relevant, instead of a giant prompt | Technical | DOC (Guide is LIVE) |
| Cedar authorization | Intervention backed by a Cedar policy | Who may trigger which tool, written as policy | Originality | DOC |
| `guardrails` | `BedrockModel(guardrail_id=..., guardrail_redact_output=True)` | Users may share Aadhaar numbers, phone numbers, health details; or whole topics must be refused | Impact, Originality | KEY (needs a Bedrock guardrail) |
| `voice` | `BidiAgent` + `BedrockNovaSonicModel`, barge-in, tools while talking | Low-literacy users. **Nova 2 Sonic has no Tamil**: English, French, Italian, German, Spanish, Portuguese, Hindi. For Tamil use Amazon Transcribe ta-IN in, text out | Impact, Communication | DOC (needs a microphone; code follows the official quickstart) |
| Structured output streaming, callbacks, OpenTelemetry traces | `stream_async`, callback handlers, built-in OTel | A live UI, or traces for Strands Evals' trace evaluators | Communication | DOC |
| Other model providers | Anthropic, OpenAI, Gemini, Ollama, LiteLLM, llama.cpp, SageMaker | Local/offline (Ollama) or cost. Hackathon is Strands, Bedrock recommended | - | DOC |

## 2. Strands harness: an assembled agent in one call

| Block | What it is | Use it when | Status |
|---|---|---|---|
| `harness` | `create_harness(model=..., instructions=..., tools=..., builtin_tools=[...], memory=..., skills=..., interventions=..., session=...)` returns a plain `Agent` with tuned prompt, context management, caching, memory, todos | Your agent is a capable generalist with a domain identity (a scheme-finder that reads pages and keeps notes). Turn off `shell`/`read`/`write`/`edit` for end users: those are coding tools | LIVE (with `builtin_tools=[]`) |

Default model is Claude Opus 5 on Bedrock, which needs an AWS Marketplace subscription; pass `model="bedrock/us.amazon.nova-2-lite-v1:0"` if you do not have one. CLI: `npm install -g @strands-agents/cli`, then `strands`; `/export` writes the code.

## 3. Strands Shell and Strands Box: safe execution

| Block | What it is | Use it when | Status |
|---|---|---|---|
| `shell` | `strands_shell.Shell(binds=[Bind(host, "/data", mode="copy")])`: an in-process sandboxed shell. Only bound folders, no host credentials, network by allowlist. Has cut, sort, grep, head, wc, jq, lua (no awk, no python). One Shell per thread | The agent crunches data (rainfall CSVs, attendance, survey results) with real commands but must not touch the laptop | LIVE (host files not visible: checked) |
| Strands Box | Pre-release (0.1.x) macOS sandbox engine: Seatbelt OS isolation plus Dogwood (Cedar-compatible) policies that decide every command, file, network request and MCP call; deny by default; decision log | Run **your coding agent** (Kiro CLI, the Strands CLI, Claude Code) or a harness agent under a policy while you build. Not something end users touch | DOC |

## 4. Strands Evals: prove it

| Block | What it is | Use it when | Status |
|---|---|---|---|
| `ss measure` | Your agent vs a one-prompt baseline on the same signed cases, deterministic safety scoring + `OutputEvaluator` judge, gate | Always: it is the evidence for the impact quarter | LIVE |
| `evals` | `AdversarialCaseGenerator(...).generate_cases(agent=..., risk_categories=[...])` + `OutputEvaluator` rubric judge | "We attacked it N ways and it held" for the article. Categories: prompt_injection, excessive_agency, sensitive_data, data_exfiltration, social_engineering, privilege_escalation, business_rule_violation | LIVE |
| Trace evaluators | `HarmfulnessEvaluator`, `FaithfulnessEvaluator`, `GoalSuccessRateEvaluator`, `TrajectoryEvaluator`, tool-selection evaluators | Need the agent's trace (run under Strands Evals telemetry); they fail with "actual_trajectory must be a Session" otherwise | DOC |
| Simulation, chaos | `UserSimulator` / `ActorSimulator` multi-turn users; `ChaosPlugin` (empty responses, malformed JSON, tool errors) | Test a multi-turn conversation, or that the agent fails safely when a tool breaks | DOC |

## 5. Strands Labs: experimental

| Block | What it is | Use it when | Status |
|---|---|---|---|
| `decider` | **Strands Decider**: a small decision model. Yes/no, choice and score answers with a calibrated confidence, no generated text. Hosted free by AWS User Group Madurai (`/v1/decide`, 2,000 decisions a month, team key on awsugmdu.in), or local `pip install strands-decider` (PyTorch, about 5 GB RAM) | One fast decision you branch on: is this an emergency, which helpline, how urgent. Act only above a threshold you calibrated on your own labelled cases | KEY (endpoint answers; needs `DECIDER_API_KEY`) |
| AI Functions | Python functions evaluated by agents, with runtime post-conditions | A step whose output you can check in code | DOC |
| Harness Optimizer, Benchmark Harnesses, Robots, Cosmos, PyWebRTC Audio | Tuning harnesses from trajectories; benchmark agents; robotics; video world models; echo cancellation for BidiAgent | Rarely needed for this hackathon | DOC |

## 6. AWS services that read as "novel use" when they do a real job

| Service | Job in a social-good agent | Notes |
|---|---|---|
| Amazon Bedrock | The models; Guardrails; Knowledge Bases for long curated sources | Nova needs no Marketplace subscription |
| Amazon Translate | Tamil/English answers when the model slips | Tamil `ta` supported |
| Amazon Transcribe | Tamil speech in (`ta-IN`, batch and streaming) | Polly and Nova Sonic do not speak Tamil |
| Amazon Location Service | Routes to shelters, clinics, cooling points | Only after a person has checked the places |
| Amazon Bedrock AgentCore | Deploy the agent (Runtime), give it memory, identity and gateways | `pip install bedrock-agentcore` (1.25.0); Strands docs: Deploy -> Amazon Bedrock AgentCore |
| AWS Lambda, Amazon S3, Amazon DynamoDB, Amazon EventBridge Scheduler | A small API, files, per-user state, a daily scheduled run | |
| AWS Knowledge MCP server | Up-to-date AWS facts for your coding agent and your agent | `mcp` block |

## 7. Patterns that combine well (pick one as your spine)

- **Code owns the facts, the model writes the words**: deterministic `@tool` + `_enforce()` + structured output (HeatSafe Shift does this).
- **Hard stop on danger**: `hooks` gate or Decider urgency -> fixed text, no model output.
- **Counted quality loop**: `graph` writer -> checker -> writer, with a fail-closed fallback when the checker never passes.
- **People in control**: `interventions` Confirm before any message leaves, Deny without consent.
- **Remember the person**: `sessions` + a daily check-in, which also gives before/after numbers.
- **Safe data work**: `shell` over the user's own files.
- **Proof**: `ss measure` + `evals` red-team, quoted in the article.
