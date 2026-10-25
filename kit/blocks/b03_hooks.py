"""03 hooks: plain Python that runs at a fixed moment in the agent loop and can cancel it.

Use it when: something must never be left to the model (a crisis word, a dose change, a child's name
in a public post). BeforeModelCallEvent.cancel stops the model call; a graph uses BeforeNodeCallEvent.
Rubric: social impact (safety you can prove), originality (beyond the workshop).
Run: ss block hooks
"""
from strands import Agent
from strands.hooks import BeforeModelCallEvent, HookProvider, HookRegistry

from _common import model, say

CRISIS = ["kill myself", "end my life", "suicide", "தற்கொலை"]
# Tele MANAS (Ministry of Health and Family Welfare): toll-free 14416, 24x7. https://telemanas.mohfw.gov.in/home
HELPLINE = "Please call Tele MANAS on 14416 now (free, 24x7, in English and many Indian languages), or 108 in an emergency."


class CrisisGate(HookProvider):
    def __init__(self):
        self.tripped = None

    def register_hooks(self, registry: HookRegistry, **_):
        registry.add_callback(BeforeModelCallEvent, self.check)

    def check(self, event: BeforeModelCallEvent):
        last = event.agent.messages[-1]["content"][0].get("text", "").lower() if event.agent.messages else ""
        hit = next((w for w in CRISIS if w in last), None)
        if hit:
            self.tripped = hit
            event.cancel = "crisis words: fixed helpline reply"


for text in ["I feel low about my exams today.", "I want to end my life."]:
    gate = CrisisGate()
    agent = Agent(model=model(), hooks=[gate], callback_handler=None, system_prompt="You are a kind study-stress check-in.")
    reply = agent(text)
    if gate.tripped:
        say("safety", f"RED FLAG ({gate.tripped}) -> model not called, helpline sent")
        print(HELPLINE)
    else:
        say("plan", str(reply).strip()[:200])
