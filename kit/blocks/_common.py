"""Shared helper for the blocks. Every block runs on its own: `ss block <name>` or `python blocks/<file>.py`.

Model: SHIP_MODEL (default Amazon Nova 2 Lite, no AWS Marketplace subscription needed) in AWS_REGION (default us-east-1).
"""
import logging
import os

from strands.models import BedrockModel

MODEL_ID = os.environ.get("SHIP_MODEL", "us.amazon.nova-2-lite-v1:0")
REGION = os.environ.get("AWS_REGION", "us-east-1")
logging.getLogger("strands").setLevel(logging.CRITICAL)


def model(**kw) -> BedrockModel:
    return BedrockModel(model_id=MODEL_ID, region_name=REGION, temperature=kw.pop("temperature", 0.2), **kw)


def say(tag: str, text: str) -> None:
    """Evidence line: the video studio turns [tag] lines into badges."""
    print(f"[{tag}] {text}", flush=True)
