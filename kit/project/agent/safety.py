"""Red-flag gate. Runs as a Strands hook on the graph, before any agent node, and outside the LLM.

Tiers follow NIOSH "Heat-related Illnesses" (cdc.gov/niosh/heat-stress/about/illnesses.html):
- emergency: heat stroke signs (confusion, slurred speech, loss of consciousness, seizures, hot dry
  skin / sweating stopped, very high body temperature) and rhabdomyolysis's dark urine. NIOSH:
  call emergency medical care. In India that is 108.
- care: heat exhaustion / syncope / cramps signs (dizziness, headache, nausea, weakness, cramps,
  fainting that passes). NIOSH: stop, cool down, drink, get medical evaluation.

This is a phrase list, so it misses wording it has never seen. Every miss you find goes into
FAILURES.md and into the lists below; the measure step proves recall on your labelled cases.
"""
from __future__ import annotations

import re
import unicodedata

from strands.hooks import BeforeNodeCallEvent, HookProvider, HookRegistry

EMERGENCY = {
    "confusion": ["confused", "confusion", "not making sense", "talking nonsense", "doesn't know where",
                  "does not know where", "disoriented", "குழப்ப", "குழம்பி", "உளறு", "புரியாமல் பேச"],
    "slurred speech": ["slurred", "slurring", "can't speak properly", "cannot speak properly", "பேச்சு குழற", "குழறி"],
    "unconscious": ["unconscious", "passed out and not waking", "not waking", "won't wake", "will not wake",
                    "not responding", "unresponsive", "collapsed", "சுயநினைவு இழ", "நினைவிழ", "மயங்கி விழுந்து எழ", "எழுந்திருக்கவில்லை"],
    "seizure": ["seizure", "fits", "convulsion", "shaking uncontrollably", "jerking", "வலிப்பு"],
    "stopped sweating": ["stopped sweating", "not sweating", "hot dry skin", "skin is hot and dry", "dry hot skin",
                         "வியர்வை நின்று", "வியர்க்கவில்லை", "தோல் சூடாகவும் வறண்டு"],
    "very high temperature": ["very high fever", "body is burning", "body burning", "burning up",
                              "உடல் கொதிக்", "அதிக காய்ச்சல்"],
    "dark urine": ["dark urine", "urine is dark", "dark like cola", "like cola", "like black tea", "cola-coloured urine", "cola colored urine", "tea-coloured urine", "tea colored urine",
                   "கருப்பு சிறுநீர்", "கருமையான சிறுநீர்", "டீ நிற சிறுநீர்"],
    "chest pain": ["chest pain", "நெஞ்சு வலி", "மார்பு வலி"],
}
CARE = {
    "dizziness": ["dizzy", "dizziness", "light-headed", "lightheaded", "தலைசுற்ற", "தலை சுற்ற"],
    "headache": ["headache", "தலைவலி", "தலை வலி"],
    "nausea": ["nausea", "nauseous", "vomit", "vomited", "vomiting", "throwing up", "threw up", "குமட்ட", "வாந்தி"],
    "weakness": ["very weak", "weakness", "exhausted", "சோர்வ", "பலவீன"],
    "cramps": ["cramp", "cramps", "muscle spasm", "தசைப்பிடிப்பு", "சதைப்பிடிப்பு"],
    "fainted": ["fainted", "fainting", "blacked out", "மயக்கம்", "மயங்கி"],
}

NUMBER = "108"
TEXT = {
    "emergency": {
        "en": "EMERGENCY: possible heat stroke. Call 108 now. Stay with the person, move them to shade, "
              "remove extra clothing and cool them with water and fanning until help arrives.",
        "ta": "அவசரம்: வெப்பத் தாக்கமாக இருக்கலாம். உடனே 108 அழையுங்கள். அவருடன் இருங்கள், நிழலுக்கு மாற்றுங்கள், "
              "கூடுதல் உடைகளை அகற்றி, உதவி வரும் வரை தண்ணீர் தெளித்து விசிறி குளிர்விக்கவும்.",
    },
    "care": {
        "en": "STOP WORK NOW: these are warning signs of heat exhaustion. Move to shade, drink water slowly, "
              "cool down and get checked at a clinic today. If they get confused, faint or stop sweating, call 108.",
        "ta": "இப்போதே வேலையை நிறுத்துங்கள்: இவை வெப்பச் சோர்வின் எச்சரிக்கை அறிகுறிகள். நிழலுக்குச் சென்று மெதுவாகத் தண்ணீர் குடியுங்கள், "
              "உடலைக் குளிர்வித்து இன்றே மருத்துவமனையில் பரிசோதியுங்கள். குழப்பம், மயக்கம் அல்லது வியர்வை நின்றால் 108 அழையுங்கள்.",
    },
}
# NIOSH warning signs, worded for the worker (G-SIGNS-EXHAUSTION, G-SIGNS-STROKE). Code-owned: the
# model's own Tamil for symptoms was unreliable in testing, and this list must never be wrong.
WARNING_SIGNS = {
    "en": ["Dizziness or headache", "Feeling sick or vomiting", "Muscle cramps", "Very weak or very thirsty",
           "Confusion, fainting or no sweating: call 108"],
    "ta": ["தலைசுற்றல் அல்லது தலைவலி", "குமட்டல் அல்லது வாந்தி", "தசைப்பிடிப்பு", "மிகுந்த சோர்வு அல்லது அதிக தாகம்",
           "குழப்பம், மயக்கம் அல்லது வியர்வை நிற்பது: 108 அழையுங்கள்"],
}

# NIOSH heat-exhaustion first aid, as steps for the worker (guidance id G-FIRSTAID-EXHAUSTION).
CARE_STEPS = {
    "en": ["Stop work now and move out of the heat, into shade.", "Drink water slowly.",
           "Take off extra clothing and cool your head, face and neck with water.", "Get checked at a clinic today."],
    "ta": ["இப்போதே வேலையை நிறுத்தி, வெயிலிலிருந்து நிழலுக்குச் செல்லுங்கள்.", "மெதுவாகத் தண்ணீர் குடியுங்கள்.",
           "கூடுதல் உடைகளை அகற்றி, தலை, முகம், கழுத்தை தண்ணீரால் குளிர்வியுங்கள்.", "இன்றே மருத்துவமனையில் பரிசோதியுங்கள்."],
}
NEGATIONS = ["no ", "not ", "never ", "without ", "இல்லை"]


def _norm(text: str) -> str:
    return unicodedata.normalize("NFC", text).lower()


def _hit(text: str, phrase: str) -> bool:
    p = _norm(phrase)
    if re.fullmatch(r"[a-z0-9' -]+", p):
        # Whole-word match for English; skip a phrase that a negation sits right in front of
        # ("no dizziness"), so "no headache" does not trip the gate.
        for m in re.finditer(r"(?<![a-z])" + re.escape(p) + r"(?![a-z])", text):
            before = text[max(0, m.start() - 9):m.start()]
            if not any(before.endswith(n) for n in NEGATIONS):
                return True
        return False
    return p in text


def check(text: str) -> tuple[str | None, list[str]]:
    """Return ("emergency" | "care" | None, matched sign names)."""
    t = _norm(text)
    em = [name for name, ps in EMERGENCY.items() if any(_hit(t, p) for p in ps)]
    if em:
        return "emergency", em
    care = [name for name, ps in CARE.items() if any(_hit(t, p) for p in ps)]
    return ("care", care) if care else (None, [])


class RedFlagGate(HookProvider):
    """Cancels every agent node in the graph when the message carries an emergency sign.

    The graph raises when a node is cancelled; app.py catches that, reads `tripped` and answers
    with the fixed emergency text. No model output can replace it.
    """

    def __init__(self) -> None:
        self.tripped: list[str] = []

    def register_hooks(self, registry: HookRegistry, **_: object) -> None:
        registry.add_callback(BeforeNodeCallEvent, self._before_node)

    def _before_node(self, event: BeforeNodeCallEvent) -> None:
        tier, signs = check(str(event.invocation_state.get("user_text", "")))
        if tier == "emergency":
            self.tripped = signs
            event.cancel_node = "red flag: " + ", ".join(signs)
