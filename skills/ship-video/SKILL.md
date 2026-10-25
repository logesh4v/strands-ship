---
name: ship-video
description: Recipe 5 of the strands-ship power. Record the under-3-minute demo video from a live run of the agent - a headless browser films a studio page while the real commands run, evidence lines become badges, and the measured results close it. Use when the user says "record the video", "make the demo video", or "demo".
---
# Recipe 5: record the video

## Step 1: the scenes
`video.json` in the project root holds a title, subtitle, tags, closing line and 3-4 scenes (`title`, `caption`, `input` shown on screen, `command` really run, optional `after` caption and `hold_s`). The shipped spec has three: a roof job (plan, EXTREME risk), a Tamil road worker with dizziness (stop work, in Tamil), and a confused coworker (hook cancels the agents, 108). Change the inputs to the user's worker group and district. Keep one normal plan, one warning-sign case and one emergency. If a scene's output is not what the user wants to show, change the scene, never the result.

## Step 2: record
`ss video`. It runs each command live, streams the output into the log panel, turns `[risk] [safety] [critic] [code] [lang] [plan]` lines into badges, adds a "Measured, not claimed" card from `results/measure.json` (run recipe 4 first), and writes `results/demo.mp4` (or `.webm` without ffmpeg) plus `results/video_run.json`. Silent, with captions. It prints the length; it must be under 180 s (about 100 s with three scenes on Nova 2 Lite).

## Step 3: check it with the user
Open the file and watch it together. Check: every scene exited 0, the Tamil renders (not boxes), no AWS account number, key or personal data on screen, sample water points are labelled "NOT checked" or replaced.

## Step 4: what only the user does
Upload it publicly (YouTube, Vimeo or similar) before submitting, with no copyrighted music. A voice-over is optional; if they record one, keep the live video unchanged underneath.

Next: say "submission check".
