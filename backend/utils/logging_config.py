"""
Centralized logging configuration that can suppress console output.

Environment variables:
- DEBUG_ENABLED: Enable/disable DEBUG messages (default: true)
- LLM_LOGGING_ENABLED: Enable/disable LLM debug messages (default: true)

All messages pass through except [DEBUG] and [LLM] based on .env settings.
"""

import os
import sys

# Global logging flags
DEBUG_ENABLED = os.getenv("DEBUG_ENABLED", "true").lower() == "true"
LLM_LOGGING_ENABLED = os.getenv("LLM_LOGGING_ENABLED", "true").lower() == "true"


def suppress_print_statements():
    """
    Intercept stdout/stderr to filter [DEBUG] and [LLM] messages.

    This works by replacing sys.stdout and sys.stderr with a custom
    stream that filters messages based on environment variables.
    """
    class FilteredStream:
        """Wrapper around stdout/stderr that filters output."""

        def __init__(self, original_stream):
            self.original_stream = original_stream

        def write(self, text):
            # Skip empty strings
            if not text:
                return

            # Filter out pure whitespace (but keep newlines for formatting)
            if text.strip() == '' and text not in ['\n', '\r\n', '\r']:
                return

            # Filter [DEBUG] messages
            if '[DEBUG]' in text:
                if not DEBUG_ENABLED:
                    return

            # Filter [LLM] messages
            if '[LLM]' in text:
                if not LLM_LOGGING_ENABLED:
                    return

            # Filter [HEARTBEAT] messages
            if '[HEARTBEAT]' in text:
                return

            # Pass through to original stream
            self.original_stream.write(text)

        def flush(self):
            self.original_stream.flush()

    # Replace stdout and stderr with filtered versions
    sys.stdout = FilteredStream(sys.stdout)
    sys.stderr = FilteredStream(sys.stderr)


# Auto-setup on import
suppress_print_statements()
