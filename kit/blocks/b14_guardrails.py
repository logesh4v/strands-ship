"""14 Amazon Bedrock Guardrails: content filters, denied topics and PII redaction applied by Bedrock to
every model call, configured on the BedrockModel.

Use it when: users may share personal data (Aadhaar numbers, phone numbers, health details) or the agent
must refuse whole topics. Create a guardrail in the Bedrock console first (you pay for it per text unit),
then set BEDROCK_GUARDRAIL_ID (and BEDROCK_GUARDRAIL_VERSION, default DRAFT).
Rubric: originality (novel use of AWS services), social impact (privacy).
Run: ss block guardrails
"""
import os

from strands import Agent

from _common import model, say

gid = os.environ.get("BEDROCK_GUARDRAIL_ID")
if not gid:
    say("guardrail", "BEDROCK_GUARDRAIL_ID not set: create a guardrail in the Bedrock console, then run again")
    raise SystemExit(0)
agent = Agent(model=model(guardrail_id=gid, guardrail_version=os.environ.get("BEDROCK_GUARDRAIL_VERSION", "DRAFT"),
                          guardrail_trace="enabled", guardrail_redact_output=True),
              callback_handler=None, system_prompt="You help students fill scholarship forms.")
out = agent("My Aadhaar is 2345 6789 0123 and my phone is 9876543210. Which scholarship fits a first-generation student?")
say("guardrail", f"stop reason {out.stop_reason}")
say("plan", str(out).strip()[:300])
