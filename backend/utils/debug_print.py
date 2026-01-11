"""
Debug print utility that respects environment variables.

Use this instead of regular print() to control debug output via .env:

- DEBUG_ENABLED=false    : Hides [DEBUG] messages
- LLM_LOGGING_ENABLED=false: Hides [LLM] messages

Usage:
    from backend.utils.debug_print import debug_print, llm_print

    debug_print("This is a debug message")  # Only shows if DEBUG_ENABLED=true
    llm_print("This is an LLM message")      # Only shows if LLM_LOGGING_ENABLED=true
"""

import os

# Global logging flags - read from environment once at import
DEBUG_ENABLED = os.getenv("DEBUG_ENABLED", "true").lower() == "true"
LLM_LOGGING_ENABLED = os.getenv("LLM_LOGGING_ENABLED", "true").lower() == "true"


def debug_print(*args, **kwargs):
    """
    Print function that respects DEBUG_ENABLED environment variable.

    Use this for [DEBUG] tagged messages that should only show when debugging.
    """
    if DEBUG_ENABLED:
        print(*args, **kwargs)


def llm_print(*args, **kwargs):
    """
    Print function that respects LLM_LOGGING_ENABLED environment variable.

    Use this for [LLM] tagged messages about API calls, response times, etc.
    """
    if LLM_LOGGING_ENABLED:
        print(*args, **kwargs)
