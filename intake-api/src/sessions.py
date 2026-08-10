"""Sesiones de chat con TTL y tope (anti DoS de memoria)."""

from __future__ import annotations

import time
from threading import Lock
from typing import Any


class SessionStore:
    def __init__(self) -> None:
        self._lock = Lock()
        # conversation_id -> {"messages": [...], "touched": float, "total_tokens": int}
        self._data: dict[str, dict[str, Any]] = {}

    def _evict(self, *, max_sessions: int, ttl_seconds: int) -> None:
        now = time.time()
        if ttl_seconds > 0:
            dead = [k for k, v in self._data.items() if now - float(v["touched"]) > ttl_seconds]
            for k in dead:
                del self._data[k]
        if max_sessions > 0 and len(self._data) > max_sessions:
            ordered = sorted(self._data.items(), key=lambda kv: float(kv[1]["touched"]))
            overflow = len(self._data) - max_sessions
            for k, _ in ordered[:overflow]:
                del self._data[k]

    def get_messages(self, conversation_id: str) -> list[dict[str, str]]:
        with self._lock:
            row = self._data.get(conversation_id)
            if not row:
                return []
            return list(row["messages"])

    def total_tokens(self, conversation_id: str) -> int:
        with self._lock:
            row = self._data.get(conversation_id)
            return int(row.get("total_tokens", 0)) if row else 0

    def append(
        self,
        conversation_id: str,
        *,
        role: str,
        content: str,
        max_sessions: int,
        ttl_seconds: int,
        max_turns: int,
    ) -> None:
        with self._lock:
            self._evict(max_sessions=max_sessions, ttl_seconds=ttl_seconds)
            row = self._data.setdefault(
                conversation_id,
                {"messages": [], "touched": time.time(), "total_tokens": 0},
            )
            row["messages"].append({"role": role, "content": content})
            if max_turns > 0 and len(row["messages"]) > max_turns:
                row["messages"] = row["messages"][-max_turns:]
            row["touched"] = time.time()
            self._evict(max_sessions=max_sessions, ttl_seconds=ttl_seconds)

    def add_tokens(self, conversation_id: str, tokens: int) -> int:
        with self._lock:
            row = self._data.setdefault(
                conversation_id,
                {"messages": [], "touched": time.time(), "total_tokens": 0},
            )
            row["total_tokens"] = int(row.get("total_tokens", 0)) + max(0, tokens)
            row["touched"] = time.time()
            return int(row["total_tokens"])


sessions = SessionStore()
