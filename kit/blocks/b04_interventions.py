"""04 interventions: typed control decisions on the agent loop (Proceed, Deny, Guide, Confirm, Transform).

Use it when: some tool calls need a rule or a person. Deny blocks a call, Guide sends feedback so the
model retries properly (steering), Confirm pauses for human approval (an interrupt you resume with
the person's answer). Rubric: technical execution, social impact (people stay in control).
Run: ss block interventions
"""
from strands import Agent, tool
from strands.interventions import Deny, Guide, InterventionHandler, Proceed

from _common import model, say

SENT = []
REGISTERED = {"9876543210"}  # farmers who gave consent; everyone else is denied by code


@tool
def send_sms(phone: str, text: str) -> str:
    """Send an SMS to a farmer.

    Args:
        phone: 10-digit Indian mobile number
        text: message under 160 characters, in Tamil or English
    """
    SENT.append((phone, text))
    return "sent"


class SmsPolicy(InterventionHandler):
    name = "sms-policy"

    def before_tool_call(self, event):
        args = event.tool_use["input"]
        if args.get("phone") not in REGISTERED:
            say("guard", f"DENY: {args.get('phone')} has not opted in to alerts")
            return Deny(reason="This number has not opted in to SMS alerts. Do not send. Tell the user it needs consent first.")
        if len(args.get("text", "")) > 160:
            say("guard", "GUIDE: message too long, model asked to shorten")
            return Guide(feedback="The SMS is over 160 characters. Rewrite it shorter and call send_sms again.")
        return Proceed()


agent = Agent(model=model(), tools=[send_sms], interventions=[SmsPolicy()], callback_handler=None,
              system_prompt="You send heat-wave alerts to farmers by SMS.")
agent("Send a heat-wave alert to farmers 9876543210 and 9123456789: irrigate before 7 am and rest in shade at noon. "
      "Make it detailed, explain heat stress, crop water needs and give five tips.")
say("plan", f"SMS actually sent: {SENT or 'none'}")
