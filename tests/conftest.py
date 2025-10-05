"""Pytest configuration helpers."""

import logging
import os

_PLACEHOLDER_AUTH = "demo:demo"


os.environ.setdefault("RTT_AUTH", _PLACEHOLDER_AUTH)


logging.basicConfig(level=logging.DEBUG)
