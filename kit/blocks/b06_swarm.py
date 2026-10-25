"""06 swarm: agents that hand work to each other on their own. This is where the workshop ends.

Use it when: the path depends on the case (triage -> the right specialist). Judges see a plain swarm as
the baseline; pair it with a hook, a graph check or Decider routing to go beyond the lessons.
Run: ss block swarm
"""
from strands import Agent
from strands.multiagent import Swarm

from _common import model, say

triage = Agent(model=model(), name="triage", callback_handler=None,
               system_prompt="You read a farmer's message and hand off to the right specialist. Do not answer yourself.")
weather = Agent(model=model(), name="weather_advisor", callback_handler=None,
                system_prompt="You give one practical step for heat or rain risk to crops. Two sentences.")
scheme = Agent(model=model(), name="scheme_advisor", callback_handler=None,
               system_prompt="You explain which government help desk a farmer should visit. Two sentences. Never promise money.")

swarm = Swarm([triage, weather, scheme], entry_point=triage, max_handoffs=4, max_iterations=6)
res = swarm("No rain for 3 weeks and my paddy leaves are curling. What do I do today?")
say("swarm", " -> ".join(n.node_id for n in res.node_history))
last = res.node_history[-1].node_id
say("plan", str(res.results[last].result).strip()[:300])
