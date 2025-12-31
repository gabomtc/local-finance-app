from datetime import date

from core.models import Expense, Income
from db.queries import (
    expenses_by_category_in_range,
    get_settings,
    insert_expense,
    insert_income,
    list_expenses,
    list_income,
    totals_expenses_in_range,
    totals_income_in_range,
)


def test_schema_initialization(tmp_path) -> None:
    db_path = tmp_path / "finance.db"
    settings = get_settings(db_path=db_path)
    assert settings.initial_balance == 0.0
    assert settings.reserve_amount == 0.0


def test_insert_and_list(tmp_path) -> None:
    db_path = tmp_path / "finance.db"
    insert_expense(
        Expense(id=None, name="Coffee", amount=3.5, date=date(2024, 5, 1), category=None),
        db_path=db_path,
    )
    insert_income(Income(id=None, name="Paycheck", amount=2000.0, date=date(2024, 5, 2)), db_path=db_path)

    expenses = list_expenses(db_path=db_path)
    income = list_income(db_path=db_path)

    assert len(expenses) == 1
    assert expenses[0].name == "Coffee"
    assert len(income) == 1
    assert income[0].name == "Paycheck"


def test_totals_in_range(tmp_path) -> None:
    db_path = tmp_path / "finance.db"
    insert_expense(
        Expense(id=None, name="Groceries", amount=50.0, date=date(2024, 5, 5), category="Food"),
        db_path=db_path,
    )
    insert_income(Income(id=None, name="Bonus", amount=100.0, date=date(2024, 5, 10)), db_path=db_path)

    start = date(2024, 5, 1)
    end = date(2024, 6, 1)
    assert totals_expenses_in_range(start, end, db_path=db_path) == 50.0
    assert totals_income_in_range(start, end, db_path=db_path) == 100.0


def test_category_normalization_in_grouping(tmp_path) -> None:
    db_path = tmp_path / "finance.db"
    insert_expense(
        Expense(id=None, name="Lunch", amount=12.0, date=date(2024, 5, 3), category=""),
        db_path=db_path,
    )
    insert_expense(
        Expense(id=None, name="Snack", amount=5.0, date=date(2024, 5, 4), category="  "),
        db_path=db_path,
    )
    insert_expense(
        Expense(id=None, name="Taxi", amount=20.0, date=date(2024, 5, 5), category="Travel"),
        db_path=db_path,
    )

    results = expenses_by_category_in_range(date(2024, 5, 1), date(2024, 6, 1), db_path=db_path)
    totals = {category: total for category, total in results}

    assert totals["(uncategorized)"] == 17.0
    assert totals["Travel"] == 20.0
