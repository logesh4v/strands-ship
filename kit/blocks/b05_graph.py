"""05 graph: fixed steps with a conditional edge, here writer -> checker -> back to writer (max 2 passes).

Use it when: you know the steps and want a quality loop you can see and count. Beyond the workshop's
swarm because the retry is a rule, not a hope. Rubric: technical execution, originality.
Run: ss block graph
"""
from pydantic import BaseModel
from strands import Agent
from strands.multiagent import GraphBuilder

from _common import model, say


class Passage(BaseModel):
    title: str
    text: str


class Check(BaseModel):
    ok: bool
    problems: list[str]


writer = Agent(model=model(), name="writer", structured_output_model=Passage, callback_handler=None,
               system_prompt="Write a 3-sentence reading passage for a Class 3 child. Fix every problem a checker lists.")
checker = Agent(model=model(), name="checker", structured_output_model=Check, callback_handler=None,
                system_prompt="ok=false if any sentence has more than 12 words or any word is harder than Class 3. List each problem.")


def again(state):
    v = state.results["checker"].result.structured_output
    n = sum(1 for x in state.execution_order if x.node_id == "writer")
    return bool(v and not v.ok and n < 2)


b = GraphBuilder()
b.add_node(writer, "writer")
b.add_node(checker, "checker")
b.add_edge("writer", "checker")
b.add_edge("checker", "writer", condition=again)
b.set_entry_point("writer")
b.set_max_node_executions(4)
b.reset_on_revisit(True)
res = b.build()("A passage about why we drink water on hot days.")
order = [n.node_id for n in res.execution_order]
say("graph", " -> ".join(order))
say("critic", "PASS" if res.results["checker"].result.structured_output.ok else "still REVISE after 2 passes")
say("plan", res.results["writer"].result.structured_output.text)
