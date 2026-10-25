"""Tools the planner can call, plus the plain helpers app.py uses. All read-only."""
from __future__ import annotations

import json
import math
import os
import re
import urllib.parse
import urllib.request
from functools import lru_cache
from pathlib import Path

from strands import tool

from . import heat

DATA = Path(__file__).parent / "data"
TAMIL = re.compile(r"[\u0B80-\u0BFF]")


@lru_cache(maxsize=1)
def guidance() -> dict:
    return json.loads((DATA / "guidance.json").read_text(encoding="utf-8"))


def guidance_ids() -> set[str]:
    return {g["id"] for g in guidance()["items"]}


@lru_cache(maxsize=1)
def places() -> dict:
    return json.loads((DATA / "places.geojson").read_text(encoding="utf-8"))


def language_of(text: str) -> str:
    return "ta" if TAMIL.search(text or "") else "en"


def has_tamil(text: str) -> bool:
    return bool(TAMIL.search(text or ""))


def _km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin(math.radians(lat2 - lat1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def nearest(lat: float, lon: float, k: int = 2) -> list[str]:
    out = []
    for f in places()["features"]:
        lon2, lat2 = f["geometry"]["coordinates"]
        p = f["properties"]
        checked = f"checked {p['verified_on']}" if p.get("verified_on") else "NOT checked yet"
        d = _km(lat, lon, lat2, lon2)
        out.append((d, f"{p['name']}, {d:.1f} km ({checked}; confirm locally)"))
    return [s for _, s in sorted(out)[:k]]


def forecast(lat: float, lon: float) -> tuple[float, float]:
    """Current temperature (C) and relative humidity (%) from Open-Meteo (free, no key)."""
    q = urllib.parse.urlencode({"latitude": lat, "longitude": lon, "current": "temperature_2m,relative_humidity_2m"})
    with urllib.request.urlopen(f"https://api.open-meteo.com/v1/forecast?{q}", timeout=15) as r:
        cur = json.load(r)["current"]
    return float(cur["temperature_2m"]), float(cur["relative_humidity_2m"])


def translate_to_tamil(texts: list[str]) -> list[str]:
    """Amazon Translate fallback when the model answered a Tamil speaker in English."""
    import boto3
    c = boto3.client("translate", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    return [c.translate_text(Text=t, SourceLanguageCode="en", TargetLanguageCode="ta")["TranslatedText"] if t and not has_tamil(t) else t
            for t in texts]


@tool
def heat_risk(temp_c: float, relative_humidity: float, intensity: str = "moderate", full_sun: bool = False) -> dict:
    """Compute the heat index and the risk level for this shift. Always call this first.

    The level is fixed by code (US NWS heat index + OSHA risk bands). Copy risk_level and
    heat_index_c into the plan exactly; never change them.

    Args:
        temp_c: air temperature in Celsius
        relative_humidity: relative humidity in percent
        intensity: light, moderate or heavy work
        full_sun: true if the worker is in direct sun most of the shift
    """
    r = heat.assess(temp_c, relative_humidity, intensity, full_sun)
    a = heat.ACTIONS[r.level]
    return {**r.as_dict(), "required_hydration_en": a["hydration"]["en"], "required_work_rest_en": a["work_rest"]["en"],
            "cite": a["guidance"] + (["G-HI-BUMP"] if r.bumped else [])}


@tool
def lookup_guidance(topic: str) -> list[dict]:
    """Find curated, dated heat-safety guidance to cite. Returns items with id and text.

    Args:
        topic: words to match, e.g. "water", "warning signs", "cramps", "buddy", "work rest"
    """
    words = [w for w in re.findall(r"[a-z0-9]+", topic.lower()) if len(w) > 2]
    items = guidance()["items"]
    hits = [g for g in items if any(w in (g["id"] + " " + g["text"]).lower() for w in words)]
    return [{"id": g["id"], "text": g["text"]} for g in (hits or items)[:6]]


@tool
def nearest_water_points(lat: float, lon: float) -> list[str]:
    """List the two nearest water/shade points from the curated, dated list. Never claim they are open now.

    Args:
        lat: latitude of the worksite
        lon: longitude of the worksite
    """
    return nearest(lat, lon)
