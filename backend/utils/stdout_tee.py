import re
import sys

from backend.utils.log_broadcaster import broadcaster, LogCategory

_ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')


class TeeStdout:
    """Wraps stdout: writes to original terminal + broadcasts to LogBroadcaster."""

    def __init__(self, original):
        self._original = original
        self._buffer = ""

    def write(self, text: str):
        self._original.write(text)
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            clean = _ANSI_ESCAPE.sub("", line)
            category = self._categorize(clean)
            broadcaster.emit(category, clean)

    def _categorize(self, line: str) -> LogCategory:
        if "[LLM]" in line:
            return LogCategory.LLM
        if "[DEBUG]" in line:
            return LogCategory.DEBUG
        return LogCategory.SYSTEM

    def flush(self):
        self._original.flush()

    def __getattr__(self, name):
        return getattr(self._original, name)


def install_tee():
    if not isinstance(sys.stdout, TeeStdout):
        sys.stdout = TeeStdout(sys.stdout)
