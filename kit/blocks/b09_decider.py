"""09 Strands Decider (Strands Labs): a small decision model that answers yes/no, choice or score
questions with a calibrated confidence and no generated text.

Use it when: the agent must make one decision fast and you want a number to branch on, not a paragraph
(is this a crisis? which helpline? how urgent, 0-1?). Act only above a confidence you measured.
Two ways to run it:
- Hosted by AWS User Group Madurai (no install, 2,000 free decisions a month): get a team key on
  https://www.awsugmdu.in and set DECIDER_URL=https://da25tnxy06gjk.cloudfront.net and DECIDER_API_KEY.
- Local: `pip install strands-decider` (needs PyTorch and about 5 GB of RAM); see the Decider Cookbook power.
Run: ss block decider
"""
import json
import os
import urllib.request

from strands import Agent, tool

from _common import model, say

URL, KEY = os.environ.get("DECIDER_URL", "https://da25tnxy06gjk.cloudfront.net"), os.environ.get("DECIDER_API_KEY")


def decide(state: str, questions: dict) -> dict:
    req = urllib.request.Request(URL + "/v1/decide", data=json.dumps({"state": state, "questions": questions}).encode(),
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["answers"]


@tool
def urgency(message: str) -> dict:
    """Ask Strands Decider how urgent a message is and which help line fits. Returns numbers to act on.

    Args:
        message: what the person wrote
    """
    # Numbers: 108 ambulance (TN Health Systems Project), Tele MANAS 14416 (MoHFW), Kisan Call Centre 1800-180-1551 (MANAGE).
    a = decide(message, {
        "emergency": {"type": "noul", "instructions": "Is someone in immediate danger to life or health?"},
        "line": {"type": "choice", "instructions": "Which help line fits best?",
                 "criteria": {"ambulance_108": "medical emergency", "tele_manas_14416": "mental health distress",
                              "kisan_1800_180_1551": "farming advice", "none": "no help line needed"}},
    })
    return {"p_emergency": a["emergency"]["noul"], "line": a["line"]["choice"], "confidence": a["line"].get("confidence")}


if not KEY:
    say("decider", "DECIDER_API_KEY not set: get a free team key on https://www.awsugmdu.in, then run again")
    raise SystemExit(0)
msg = "My father fainted in the field and is not answering me."
d = urgency._tool_func(msg) if hasattr(urgency, "_tool_func") else urgency(msg)
say("decider", f"p_emergency {d['p_emergency']:.2f}, line {d['line']} (confidence {d['confidence']})")
if d["p_emergency"] >= 0.8:  # pick this threshold from YOUR labelled cases, never by feel
    say("safety", "ACT: send the fixed 108 instruction, no LLM text")
else:
    agent = Agent(model=model(), tools=[urgency], callback_handler=None, system_prompt="Help the user calmly.")
    say("plan", str(agent(msg)).strip()[:200])
