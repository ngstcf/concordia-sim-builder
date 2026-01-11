"""
Centralized logging configuration for the backend.

Environment variables:
- DEBUG_ENABLED: Enable/disable DEBUG messages (default: true)
- LLM_LOGGING_ENABLED: Enable/disable LLM debug messages (default: true)
"""

import os
from typing import Optional

# Global logging flags
DEBUG_ENABLED = os.getenv("DEBUG_ENABLED", "true").lower() == "true"
LLM_LOGGING_ENABLED = os.getenv("LLM_LOGGING_ENABLED", "true").lower() == "true"


def debug_print(message: str, category: str = "DEBUG") -> None:
    """
    Conditional print statement that respects environment variables.

    Args:
        message: The message to print
        category: The log category (DEBUG, LLM, etc.)
    """
    if category == "LLM" and not LLM_LOGGING_ENABLED:
        return
    if category == "DEBUG" and not DEBUG_ENABLED:
        return

    print(f"[{category}] {message}")


def set_debug_enabled(enabled: bool) -> None:
    """Enable or disable DEBUG messages at runtime."""
    global DEBUG_ENABLED
    DEBUG_ENABLED = enabled


def set_llm_logging_enabled(enabled: bool) -> None:
    """Enable or disable LLM logging at runtime."""
    global LLM_LOGGING_ENABLED
    LLM_LOGGING_ENABLED = enabled


def is_debug_enabled() -> bool:
    """Check if DEBUG logging is enabled."""
    return DEBUG_ENABLED


def is_llm_logging_enabled() -> bool:
    """Check if LLM logging is enabled."""
    return LLM_LOGGING_ENABLED
