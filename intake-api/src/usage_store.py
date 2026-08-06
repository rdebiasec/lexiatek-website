"""Persistencia simple de usage (JSONL) para panel admin."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

_lock = Lock()


def append_usage(path: str, record: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    row = {
        **record,
        "ts": record.get("ts") or datetime.now(timezone.utc).isoformat(),
    }
    with _lock:
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def summarize_usage(path: str, *, days: int = 7) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {
            "days": days,
            "runs": 0,
            "total_tokens": 0,
            "estimated_cost_usd": 0.0,
            "estimated_cost_cop": 0.0,
            "top_conversations": [],
        }

    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    rows: list[dict[str, Any]] = []
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = row.get("ts")
            try:
                t = datetime.fromisoformat(str(ts).replace("Z", "+00:00")).timestamp()
            except ValueError:
                continue
            if t >= cutoff:
                rows.append(row)

    total_tokens = sum(int(r.get("total_tokens") or 0) for r in rows)
    cost_usd = sum(float(r.get("estimated_cost_usd") or 0) for r in rows)
    cost_cop = sum(float(r.get("estimated_cost_cop") or 0) for r in rows)

    by_conv: dict[str, dict[str, Any]] = {}
    for r in rows:
        cid = str(r.get("conversation_id") or "unknown")
        bucket = by_conv.setdefault(
            cid,
            {"conversation_id": cid, "total_tokens": 0, "estimated_cost_cop": 0.0, "runs": 0},
        )
        bucket["total_tokens"] += int(r.get("total_tokens") or 0)
        bucket["estimated_cost_cop"] += float(r.get("estimated_cost_cop") or 0)
        bucket["runs"] += 1

    top = sorted(by_conv.values(), key=lambda x: x["total_tokens"], reverse=True)[:10]
    return {
        "days": days,
        "runs": len(rows),
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(cost_usd, 6),
        "estimated_cost_cop": round(cost_cop, 2),
        "top_conversations": top,
    }
