"""Rate limit in-memory por IP (single-instance; suficiente en Render starter)."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._lock = Lock()
        self._minute: dict[str, deque[float]] = defaultdict(deque)
        self._day: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, *, per_minute: int, per_day: int) -> tuple[bool, str]:
        now = time.time()
        with self._lock:
            m = self._minute[key]
            d = self._day[key]
            while m and now - m[0] > 60:
                m.popleft()
            while d and now - d[0] > 86400:
                d.popleft()
            if per_minute > 0 and len(m) >= per_minute:
                return False, "rate_limit_minute"
            if per_day > 0 and len(d) >= per_day:
                return False, "rate_limit_day"
            m.append(now)
            d.append(now)
            return True, "ok"


chat_limiter = SlidingWindowLimiter()
