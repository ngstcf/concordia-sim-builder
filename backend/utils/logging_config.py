"""
Centralized logging configuration that can suppress console output.

Environment variables:
- DEBUG_ENABLED: Enable/disable DEBUG messages (default: true)
- LLM_LOGGING_ENABLED: Enable/disable LLM debug messages (default: true)

This uses Python's logging module to filter messages without
interfering with terminal color output.
"""

import os
import sys
import logging

# Global logging flags
DEBUG_ENABLED = os.getenv("DEBUG_ENABLED", "true").lower() == "true"
LLM_LOGGING_ENABLED = os.getenv("LLM_LOGGING_ENABLED", "true").lower() == "true"


class DebugFilter(logging.Filter):
    """Custom filter to control [DEBUG] and [LLM] log messages."""

    def filter(self, record):
        # Check if this is a debug log with [DEBUG] or [LLM] tags
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            msg_lower = record.msg.lower()

            # Filter [DEBUG] messages
            if '[debug]' in msg_lower:
                return DEBUG_ENABLED

            # Filter [LLM] messages
            if '[llm]' in msg_lower:
                return LLM_LOGGING_ENABLED

        return True


def setup_logging_filter():
    """
    Setup logging filter without interfering with stdout/stderr.

    This approach:
    - Does NOT intercept sys.stdout/sys.stderr (preserves colors)
    - Only affects logging module output
    - Regular print() statements work normally
    """
    # Note: We're not using the logging module for most output,
    # so this filter won't catch print() statements with [DEBUG]/[LLM]

    # For now, this is a placeholder for future implementation
    pass


# Auto-setup on import (disabled for now)
# setup_logging_filter()
