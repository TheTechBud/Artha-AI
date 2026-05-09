def format_inr(amount: float) -> str:
    """Format a number as Indian Rupees."""
    return f"₹{amount:,.0f}"


def drs_label(score: float) -> str:
    if score >= 81:
        return "Optimal"
    if score >= 61:
        return "Stable"
    if score >= 41:
        return "Caution"
    if score >= 21:
        return "Danger"
    return "Critical"


def drs_color(score: float) -> str:
    if score >= 81:
        return "green"
    if score >= 61:
        return "teal"
    if score >= 41:
        return "amber"
    if score >= 21:
        return "orange"
    return "red"


def pct(value: float, total: float) -> float:
    if total == 0:
        return 0.0
    return round((value / total) * 100, 1)


def truncate(text: str, max_len: int = 120) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "…"
