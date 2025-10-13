"""Pytest configuration helpers."""

import logging

from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(level=logging.DEBUG)
