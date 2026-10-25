"""Deterministic heat risk. The model never computes or overrides anything in this file.

Heat index: US National Weather Service (Rothfusz regression with NWS adjustments),
https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
Risk bands: OSHA "Using the Heat Index: A Guide for Employers":
  < 91 F lower (caution) | 91-103 F moderate | 103-115 F high | > 115 F very high to extreme.
Kit rule (conservative): heavy work or a full shift in direct sun moves the band up one level.
OSHA's guide says those workers need "additional precautions" at every band; one level is
this kit's reading of that note, not an OSHA number. Change it only with a cited source.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass

LEVELS = ["LOWER", "MODERATE", "HIGH", "EXTREME"]


def heat_index_c(temp_c: float, rh: float) -> float:
    """NWS heat index in Celsius from air temperature (C) and relative humidity (%)."""
    t = temp_c * 9 / 5 + 32
    simple = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + rh * 0.094)
    hi = (simple + t) / 2
    if hi >= 80:
        hi = (-42.379 + 2.04901523 * t + 10.14333127 * rh - 0.22475541 * t * rh
              - 0.00683783 * t * t - 0.05481717 * rh * rh + 0.00122874 * t * t * rh
              + 0.00085282 * t * rh * rh - 0.00000199 * t * t * rh * rh)
        if rh < 13 and 80 <= t <= 112:
            hi -= ((13 - rh) / 4) * math.sqrt((17 - abs(t - 95)) / 17)
        elif rh > 85 and 80 <= t <= 87:
            hi += ((rh - 85) / 10) * ((87 - t) / 5)
    return round((hi - 32) * 5 / 9, 1)


def band(hi_c: float) -> str:
    hi_f = hi_c * 9 / 5 + 32
    if hi_f < 91:
        return "LOWER"
    if hi_f < 103:
        return "MODERATE"
    if hi_f <= 115:
        return "HIGH"
    return "EXTREME"


@dataclass
class Risk:
    temp_c: float
    rh: float
    heat_index_c: float
    band: str
    level: str
    bumped: bool
    reason: str

    def as_dict(self) -> dict:
        return asdict(self)


def assess(temp_c: float, rh: float, intensity: str = "moderate", full_sun: bool = False) -> Risk:
    hi = heat_index_c(float(temp_c), float(rh))
    b = band(hi)
    bump = intensity == "heavy" or bool(full_sun)
    level = LEVELS[min(LEVELS.index(b) + (1 if bump else 0), 3)]
    why = []
    if intensity == "heavy":
        why.append("heavy work")
    if full_sun:
        why.append("full sun")
    reason = f"heat index {hi} C = {b}" + (f", +1 for {' and '.join(why)}" if bump and level != b else "")
    return Risk(float(temp_c), float(rh), hi, b, level, bump and level != b, reason)


# What each level requires. Text comes from the OSHA guide's summary table; ids point into
# data/guidance.json so every line in a plan is traceable to a source.
ACTIONS = {
    "LOWER": {
        "summary": {"en": "Lower heat risk today. Keep water close and use shade when you can.",
                    "ta": "இன்று வெப்ப அபாயம் குறைவு. குடிநீரை அருகில் வைத்து, முடிந்தவரை நிழலில் இருங்கள்."},
        "hydration": {"en": "Keep drinking water close by and drink at every break.",
                      "ta": "குடிநீரை அருகில் வைத்துக்கொண்டு ஒவ்வொரு இடைவேளையிலும் குடியுங்கள்."},
        "work_rest": {"en": ["Normal breaks. Use shade when you can.", "Wear a hat or cover your head in the sun."],
                      "ta": ["வழக்கமான இடைவேளைகள். முடிந்தவரை நிழலில் இருங்கள்.", "வெயிலில் தொப்பி அணியுங்கள் அல்லது தலையை மூடுங்கள்."]},
        "guidance": ["G-HI-LOWER", "G-WATER-NEAR"],
    },
    "MODERATE": {
        "summary": {"en": "Moderate heat risk. Drink water every 15 minutes and take breaks in the shade.",
                    "ta": "மிதமான வெப்ப அபாயம். 15 நிமிடத்திற்கு ஒருமுறை தண்ணீர் குடித்து, நிழலில் ஓய்வு எடுங்கள்."},
        "hydration": {"en": "Drink about one glass (250 ml) of water every 15 minutes, even if you are not thirsty.",
                      "ta": "தாகம் இல்லாவிட்டாலும் 15 நிமிடத்திற்கு ஒரு டம்ளர் (250 மி.லி) தண்ணீர் குடியுங்கள்."},
        "work_rest": {"en": ["Take frequent breaks in a cool, shaded place.", "Work with a buddy and watch each other for warning signs.",
                             "New or returning workers: start with a lighter load (acclimatize)."],
                      "ta": ["அடிக்கடி குளிர்ந்த நிழலில் ஓய்வு எடுங்கள்.", "ஒரு துணையுடன் வேலை செய்து, ஒருவரை ஒருவர் கவனியுங்கள்.",
                             "புதிதாக வந்தவர்கள் அல்லது திரும்பி வந்தவர்கள்: முதலில் குறைந்த வேலை செய்யுங்கள்."]},
        "guidance": ["G-HI-MODERATE", "G-WATER-4CUPS", "G-SHADE-BREAKS", "G-BUDDY", "G-ACCLIM"],
    },
    "HIGH": {
        "summary": {"en": "High heat risk. Do the hardest work in the cooler hours and rest in the shade on a schedule.",
                    "ta": "அதிக வெப்ப அபாயம். கடினமான வேலையை குளிர்ந்த நேரத்தில் செய்து, அட்டவணைப்படி நிழலில் ஓய்வு எடுங்கள்."},
        "hydration": {"en": "Drink about one glass (250 ml) of water every 15 minutes, even if you are not thirsty.",
                      "ta": "தாகம் இல்லாவிட்டாலும் 15 நிமிடத்திற்கு ஒரு டம்ளர் (250 மி.லி) தண்ணீர் குடியுங்கள்."},
        "work_rest": {"en": ["Move the hardest tasks to the coolest hours (early morning or evening).",
                             "Follow a fixed work/rest schedule with rest in shade.", "Limit heavy lifting; use tools or share the load.",
                             "Work with a buddy and watch each other for warning signs."],
                      "ta": ["கடினமான வேலைகளை குளிர்ந்த நேரத்திற்கு (அதிகாலை அல்லது மாலை) மாற்றுங்கள்.",
                             "நிழலில் ஓய்வுடன் நிலையான வேலை/ஓய்வு அட்டவணையைப் பின்பற்றுங்கள்.",
                             "கனமான பொருட்களைத் தூக்குவதைக் குறையுங்கள்; கருவிகளைப் பயன்படுத்துங்கள் அல்லது பகிர்ந்து கொள்ளுங்கள்.",
                             "ஒரு துணையுடன் வேலை செய்து, ஒருவரை ஒருவர் கவனியுங்கள்."]},
        "guidance": ["G-HI-HIGH", "G-WATER-4CUPS", "G-WORK-REST", "G-BUDDY"],
    },
    "EXTREME": {
        "summary": {"en": "Extreme heat risk. Stop non-essential work and do essential work only in the coolest hours.",
                    "ta": "மிக அதிக வெப்ப அபாயம். அவசியமில்லாத வேலையை நிறுத்தி, அவசிய வேலையை மட்டும் மிகக் குளிர்ந்த நேரத்தில் செய்யுங்கள்."},
        "hydration": {"en": "Drink about one glass (250 ml) of water every 15 minutes on a fixed schedule.",
                      "ta": "நிலையான அட்டவணைப்படி 15 நிமிடத்திற்கு ஒரு டம்ளர் (250 மி.லி) தண்ணீர் குடியுங்கள்."},
        "work_rest": {"en": ["Stop non-essential work now and move it to a cooler day or time.",
                             "Essential work only in the coolest part of the shift.", "No strenuous work while the heat index is this high.",
                             "Someone must watch every worker at all times."],
                      "ta": ["அவசியமில்லாத வேலையை இப்போதே நிறுத்தி, குளிர்ந்த நாள் அல்லது நேரத்திற்கு மாற்றுங்கள்.",
                             "அவசிய வேலையை மட்டும் மிகக் குளிர்ந்த நேரத்தில் செய்யுங்கள்.",
                             "இந்த அளவு வெப்பத்தில் கடினமான உடல் உழைப்பு வேண்டாம்.",
                             "ஒவ்வொரு தொழிலாளியையும் எப்போதும் யாராவது கவனிக்க வேண்டும்."]},
        "guidance": ["G-HI-EXTREME", "G-WATER-4CUPS", "G-WORK-REST", "G-BUDDY"],
    },
}
