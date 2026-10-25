# Method: how a Workshop-to-Ship agent is built

The workshop ends at multi-agent swarms. Judges score originality as "how far the project extends beyond the lessons", so this kit's agents add four things on top:

1. **Code owns the facts that must never be wrong.** Thresholds, risk levels, amounts and the emergency number live in plain Python (`agent/heat.py`, `agent/safety.py`). The model reads them through a tool and cannot change them; `_enforce()` in `agent/app.py` puts them back if it tries, and prints `[code] corrected`.
2. **A Strands hook stops the agents when a person is in danger.** `RedFlagGate` runs on `BeforeNodeCallEvent` and cancels every graph node, so no model writes the emergency answer.
3. **A graph with a critic loop, not a single prompt.** `GraphBuilder`: planner -> critic -> (conditional edge) planner, at most 2 planner passes. Both use `structured_output_model`, so every plan has the same fields and can be scored.
4. **Measured against a baseline on human-labelled cases.** `ss measure` runs the agent and a one-prompt agent on the same signed cases and blocks submission unless the agent is safe on every case and better than the baseline.

## Rules for the builder (and for Kiro)
- Report only numbers in `results/MEASURE.md` / `results/FACTS.md`. Never type a number into the article or video by hand.
- Never edit `results/` by hand. Never sign off cases for someone else: `ss cases approve --by` takes the reviewer's real name.
- After any change to `agent/heat.py`, `agent/safety.py` or `agent/data/`, re-run `ss measure`.
- Every guidance line needs a source URL and the date you checked it. Every water/shade point needs a person who visited it and a date.
- Never paste AWS keys into chat or files. Credentials come from `aws configure` / `aws sso login` in your own terminal.
- Keep the repo private until 28 Oct 2026; the agent must not be published before the window.
- When a case fails, log it in `FAILURES.md` (what broke, how you found it, what you changed, the re-measured number). Judges trust a project that shows its failures.
