"""07 agents as tools: an orchestrator agent calls specialist agents like tools.

Use it when: one main agent should stay in charge and ask experts (a translator, a fact checker).
Rubric: technical execution (clear roles).
Run: ss block agents-as-tools
"""
from strands import Agent

from _common import model, say

simplifier = Agent(model=model(), name="simplifier", description="Rewrites medical text in plain words a 10-year-old understands.",
                   callback_handler=None, system_prompt="Rewrite the text in plain words. Keep every fact. Two sentences.")
translator = Agent(model=model(), name="tamil_translator", description="Translates English text into simple spoken Tamil.",
                   callback_handler=None, system_prompt="Translate into simple spoken Tamil script. Output only the Tamil.")

lead = Agent(model=model(), tools=[simplifier.as_tool(), translator.as_tool()], callback_handler=None,
             system_prompt="First call simplifier, then call tamil_translator on its output. Return only the Tamil text.")
out = lead("Paracetamol 500 mg: take one tablet every 6 hours after food if fever is above 100 F; do not exceed 4 tablets in 24 hours.")
say("tools", ", ".join(lead.tool_names))
say("plan", str(out).strip()[:300])
