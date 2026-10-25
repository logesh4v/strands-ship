# How the recommendation was made (26 Oct 2026)

Two frontier models judged the hackathon brief as an LLM-as-judge pair: **Claude Opus 5.5** and **GPT-5.6 sol**, run through Kiro. Three rounds.

## Round 1: independent proposals (each saw only the brief)
| | Opus 5.5 | GPT-5.6 sol |
|---|---|---|
| Default pick | Padippu: Tamil Nadu textbook chapter -> cited, leveled practice, with a verifier | HeatSafe Shift: heat-safety plans for outdoor workers |
| Score (rubric 4 x 10 + feasibility 10) | 39/50 (feasibility 9) | 44/50 (originality 9) |
| Main argument | A scaffold can carry it all the way in a week | Higher impact and originality; Padippu copies the page's own example |

Both, without seeing each other, named the same top risk: **impact claimed but not measured**. Both asked for a gate: human-signed cases, a one-prompt baseline on the same cases, raw outputs, and a documented failure.

## Round 2: blind cross-critique (authors hidden as X and Y)
- Opus attacked HeatSafe: "the Tamil voice path probably does not exist"; scope too wide. Attacked Padippu: originality capped, and if a whole user group gets one default, every team ships the same agent.
- GPT attacked HeatSafe: evidence credibility (synthetic cases, stale facilities). Attacked Padippu: it is the brief's example.
- **Both voted for the same hybrid**: HeatSafe Shift + Padippu's measurement gate + a critic -> planner retry. Confidence: Opus 62, GPT 84.
- Remaining disagreement: Opus wanted text-first, GPT wanted voice.

## Fact check by the chairman (AWS docs, 26 Oct 2026)
- Amazon Nova 2 Sonic speaks English, French, Italian, German, Spanish, Portuguese, Hindi: **no Tamil**. (docs.aws.amazon.com/nova/latest/nova2-userguide/sonic-language-support.html)
- Amazon Polly: **no Tamil voice**. Amazon Transcribe: **Tamil ta-IN supported** (speech in). Amazon Translate: **Tamil supported**.

## Round 3: final judge (fresh GPT-5.6 sol, given the facts)
- Text-first (Tamil text via Bedrock + Translate); voice is a stretch goal.
- A 10-20 person user test is optional; signed labelled scenarios are the required evidence.
- Amazon Location routing is a stretch goal; the MVP lists curated, dated points only.
- Default straight to HeatSafe; still offer all three focus areas.
- Ranked alternatives: Padippu (education), Marundhu (health), FloodReady (climate).
- Gate: 30+ cases (8+ emergencies, 10+ Tamil, 3+ job types), 100% emergency recall, 0 unsafe plans, 100% risk-level accuracy, 95%+ citation validity, 90%+ completeness, goal success above baseline, every case signed.
- Confidence 88/100. Residual risk: labelled scenarios and a short demo may not convince experts of real behaviour change.

Full transcripts of all three rounds are kept by the power author.
