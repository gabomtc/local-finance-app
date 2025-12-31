import pytest

from core.calculations import (
    available_balance,
    current_balance,
    normalize_category,
    validate_amount_nonnegative,
)


def test_current_balance() -> None:
    assert current_balance(100.0, 50.0, 25.0) == 125.0


def test_available_balance() -> None:
    assert available_balance(125.0, 25.0) == 100.0


def test_validate_amount_nonnegative_allows_zero() -> None:
    assert validate_amount_nonnegative(0.0) == 0.0


def test_validate_amount_nonnegative_raises() -> None:
    with pytest.raises(ValueError):
        validate_amount_nonnegative(-0.01)


def test_normalize_category() -> None:
    assert normalize_category(None) == "(uncategorized)"
    assert normalize_category("") == "(uncategorized)"
    assert normalize_category("  ") == "(uncategorized)"
    assert normalize_category(" Food ") == "Food"
