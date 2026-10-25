"""01 tools + structured output: the base every agent builds on.

Use it when: the agent must look facts up (a tool) and return the same fields every time (structured
output), so you can score every answer. Rubric: technical execution.
Run: ss block tools
"""
from pydantic import BaseModel, Field
from strands import Agent, tool

from _common import model, say

CLINICS = {"madurai": "Government Rajaji Hospital (sample)", "theni": "District HQ Hospital (sample)"}


@tool
def nearest_clinic(district: str) -> str:
    """Return the listed clinic for a district.

    Args:
        district: district name, e.g. Madurai
    """
    return CLINICS.get(district.strip().lower(), "not listed: ask a local health worker")


class Answer(BaseModel):
    district: str
    clinic: str = Field(description="exactly what nearest_clinic returned")
    advice: str = Field(description="one short sentence")


agent = Agent(model=model(), tools=[nearest_clinic], structured_output_model=Answer, callback_handler=None,
              system_prompt="Answer health-access questions. Always call nearest_clinic. Never invent a clinic.")
out = agent("My mother in Madurai has a fever since two days. Where should she go?").structured_output
say("tool", f"nearest_clinic -> {out.clinic}")
say("plan", out.model_dump_json())
assert out.clinic == CLINICS["madurai"], "the clinic must come from the tool"
