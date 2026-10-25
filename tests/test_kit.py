"""Offline tests: no AWS calls. Run: python -m pytest -q tests (from the power folder, Strands installed)."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kit" / "project"))
sys.path.insert(0, str(ROOT / "kit"))

from agent import heat, safety, score, tools  # noqa: E402
from ship_kit import cases as casesmod  # noqa: E402


@pytest.mark.parametrize("t,rh,hi_f", [(90, 40, 91), (90, 45, 93), (96, 55, 112), (100, 40, 109), (86, 90, 105), (92, 70, 112)])
def test_heat_index_matches_nws_chart(t, rh, hi_f):
    # Values read off the NWS heat index chart (degrees F); allow 1.5 F for chart rounding.
    got_f = heat.heat_index_c((t - 32) * 5 / 9, rh) * 9 / 5 + 32
    assert abs(got_f - hi_f) <= 1.5


@pytest.mark.parametrize("hi_c,band", [(30, "LOWER"), (32.7, "LOWER"), (33, "MODERATE"), (39.3, "MODERATE"),
                                       (39.5, "HIGH"), (46.1, "HIGH"), (46.3, "EXTREME")])
def test_osha_bands(hi_c, band):
    assert heat.band(hi_c) == band


def test_bump_one_level_and_cap():
    assert heat.assess(31, 62, "moderate").level == "MODERATE"
    assert heat.assess(31, 62, "heavy").level == "HIGH"
    assert heat.assess(31, 62, "heavy", True).level == "HIGH"       # one level, not two
    assert heat.assess(40, 60, "heavy", True).level == "EXTREME"    # capped


def test_every_level_has_both_languages_and_valid_citations():
    ids = tools.guidance_ids()
    for lvl, a in heat.ACTIONS.items():
        assert a["hydration"]["en"] and tools.has_tamil(a["hydration"]["ta"])
        assert len(a["work_rest"]["en"]) == len(a["work_rest"]["ta"])
        assert set(a["guidance"]) <= ids, lvl


@pytest.mark.parametrize("text,tier", [
    ("My coworker is confused and talking nonsense", "emergency"),
    ("he had a seizure near the drain", "emergency"),
    ("Rider stopped sweating, skin is hot and dry", "emergency"),
    ("my urine is dark like cola", "emergency"),
    ("என் நண்பருக்கு வலிப்பு வருகிறது", "emergency"),
    ("குழப்பமாகப் பேசுகிறார்", "emergency"),
    ("மயங்கி விழுந்து எழுந்திருக்கவில்லை", "emergency"),
    ("I feel dizzy and have a headache", "care"),
    ("I threw up twice", "care"),
    ("எனக்கு தலைசுற்றுகிறது", "care"),
    ("No dizziness, no headache, just tired legs", None),
    ("It is 105 F outside and I am fine", None),
    ("Laying bricks on a roof in Madurai", None),
])
def test_red_flag_tiers(text, tier):
    assert safety.check(text)[0] == tier


def test_emergency_text_has_number_in_both_languages():
    for lang in ("en", "ta"):
        assert safety.NUMBER in safety.TEXT["emergency"][lang]
        assert safety.NUMBER in safety.TEXT["care"][lang]


def _plan(**kw):
    p = {"language": "en", "risk_level": "HIGH", "heat_index_c": 40.0, "summary": "Take care in the heat.",
         "work_rest": ["Rest in shade."], "hydration": "Drink water.", "warning_signs": ["dizziness"],
         "escalation": "Call 108 if confused.", "water_points": [], "citations": ["G-HI-HIGH"]}
    p.update(kw)
    return {"plan": p, "meta": {"latency_ms": 10}}


def _case(**kw):
    c = {"id": "x", "lang": "en", "job": "road", "text": "road work", "expected": {"risk_level": "HIGH", "escalation": "none"}}
    c.update(kw)
    return c


def test_score_flags_under_call_banned_advice_and_missed_emergency():
    assert score.score(_case(), _plan())["unsafe"] == []
    assert "risk under-called" in score.score(_case(), _plan(risk_level="MODERATE"))["unsafe"][0]
    assert score.score(_case(), _plan(summary="Take salt tablets."))["unsafe"]
    assert score.score(_case(), _plan(summary="Avoid salt tablets."))["unsafe"] == []
    em = _case(expected={"risk_level": "HIGH", "escalation": "emergency"})
    assert score.score(em, _plan(escalation="Rest.", summary="Rest."))["unsafe"] == ["emergency not escalated to 108"]


def test_score_tamil_language_and_madurai_is_not_alcohol():
    ta = _case(lang="ta", text="சாலை வேலை")
    assert score.score(ta, _plan())["complete"] == 0.0               # English answer to a Tamil user
    ok = score.score(ta, _plan(summary="மதுரையில் நிழலில் ஓய்வு எடுங்கள்."))
    assert ok["complete"] == 1.0 and ok["unsafe"] == []


def test_seed_cases_meet_minimums_and_are_unsigned():
    cs = [json.loads(line) for line in (ROOT / "kit/project/cases.seed.jsonl").read_text(encoding="utf-8").splitlines() if line]
    r = casesmod.check(cs)
    assert not r["errors"] and not r["below_minimum"]
    assert r["counts"]["unsigned"] == len(cs)                        # the author never signs for the builder
    for c in cs:                                                     # labels agree with the gate's own tiers
        assert (safety.check(c["text"])[0] or "none") == c["expected"]["escalation"], c["id"]
        assert heat.assess(c["temp_c"], c["rh"], c["intensity"], c["full_sun"]).level == c["expected"]["risk_level"], c["id"]


def test_approve_refuses_empty_name():
    with pytest.raises(SystemExit):
        casesmod.approve([{"id": "a"}], " ")


def test_init_never_overwrites(tmp_path):
    env = {**os.environ, "PYTHONPATH": str(ROOT / "kit")}
    (tmp_path / "README.md").write_text("mine")
    r = subprocess.run([sys.executable, "-m", "ship_kit.cli", "init"], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "agent" / "app.py").exists() and (tmp_path / ".kiro" / "hooks" / "strands-ship.json").exists()
    (tmp_path / "agent" / "app.py").write_text("# edited")
    subprocess.run([sys.executable, "-m", "ship_kit.cli", "init"], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert (tmp_path / "agent" / "app.py").read_text() == "# edited"
    assert (tmp_path / "README.md").read_text() == "mine"


def test_manifests():
    plugin = json.loads((ROOT / "plugin.json").read_text())
    assert plugin["name"] == "strands-ship" and plugin["author"]["name"]
    mcp = json.loads((ROOT / "mcp.json").read_text())["mcpServers"]
    assert mcp["strands-agents"]["command"] == "uvx" and mcp["aws-knowledge-mcp-server"]["url"].startswith("https://")
    for skill in (ROOT / "skills").glob("*/SKILL.md"):
        head = skill.read_text().split("---")[1]
        assert f"name: {skill.parent.name}" in head and "description:" in head


def test_enforce_owns_fields_and_fails_closed():
    from agent.app import _enforce
    from agent.plan import ShiftPlan
    risk = heat.assess(37, 50, "heavy", True)
    p = ShiftPlan(language="en", risk_level="LOWER", heat_index_c=1.0, summary="Keep working, it is fine.",
                  work_rest=["Work 60 minutes, rest 5."], hydration="Some water.", warning_signs=["x"],
                  escalation="Rest.", water_points=[], citations=["G-NOT-REAL"])
    out, fixed = _enforce(p, risk, "en", None, critic_ok=False)
    assert out.risk_level == "EXTREME" and out.heat_index_c == risk.heat_index_c
    assert out.summary == heat.ACTIONS["EXTREME"]["summary"]["en"]
    assert out.work_rest == heat.ACTIONS["EXTREME"]["work_rest"]["en"]       # planner lines dropped
    assert out.warning_signs == safety.WARNING_SIGNS["en"] and "108" in out.escalation
    assert "G-NOT-REAL" not in out.citations and any("critic never passed" in f for f in fixed)
