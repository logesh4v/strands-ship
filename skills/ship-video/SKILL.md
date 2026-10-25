---
name: ship-video
description: Recipe 6 of the strands-ship power. Record the under-3-minute demo video from a live run of the agent - a headless browser films a studio page while the real commands run, evidence lines become badges, and the measured results close it. Use when the user says "record the video", "make the demo video", or "demo".
---
# Recipe 6: record the video

## Step 1: the scenes
`video.json` in the project root holds a title, subtitle, tags, closing line and 3-4 scenes (`title`, `caption`, `input` shown on screen, `command` really run, optional `after` caption and `hold_s`). Write the scenes from IDEA.md: one normal request, one where a check or rule changes the answer (critic REVISE, Deny, Decider below threshold), and one red flag the hook stops. The HeatSafe example's `video.json` shows a finished spec. If a scene's output is not what the user wants to show, change the scene, never the result.

## Step 2: record
`ss video`. It runs each command live, streams the output into the log panel, turns `[risk] [safety] [critic] [code] [lang] [plan]` lines (and `[guard] [decider] [tool] [graph] [swarm] [shell]` from blocks) into badges, adds a "Measured, not claimed" card from `results/measure.json` (run recipe 5 first), and writes `results/demo.mp4` (or `.webm` without ffmpeg) plus `results/video_run.json`. Silent, with captions. It prints the length; it must be under 180 s (the HeatSafe example's three scenes record in about 57 s).

## Step 3: check it with the user
Open the file and watch it together. Check: every scene exited 0, Tamil renders (not boxes), no AWS account number, key or personal data on screen, and any sample data is labelled as a sample.

## Step 4: what only the user does
Upload it publicly (YouTube, Vimeo or similar) before submitting, with no copyrighted music. A voice-over is optional; if they record one, keep the live video unchanged underneath.

Next: say "submission check".
