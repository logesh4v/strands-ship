"""13 voice (BidiAgent + Amazon Nova Sonic): talk to the agent through the microphone; it talks back and can
be interrupted mid-sentence (barge-in), and it calls tools while you speak.

Use it when: your users read with difficulty. Language check first: Nova 2 Sonic speaks English, French,
Italian, German, Spanish, Portuguese and Hindi, not Tamil (docs.aws.amazon.com/nova/latest/nova2-userguide/
sonic-language-support.html). For Tamil, take speech in with Amazon Transcribe (ta-IN) and answer in text.
Needs: Python 3.12+, a microphone, `brew install portaudio` (macOS), and
  pip install "strands-agents[bidi,bidi-io,bidi-pyaudio,bidi-aec]"
Run: ss block voice   (interactive: say "goodbye" to stop). Not run by the automated tests.
"""
import asyncio

from strands import ToolContext, tool
from strands.bidi import BidiAgent
from strands.bidi.io import AudioIO
from strands.bidi.models import BedrockNovaSonicModel


@tool
def heat_tip(job: str) -> str:
    """Return the fixed heat-safety tip for a job.

    Args:
        job: the worker's job, e.g. construction
    """
    return "Drink a glass of water every 15 minutes, rest in shade, and stop if you feel dizzy. Call 108 if someone is confused."


@tool(context=True)
def end_conversation(tool_context: ToolContext[BidiAgent]) -> str:
    """End the conversation when the user says goodbye."""
    tool_context.agent.cancel()
    return "Goodbye."


async def main() -> None:
    agent = BidiAgent(model=BedrockNovaSonicModel(model_id="amazon.nova-2-5-sonic"), tools=[heat_tip, end_conversation],
                      system_prompt="You are a heat-safety helper for outdoor workers. Short, calm replies in English or Hindi.")
    audio = AudioIO(audio_processor=True)  # echo cancellation for open speakers
    await agent.run(inputs=[audio.input()], outputs=[audio.output()])


if __name__ == "__main__":
    asyncio.run(main())
