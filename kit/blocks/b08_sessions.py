"""08 sessions + memory: the agent remembers a user across runs (files on disk, or S3 with S3SessionManager).

Use it when: a daily check-in, a tutor that tracks progress, a farmer who comes back each week.
Measurable impact needs a "before" and an "after" for the same person; sessions give you that.
Run: ss block sessions
"""
import shutil
import tempfile

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.session import FileSessionManager

from _common import model, say

store = tempfile.mkdtemp(prefix="ship-sessions-")


def tutor():
    return Agent(model=model(), callback_handler=None, conversation_manager=SlidingWindowConversationManager(window_size=20),
                 session_manager=FileSessionManager(session_id="student-007", storage_dir=store),
                 system_prompt="You are a maths tutor. Keep answers to one sentence.")


tutor()("Remember: my name is Kavya and I keep getting fractions wrong.")
say("session", f"run 1 saved to {store}")
out = tutor()("What is my name and what should we practise today?")  # a brand-new Agent object
say("plan", str(out).strip()[:200])
assert "kavya" in str(out).lower(), "the second run must remember the first"
shutil.rmtree(store, ignore_errors=True)
