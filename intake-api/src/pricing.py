"""Precios OpenAI USD/1M + conversión COP (TRM configurable)."""

from __future__ import annotations

_MODEL_PRICES_USD_PER_1M: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1": (2.00, 8.00),
    "gpt-4o": (2.50, 10.00),
}


def price_for_model(model: str | None) -> tuple[float, float] | None:
    if not model:
        return None
    key = str(model).strip().lower()
    if key in _MODEL_PRICES_USD_PER_1M:
        return _MODEL_PRICES_USD_PER_1M[key]
    for known, prices in _MODEL_PRICES_USD_PER_1M.items():
        if key.startswith(known):
            return prices
    return None


def estimate_cost_usd(*, model: str | None, input_tokens: int, output_tokens: int) -> float | None:
    prices = price_for_model(model)
    if prices is None:
        return None
    in_rate, out_rate = prices
    return (max(0, input_tokens) * in_rate + max(0, output_tokens) * out_rate) / 1_000_000.0


def estimate_cost_cop(
    *,
    model: str | None,
    input_tokens: int,
    output_tokens: int,
    usd_to_cop: float,
) -> float | None:
    usd = estimate_cost_usd(model=model, input_tokens=input_tokens, output_tokens=output_tokens)
    if usd is None:
        return None
    return round(usd * usd_to_cop, 2)
