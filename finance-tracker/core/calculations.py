from __future__ import annotations


def current_balance(initial_balance: float, total_income: float, total_expenses: float) -> float:
    """Compute current balance from settings and totals."""
    return initial_balance + total_income - total_expenses


def available_balance(current_balance_value: float, reserve_amount: float) -> float:
    """Compute available balance after subtracting reserve amount."""
    return current_balance_value - reserve_amount


def validate_amount_nonnegative(value: float) -> float:
    """Validate that a numeric amount is non-negative."""
    if value < 0:
        raise ValueError("Amount must be non-negative")
    return value


def normalize_category(category: str | None) -> str:
    """Normalize category text for reporting."""
    if category is None:
        return "(uncategorized)"
    cleaned = category.strip()
    return cleaned if cleaned else "(uncategorized)"
