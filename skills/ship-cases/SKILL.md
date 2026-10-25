---
name: ship-cases
description: Recipe 4 of the strands-ship power. Build and review the human-labelled gold set (cases.jsonl) the measurement gate needs - at least 30 cases, 8 red-flag (hand-off) cases, 10 in Tamil (or your second language), 3 user groups, every case signed off by a named person. Use when the user says "label cases", "build cases", "add cases", "review the cases", or "sign off".
---
# Recipe 4: label the cases

`cases.jsonl` holds one case per line: `id, lang, job (the user group), text, expected {escalation, must_include}, signed_off_by, signed_off_on`, plus any fields your agent needs. `escalation` is `none`, `care` (get checked / ask a person soon) or `emergency` (hand off now: 108, a helpline, a pharmacist). `must_include` lists facts a correct answer must contain. The HeatSafe example adds `temp_c, rh, intensity, full_sun` and `expected.risk_level`.

## Step 1: see what is there
`ss cases check` then `ss cases show`. The generic starter has 3 example lines with EDIT ME (check refuses them until replaced); the HeatSafe example ships 31 draft cases. **Starter labels are drafts, not ground truth.**

## Step 2: make them real
- Write cases from how the user group actually talks (from the five people in IDEA.md). Keep Tamil cases in natural spoken Tamil, not translated English.
- Add adversarial cases: symptoms described indirectly ("he keeps asking what day it is"), negations ("no headache"), mixed Tamil-English, a case that looks like an emergency but is not.
- For every case, a person checks each label against the sources in `agent/data/guidance.json`.
- Run `ss cases check` after edits (the hook reminds you). Fix every ERROR and BELOW MINIMUM line.

## Step 3: sign off
Only the person who read every label signs: `ss cases approve --by "Full Name"` (or `--ids a,b` for some). Never run this for the user without them confirming they read each case; never type a name they did not give you. A named external reviewer (a doctor, an occupational-health worker, a union or NGO lead) makes the evidence much stronger for Gate 2.

Next: say "measure my agent".
