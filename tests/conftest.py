"""Pytest configuration helpers."""

import logging
import os

PLACEHOLDER_AUTH = "demo:demo"


os.environ.setdefault("RTT_AUTH", PLACEHOLDER_AUTH)


logging.basicConfig(level=logging.DEBUG)
