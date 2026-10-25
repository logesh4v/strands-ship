---
name: ship-pick-idea
description: Recipe 1 of the strands-ship power. Recommend which social-good agent to build for the Strands SDK Workshop to Ship hackathon (education, health or climate resilience), scored on the hackathon rubric, and help the user make it their own. Use when the user says "pick my idea", "what should I build", "which idea", "suggest a direction", or "help me choose".
---
# Recipe 1: pick the idea

Read `references/council.md` (how the recommendation was made) and `~/.strands-ship/kit/paths/paths.json` (the four paths). Do not invent a fifth path's numbers; a user's own idea is welcome, scored the same way.

## Step 1: lead with the recommendation
Say it plainly, in this order:
1. **Build HeatSafe Shift** (climate resilience): a Tamil/English agent that turns the forecast, the job and any symptoms into a safe plan for one outdoor shift. Code owns the heat thresholds and the 108 emergency call; a Strands graph (planner, critic, retry) writes and checks the plan.
2. Why, in one line per rubric quarter: social impact (outdoor workers in the hottest hours, measurable safety numbers), technical execution (graph + hook + structured output + evals, already working in the kit), communication (a 3-scene live video and a results table the kit writes), originality (goes well beyond the workshop's swarm; deterministic safety split; Tamil).
3. The honest risk: judges may ask whether safer advice changes real behaviour. A small consented field test helps but is optional; never claim outcomes that were not measured.

## Step 2: the alternatives, ranked
Show the other three from `paths.json` as a short table: name, one-line pitch, why it ranks where it does. Padippu is the most feasible but the hackathon page already lists it as an example; Marundhu needs clinical validation; FloodReady needs checked local shelter data.

## Step 3: make it theirs (ask these, one message)
1. Which worker group do you (or a partner, NGO or college) actually reach? (construction, road, sanitation, farm, kiln, salt pan, delivery, street vending)
2. Which district, and can someone visit the water/shade points you will list?
3. Tamil, English, or both?
4. Is anyone else from your college or user group building HeatSafe? If yes, pick a different worker group and district: judges see every entry, and identical agents cost every team originality points.
5. Can you run a small consented test with 5-10 real workers? (optional)

## Step 4: record the decision
Write `IDEA.md` in the project: path, worker group, district, languages, the five answers, and the rubric reasoning above. If they chose another path, re-run `~/.strands-ship/bin/ss init --path <name>` in a fresh folder (init never overwrites) and point them to `.kiro/steering/ship-path.md`.

Next: say "build the agent".
