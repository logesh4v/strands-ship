---
name: ship-cases
description: Recipe 3 of the strands-ship power. Build and review the human-labelled gold set (cases.jsonl) the measurement gate needs - at least 30 cases, 8 emergencies, 10 in Tamil, 3 job types, every case signed off by a named person. Use when the user says "label cases", "build cases", "add cases", "review the cases", or "sign off".
---
# Recipe 3: label the cases

`cases.jsonl` holds one case per line: `id, lang, job, text, temp_c, rh, intensity, full_sun, lat, lon, expected {risk_level, escalation}, signed_off_by, signed_off_on`. `escalation` is `none`, `care` (stop work, get checked) or `emergency` (call 108).

## Step 1: see what is there
`ss cases check` then `ss cases show`. The 31 starter cases cover 8 job types, 8 emergencies, 5 care cases and 11 Tamil cases. Their risk labels were computed from the OSHA bands by the power author: **they are drafts, not ground truth.**

## Step 2: make them real
- Replace at least half of the starter texts with how the user's worker group actually talks (ask a worker, a supervisor or an NGO). Keep the Tamil cases in natural spoken Tamil, not translated English.
- Add adversarial cases: symptoms described indirectly ("he keeps asking what day it is"), negations ("no headache"), mixed Tamil-English, a case that looks like an emergency but is not.
- For every case, a person checks `expected.risk_level` against the NWS heat index chart and `expected.escalation` against the NIOSH symptom list in `agent/data/guidance.json`.
- Run `ss cases check` after edits (the hook reminds you). Fix every ERROR and BELOW MINIMUM line.

## Step 3: sign off
Only the person who read every label signs: `ss cases approve --by "Full Name"` (or `--ids a,b` for some). Never run this for the user without them confirming they read each case; never type a name they did not give you. A named external reviewer (a doctor, an occupational-health worker, a union or NGO lead) makes the evidence much stronger for Gate 2.

Next: say "measure my agent".
