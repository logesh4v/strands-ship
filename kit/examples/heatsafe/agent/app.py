"""HeatSafe Shift: a Tamil/English heat-safety plan for one outdoor shift.

    python -m agent.app "I lay bricks on a roof today, 2pm to 6pm" --temp 37 --rh 55 --intensity heavy --sun
    python -m agent.app "இன்று சாலை வேலை, தலைசுற்றுகிறது" --lat 9.92 --lon 78.12      (weather from Open-Meteo)

Who decides what:
- code: heat index and risk level (agent/heat.py), red-flag escalation (agent/safety.py, a Strands hook
  that cancels every graph node), water amount, the fixed work/rest steps for the level.
- Strands graph: a planner agent (tools + ShiftPlan structured output) writes the plan for this job;
  a critic agent checks it against the rules; a conditional edge sends it back to the planner once.
- Amazon Bedrock runs both agents; Amazon Translate answers in Tamil if the model slipped into English.
Lines starting with [risk] [safety] [critic] [lang] [plan] are the evidence the video and measure read.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time

from strands import Agent
from strands.models import BedrockModel
from strands.multiagent import GraphBuilder

from . import heat, safety, tools
from .plan import Critique, ShiftPlan

MODEL_ID = os.environ.get("SHIP_MODEL", "us.amazon.nova-2-lite-v1:0")
REGION = os.environ.get("AWS_REGION", "us-east-1")
MAX_PLANNER_PASSES = 2
logging.getLogger("strands").setLevel(logging.CRITICAL)  # a cancelled node is expected, not an error

PLANNER = """You write a heat-safety plan for ONE outdoor worker's shift. The worker may have low literacy.
Rules:
1. Call heat_risk first with the numbers in the message. Copy risk_level and heat_index_c exactly.
2. Write every text field in the worker's language ({lang}: en = English, ta = Tamil script). Short, plain sentences.
3. work_rest: two or three steps that fit THIS job and THIS time of day. Hydration must follow the tool's required_hydration.
   Never invent numbers (minutes of work or rest, litres, temperatures) that the tools did not give you.
4. warning_signs: list the signs that mean stop now (code replaces this list with the fixed NIOSH list).
5. escalation: when to stop work and when to call 108.
6. If a lat/lon is given, call nearest_water_points and copy what it returns. Never say a place is open now.
7. citations: only ids returned by heat_risk or lookup_guidance.
8. Never suggest salt tablets, alcohol or energy drinks, and never tell anyone to keep working through symptoms.
If a critic lists problems, fix every one of them and return the whole corrected plan."""

CRITIC = """You check a heat-safety plan. Reply ok=false with one line per problem if ANY rule is broken:
- risk_level or heat_index_c differs from the heat_risk facts in the task;
- a text field is not in the requested language ({lang}: en = English, ta = Tamil script);
- warning_signs or escalation is empty, or escalation does not say when to call 108;
- work_rest says nothing specific to the job or time of day in the task;
- the task reports symptoms and the plan still tells the worker to keep working;
- any advice to take salt tablets, alcohol or energy drinks;
- a number (minutes, litres, degrees) that is not in the heat_risk facts or the required steps.
Citations are checked by code, not by you. Name the exact field and words for each problem.
Otherwise ok=true with no problems. Do not rewrite the plan."""


def _model() -> BedrockModel:
    return BedrockModel(model_id=MODEL_ID, region_name=REGION, temperature=0.2)


def _task(case: dict, risk: heat.Risk, lang: str, tier: str | None) -> str:
    where = f"\nWorksite lat {case['lat']}, lon {case['lon']}." if case.get("lat") is not None else ""
    care = ("\nThe worker reports heat exhaustion warning signs: the plan must tell them to stop work now and get checked."
            " work_rest must be stop-and-recover steps, not work steps."
            if tier == "care" else "")
    return (f"Worker message ({lang}): {case['text']}\nJob: {case.get('job', 'outdoor work')}."
            f" Work intensity: {case.get('intensity', 'moderate')}. Direct sun all shift: {bool(case.get('full_sun'))}."
            f"\nWeather: {risk.temp_c} C air temperature, {risk.rh}% relative humidity.{where}"
            f"\nheat_risk facts (fixed): risk_level={risk.level}, heat_index_c={risk.heat_index_c}.{care}")


def build_graph(lang: str, gate: safety.RedFlagGate):
    planner = Agent(model=_model(), name="planner", system_prompt=PLANNER.format(lang=lang),
                    tools=[tools.heat_risk, tools.lookup_guidance, tools.nearest_water_points],
                    structured_output_model=ShiftPlan, callback_handler=None)
    critic = Agent(model=_model(), name="critic", system_prompt=CRITIC.format(lang=lang),
                   structured_output_model=Critique, callback_handler=None)

    seen: set[int] = set()

    def needs_revision(state) -> bool:  # the graph may evaluate an edge more than once per pass
        r = state.results.get("critic")
        verdict = getattr(r.result, "structured_output", None) if r else None
        passes = sum(1 for n in state.execution_order if n.node_id == "planner")
        if verdict is not None and passes not in seen:
            seen.add(passes)
            print(f"[critic] pass {passes}: " + ("PASS" if verdict.ok else "REVISE - " + "; ".join(verdict.problems)[:220]), flush=True)
        return bool(verdict is not None and not verdict.ok and passes < MAX_PLANNER_PASSES)

    b = GraphBuilder()
    b.add_node(planner, "planner")
    b.add_node(critic, "critic")
    b.add_edge("planner", "critic")
    b.add_edge("critic", "planner", condition=needs_revision)
    b.set_entry_point("planner")
    b.set_max_node_executions(MAX_PLANNER_PASSES * 2)
    b.reset_on_revisit(True)
    b.set_hook_providers([gate])
    return b.build()


def _emergency_plan(lang: str, risk: heat.Risk, signs: list[str], case: dict) -> ShiftPlan:
    stop = {"en": ["Stop all work now.", "Do not leave the person alone."],
            "ta": ["எல்லா வேலையையும் இப்போதே நிறுத்துங்கள்.", "அவரை தனியாக விடாதீர்கள்."]}[lang]
    cool = {"en": "Cool the person with water on the skin, wet cloths and fanning while you wait for 108.",
            "ta": "108 வரும் வரை தோலில் தண்ணீர் தெளித்து, ஈரத் துணி வைத்து, விசிறி குளிர்விக்கவும்."}[lang]
    signs_txt = {"en": ["Confusion or slurred speech", "Fainting or not waking", "Seizure", "Hot, dry skin"],
                 "ta": ["குழப்பம் அல்லது குழறிய பேச்சு", "மயக்கம் அல்லது எழுந்திருக்காமை", "வலிப்பு", "சூடான, வறண்ட தோல்"]}[lang]
    pts = tools.nearest(case["lat"], case["lon"]) if case.get("lat") is not None else []
    return ShiftPlan(language=lang, risk_level=risk.level, heat_index_c=risk.heat_index_c,
                     summary=safety.TEXT["emergency"][lang], work_rest=stop, hydration=cool, warning_signs=signs_txt,
                     escalation=safety.TEXT["emergency"][lang], water_points=pts,
                     citations=["G-SIGNS-STROKE", "G-FIRSTAID-STROKE", "G-108"])


def _enforce(plan: ShiftPlan, risk: heat.Risk, lang: str, tier: str | None, critic_ok: bool) -> tuple[ShiftPlan, list[str]]:
    """Put back every field the code owns. Returns the list of fields it had to correct.

    If the critic still rejected the plan after the last pass, fail closed: the planner's own
    summary and work/rest lines are dropped and only code-owned text ships.
    """
    fixed = []
    a = heat.ACTIONS[risk.level]
    if not critic_ok:
        plan.summary, plan.work_rest = a["summary"][lang], []
        fixed.append("critic never passed: planner text dropped, fixed text used")
    if plan.risk_level != risk.level or abs(plan.heat_index_c - risk.heat_index_c) > 0.05:
        fixed.append(f"risk {plan.risk_level}/{plan.heat_index_c} -> {risk.level}/{risk.heat_index_c}")
    plan.risk_level, plan.heat_index_c, plan.language = risk.level, risk.heat_index_c, lang
    plan.hydration = a["hydration"][lang]
    plan.warning_signs = safety.WARNING_SIGNS[lang]
    own = [s for s in plan.work_rest if s not in a["work_rest"][lang]][:2]
    plan.work_rest = safety.CARE_STEPS[lang] if tier == "care" else a["work_rest"][lang] + own
    if tier == "care":
        plan.escalation = safety.TEXT["care"][lang]
        plan.summary = safety.TEXT["care"][lang]
        plan.citations += ["G-SIGNS-EXHAUSTION", "G-FIRSTAID-EXHAUSTION"]
    elif safety.NUMBER not in plan.escalation:
        plan.escalation = (plan.escalation + " " if plan.escalation else "") + {
            "en": "If anyone is confused, faints or stops sweating, call 108 now.",
            "ta": "யாருக்காவது குழப்பம், மயக்கம் அல்லது வியர்வை நின்றால் உடனே 108 அழையுங்கள்."}[lang]
        fixed.append("escalation: added 108")
    unknown = [c for c in plan.citations if c not in tools.guidance_ids()]
    if unknown:
        fixed.append("dropped unknown citations " + ", ".join(unknown))
    plan.citations = list(dict.fromkeys([c for c in plan.citations if c not in unknown] + a["guidance"]
                                        + ["G-SIGNS-EXHAUSTION", "G-SIGNS-STROKE"] + (["G-HI-BUMP"] if risk.bumped else [])))
    return plan, fixed


def run(case: dict) -> dict:
    """One shift plan for one case. Returns {"plan": ShiftPlan dict, "meta": evidence}."""
    t0 = time.time()
    lang = case.get("lang") or tools.language_of(case["text"])
    if case.get("temp_c") is None:
        case = {**case, **dict(zip(("temp_c", "rh"), tools.forecast(case["lat"], case["lon"])))}
        print(f"[weather] Open-Meteo now: {case['temp_c']} C, RH {case['rh']}%", flush=True)
    risk = heat.assess(case["temp_c"], case["rh"], case.get("intensity", "moderate"), case.get("full_sun", False))
    print(f"[risk] {risk.reason} -> {risk.level}", flush=True)
    tier, signs = safety.check(case["text"])
    meta = {"tier": tier, "signs": signs, "risk": risk.as_dict(), "passes": 0, "critic_ok": None, "fixed": [], "translated": False}

    if tier == "care":
        print(f"[safety] warning signs ({', '.join(signs)}) -> STOP WORK, get checked", flush=True)
    gate = safety.RedFlagGate()
    graph = build_graph(lang, gate)
    try:
        res = graph(_task(case, risk, lang, tier), invocation_state={"user_text": case["text"]})
    except RuntimeError:
        if not gate.tripped:
            raise
        res = None
    if gate.tripped:
        print(f"[safety] RED FLAG ({', '.join(gate.tripped)}) -> EMERGENCY 108, agents cancelled", flush=True)
        plan = _emergency_plan(lang, risk, gate.tripped, case)
        meta.update(path="emergency")
    else:
        plan = res.results["planner"].result.structured_output
        if plan is None:
            raise RuntimeError("planner returned no structured plan")
        crit = res.results.get("critic")
        verdict = getattr(crit.result, "structured_output", None) if crit else None
        meta.update(path="agent", passes=sum(1 for n in res.execution_order if n.node_id == "planner"),
                    critic_ok=bool(verdict and verdict.ok), critic_problems=list(verdict.problems) if verdict else [])
        plan, meta["fixed"] = _enforce(plan, risk, lang, tier, meta["critic_ok"])
        if meta["fixed"]:
            print("[code] corrected: " + "; ".join(meta["fixed"]), flush=True)
    if lang == "ta" and not tools.has_tamil(plan.summary + " ".join(plan.work_rest) + " ".join(plan.warning_signs)):
        plan.summary, plan.escalation = tools.translate_to_tamil([plan.summary, plan.escalation])
        plan.work_rest = tools.translate_to_tamil(plan.work_rest)
        plan.warning_signs = tools.translate_to_tamil(plan.warning_signs)
        meta["translated"] = True
        print("[lang] model answered in English -> Amazon Translate to Tamil", flush=True)
    meta["latency_ms"] = int((time.time() - t0) * 1000)
    print(f"[plan] {plan.risk_level} | heat index {plan.heat_index_c} C | {meta.get('path')} | {meta['latency_ms']} ms", flush=True)
    return {"plan": plan.model_dump(), "meta": meta}


def _print_plan(p: dict) -> None:
    print("\n" + p["summary"])
    for k in ("work_rest", "warning_signs", "water_points"):
        for s in p[k]:
            print(f"  - {s}")
    print("Water: " + p["hydration"])
    print("If it gets worse: " + p["escalation"])
    print("Sources: " + ", ".join(p["citations"]))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m agent.app", description=__doc__.splitlines()[0])
    ap.add_argument("text")
    ap.add_argument("--temp", type=float, dest="temp_c")
    ap.add_argument("--rh", type=float)
    ap.add_argument("--intensity", choices=["light", "moderate", "heavy"], default="moderate")
    ap.add_argument("--sun", action="store_true", dest="full_sun", help="direct sun most of the shift")
    ap.add_argument("--job", default="outdoor work")
    ap.add_argument("--lat", type=float)
    ap.add_argument("--lon", type=float)
    ap.add_argument("--json", action="store_true")
    a = vars(ap.parse_args(argv))
    if a["temp_c"] is None and (a["lat"] is None or a["lon"] is None):
        ap.error("give --temp and --rh, or --lat and --lon for live weather")
    if a["temp_c"] is not None and a["rh"] is None:
        ap.error("--temp needs --rh")
    as_json = a.pop("json")
    out = run(a)
    print(json.dumps(out, ensure_ascii=False, indent=2) if as_json else "", end="")
    if not as_json:
        _print_plan(out["plan"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
