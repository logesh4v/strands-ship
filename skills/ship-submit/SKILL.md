---
name: ship-submit
description: Recipe 7 of the strands-ship power. Prepare the Workshop to Ship submission - FACTS.md from measured numbers, the repo README, the Builder Center article draft (one heading per judging criterion), and the PASS/FAIL/HUMAN submission check. Use when the user says "submission check", "ship it", "write the article", "write the README", or "am I ready to submit".
---
# Recipe 7: submit

Rules: `.kiro/steering/hackathon-rules.md`. Re-read them first.

## Step 1: the check
`ss ship` writes `results/FACTS.md` and `SUBMISSION.md`. Fix every FAIL, then run it again. Typical FAILs: gate not passed (recipe 5), no FAILURES.md entry, sample data not replaced, no README or LICENSE, a key in git history.

## Step 2: README.md (with the user)
What the agent does and for whom; the architecture in five lines from DESIGN.md (what code owns, which Strands blocks, which AWS services); how to run it (`pip install -r requirements.txt`, AWS credentials in their own terminal, `python -m agent.app "..."`); the results table copied from `results/MEASURE.md`; honest limits (labelled scenarios, not field outcomes; sample data if any; who reviewed the Tamil). Add an OSI licence (Apache-2.0 or MIT; ask which). `ship_kit/` is Apache-2.0 and may ship in their repo.

## Step 3: ARTICLE.md (Builder Center), in the user's voice
One heading per judging quarter, so a reader and the Gate-1 AI scorer find each:
1. **Social impact**: the people, the place, the story from IDEA.md, and the measured numbers (from FACTS.md, quoted exactly).
2. **Technical execution**: the Strands blocks from DESIGN.md and what each does, Strands Evals, the baseline comparison.
3. **What we learned**: at least one failure from FAILURES.md, with before/after numbers.
4. **Originality**: what goes beyond the workshop's swarm (DESIGN.md's "beyond the workshop" line) and the AWS services used and why.
Ask the user for the story parts (why they built it, who they talked to, what surprised them); do not invent them. Every number comes from FACTS.md. Include the video link and the repo link.

## Step 4: what only the user can do (the HUMAN rows)
Complete the Builder Center workshop inside the window; make the repo public inside the window (28 Oct - 4 Nov 2026); upload the video publicly; publish the article on Builder Center; submit before **4 Nov 2026 11:59 PM PST (5 Nov 1:29 PM IST)**. Before the repo goes public: `git log -p | grep -E "AKIA|BEGIN .*PRIVATE KEY"` must print nothing (`ss ship` checks this too).
