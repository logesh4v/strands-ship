"""Structured output. Every plan has the same fields, so every plan can be scored."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ShiftPlan(BaseModel):
    language: Literal["en", "ta"] = Field(description="Language the worker wrote in: en or ta")
    risk_level: Literal["LOWER", "MODERATE", "HIGH", "EXTREME"] = Field(description="Copy exactly from the heat_risk tool")
    heat_index_c: float = Field(description="Copy exactly from the heat_risk tool")
    summary: str = Field(description="One or two short sentences the worker reads first, in their language")
    work_rest: list[str] = Field(description="Short work/rest steps for this job and this shift, in their language")
    hydration: str = Field(description="How much water and how often, in their language")
    warning_signs: list[str] = Field(description="Signs that mean stop now, in their language")
    escalation: str = Field(description="What to do and who to call if warning signs appear, in their language")
    water_points: list[str] = Field(default_factory=list, description="Nearest listed water/shade points, from the tool")
    citations: list[str] = Field(description="Guidance ids (like G-WATER-4CUPS) that back this plan. Only ids returned by tools")


class Critique(BaseModel):
    ok: bool = Field(description="true only if the plan breaks none of the rules")
    problems: list[str] = Field(default_factory=list, description="Each rule the plan breaks, one short line each")
