"""
Centralized logging configuration that can suppress console output.

Environment variables:
- DEBUG_ENABLED: Enable/disable DEBUG messages (default: true)
- LLM_LOGGING_ENABLED: Enable/disable LLM debug messages (default: true)

Important messages are ALWAYS shown:
- Simulation start/end banners
- Provider and model info
- Step progress
- Errors and warnings
"""

import os
import sys

# Global logging flags
DEBUG_ENABLED = os.getenv("DEBUG_ENABLED", "true").lower() == "true"
LLM_LOGGING_ENABLED = os.getenv("LLM_LOGGING_ENABLED", "true").lower() == "true"


# Messages that should ALWAYS be shown (not filtered)
IMPORTANT_PATTERNS = [
    '============================================================',
    'Starting Simulation Execution',
    'Provider:',
    'Model:',
    'Max Steps:',
    'Agents:',
    'Simulation built successfully',
    '✓',  # Checkmarks for success
    '🎮',  # Game emoji
    '🔨',  # Hammer emoji
    '⚠️',  # Warning emoji
    '❌',  # Error emoji
    'Step ',  # Progress updates
    'of steps completed',
]


def is_important_message(text):
    """Check if message contains important patterns that should always be shown."""
    text_lower = text.lower()
    for pattern in IMPORTANT_PATTERNS:
        if pattern.lower() in text_lower:
            return True
    return False


def suppress_print_statements():
    """
    Intercept stdout/stderr to filter [DEBUG] and [LLM] messages.

    This works by replacing sys.stdout and sys.stderr with a custom
    stream that filters messages based on environment variables.

    IMPORTANT: Always shows simulation headers, provider info, progress, and errors.
    """
    class FilteredStream:
        """Wrapper around stdout/stderr that filters output."""

        def __init__(self, original_stream):
            self.original_stream = original_stream

        def write(self, text):
            # Always show important messages
            if is_important_message(text):
                self.original_stream.write(text)
                return

            # Filter [DEBUG] messages
            if '[DEBUG]' in text:
                if not DEBUG_ENABLED:
                    return

            # Filter [LLM] messages (but not important LLM info)
            if '[LLM]' in text:
                if not LLM_LOGGING_ENABLED:
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
