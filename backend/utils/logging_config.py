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
            self.last_was_newline = False

        def write(self, text):
            # Skip empty strings
            if not text:
                return

            # Check if this should be filtered
            should_skip = False

            # Filter [DEBUG] messages
            if '[DEBUG]' in text:
                if not DEBUG_ENABLED:
                    should_skip = True

            # Filter [LLM] messages
            if '[LLM]' in text:
                if not LLM_LOGGING_ENABLED:
                    should_skip = True

            # Filter [HEARTBEAT] messages
            if '[HEARTBEAT]' in text:
                should_skip = True

            # Skip if marked for filtering
            if should_skip:
                return

            # Handle newlines properly - only allow single newlines
            if text == '\n':
                if not self.last_was_newline:
                    self.original_stream.write(text)
                    self.last_was_newline = True
                return
            else:
                self.last_was_newline = False

            # Filter out pure whitespace (spaces, tabs, multiple newlines)
            if text.strip() == '':
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
