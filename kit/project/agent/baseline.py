"""The baseline the rubric asks you to beat: ONE agent, ONE prompt, the same model and the same guidance.

No tools, no graph, no critic, no red-flag hook, no code-owned fields. It gets the curated guidance
pasted into its prompt so the comparison isolates the architecture, not access to facts.
"""
from __future__ import annotations

import time

from strands import Agent

from . import tools
from .app import _model
from .plan import ShiftPlan

PROMPT = """You are a heat-safety assistant for outdoor workers. Write a safe plan for this worker's shift, in the
worker's language (Tamil script if they wrote Tamil). Work out the heat index and risk level yourself
(levels: LOWER, MODERATE, HIGH, EXTREME, using the US NWS heat index and the OSHA bands: below 91 F lower,
91-103 F moderate, 103-115 F high, above 115 F extreme; then one level higher, at most EXTREME, for heavy
work or a full shift in direct sun). If the worker has
emergency signs, tell them to call 108. Cite only these guidance ids:
{guidance}"""


def run(case: dict) -> dict:
    t0 = time.time()
    lines = "\n".join(f"{g['id']}: {g['text']}" for g in tools.guidance()["items"])
    agent = Agent(model=_model(), system_prompt=PROMPT.format(guidance=lines), structured_output_model=ShiftPlan,
                  callback_handler=None)
    lang = case.get("lang") or tools.language_of(case["text"])
    msg = (f"Answer in {'Tamil (Tamil script)' if lang == 'ta' else 'English'}.\nWorker message ({lang}): {case['text']}\nJob: {case.get('job', 'outdoor work')}. Intensity: {case.get('intensity', 'moderate')}."
           f" Direct sun all shift: {bool(case.get('full_sun'))}. Weather: {case['temp_c']} C, {case['rh']}% relative humidity.")
    plan = agent(msg).structured_output
    if plan is None:  # one retry, the same allowance the agent's graph gets from its critic loop
        plan = agent(msg).structured_output
    if plan is None:
        raise RuntimeError("baseline returned no structured plan")
    return {"plan": plan.model_dump(), "meta": {"path": "baseline", "latency_ms": int((time.time() - t0) * 1000)}}
