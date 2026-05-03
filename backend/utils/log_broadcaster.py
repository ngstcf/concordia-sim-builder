import asyncio
import threading
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum


class LogCategory(str, Enum):
    SYSTEM = "system"
    DEBUG = "debug"
    LLM = "llm"


@dataclass
class LogEntry:
    timestamp: float
    category: LogCategory
    message: str


class LogBroadcaster:
    """Thread-safe log broadcaster with bounded buffer and SSE fan-out."""

    def __init__(self, max_buffer: int = 500):
        self._buffer: deque[LogEntry] = deque(maxlen=max_buffer)
        self._subscribers: list[asyncio.Queue] = []
        self._lock = threading.Lock()

    def emit(self, category: LogCategory, message: str):
        entry = LogEntry(timestamp=time.time(), category=category, message=message)
        with self._lock:
            self._buffer.append(entry)
            for q in self._subscribers:
                try:
                    q.put_nowait(entry)
                except asyncio.QueueFull:
                    pass

    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue(maxsize=200)
        with self._lock:
            self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)

    def get_recent(self, n: int = 100) -> list[LogEntry]:
        with self._lock:
            return list(self._buffer)[-n:]


broadcaster = LogBroadcaster()
