"""
Centralized logging configuration that can suppress console output.

Environment variables:
- DEBUG_ENABLED: Enable/disable DEBUG messages (default: true)
- LLM_LOGGING_ENABLED: Enable/disable LLM debug messages (default: true)

Temporarily DISABLED to restore blue color output.
"""

import os
import sys

# Global logging flags
DEBUG_ENABLED = os.getenv("DEBUG_ENABLED", "true").lower() == "true"
LLM_LOGGING_ENABLED = os.getenv("LLM_LOGGING_ENABLED", "true").lower() == "true"


def suppress_print_statements():
    """
    DISABLED: This function is disabled to restore blue color output.

    The filtering mechanism was interfering with terminal color output.
    For now, all messages pass through unchanged.
    """
    pass  # Disabled - let all output through naturally


# Auto-setup on import is also disabled
# suppress_print_statements()
