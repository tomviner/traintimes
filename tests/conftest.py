"""Pytest configuration helpers."""

import logging
import os

from dotenv import load_dotenv

load_dotenv()
_PLACEHOLDER_AUTH = "demo:demo"


os.environ.setdefault("RTT_AUTH", _PLACEHOLDER_AUTH)


logging.basicConfig(level=logging.DEBUG)
