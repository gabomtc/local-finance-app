from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Iterable, Optional, Sequence

from core.calculations import normalize_category, validate_amount_nonnegative
from core.models import Expense, Income, Settings
from db.connection import DEFAULT_DB_PATH, get_connection

DateLike = date | str


def _to_date_string(value: DateLike) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return value


def _date_filter(start_date: Optional[DateLike], end_date: Optional[DateLike]) -> tuple[str, list]:
    clauses = []
    params: list = []
    if start_date is not None:
        clauses.append("date >= ?")
        params.append(_to_date_string(start_date))
    if end_date is not None:
        clauses.append("date <= ?")
        params.append(_to_date_string(end_date))
    if clauses:
        return " WHERE " + " AND ".join(clauses), params
    return "", params


def get_settings(db_path: Path | str = DEFAULT_DB_PATH) -> Settings:
    with get_connection(db_path) as connection:
        row = connection.execute("SELECT initial_balance, reserve_amount FROM settings WHERE id = 1").fetchone()
        if row is None:
            return Settings(initial_balance=0.0, reserve_amount=0.0)
        return Settings(initial_balance=row["initial_balance"], reserve_amount=row["reserve_amount"])


def upsert_settings(settings: Settings, db_path: Path | str = DEFAULT_DB_PATH) -> None:
    validate_amount_nonnegative(settings.initial_balance)
    validate_amount_nonnegative(settings.reserve_amount)
    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO settings (id, initial_balance, reserve_amount)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                initial_balance = excluded.initial_balance,
                reserve_amount = excluded.reserve_amount
            """,
            (settings.initial_balance, settings.reserve_amount),
        )
        connection.commit()


def insert_expense(expense: Expense, db_path: Path | str = DEFAULT_DB_PATH) -> int:
    validate_amount_nonnegative(expense.amount)
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO expenses (name, amount, date, category, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                expense.name,
                expense.amount,
                _to_date_string(expense.date),
                expense.category,
                expense.notes,
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def insert_income(income: Income, db_path: Path | str = DEFAULT_DB_PATH) -> int:
    validate_amount_nonnegative(income.amount)
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO income (name, amount, date, notes)
            VALUES (?, ?, ?, ?)
            """,
            (
                income.name,
                income.amount,
                _to_date_string(income.date),
                income.notes,
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def _rows_to_expenses(rows: Iterable) -> list[Expense]:
    return [
        Expense(
            id=row["id"],
            name=row["name"],
            amount=row["amount"],
            date=date.fromisoformat(row["date"]),
            category=row["category"],
            notes=row["notes"],
        )
        for row in rows
    ]


def _rows_to_income(rows: Iterable) -> list[Income]:
    return [
        Income(
            id=row["id"],
            name=row["name"],
            amount=row["amount"],
            date=date.fromisoformat(row["date"]),
            notes=row["notes"],
        )
        for row in rows
    ]


def list_expenses(
    db_path: Path | str = DEFAULT_DB_PATH,
    limit: Optional[int] = None,
    start_date: Optional[DateLike] = None,
    end_date: Optional[DateLike] = None,
) -> list[Expense]:
    date_clause, params = _date_filter(start_date, end_date)
    limit_clause = "" if limit is None else " LIMIT ?"
    if limit is not None:
        params.append(limit)
    query = f"SELECT * FROM expenses{date_clause} ORDER BY date DESC, id DESC{limit_clause}"
    with get_connection(db_path) as connection:
        rows = connection.execute(query, params).fetchall()
    return _rows_to_expenses(rows)


def list_income(
    db_path: Path | str = DEFAULT_DB_PATH,
    limit: Optional[int] = None,
    start_date: Optional[DateLike] = None,
    end_date: Optional[DateLike] = None,
) -> list[Income]:
    date_clause, params = _date_filter(start_date, end_date)
    limit_clause = "" if limit is None else " LIMIT ?"
    if limit is not None:
        params.append(limit)
    query = f"SELECT * FROM income{date_clause} ORDER BY date DESC, id DESC{limit_clause}"
    with get_connection(db_path) as connection:
        rows = connection.execute(query, params).fetchall()
    return _rows_to_income(rows)


def totals_income(db_path: Path | str = DEFAULT_DB_PATH) -> float:
    with get_connection(db_path) as connection:
        row = connection.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM income").fetchone()
    return float(row["total"])


def totals_expenses(db_path: Path | str = DEFAULT_DB_PATH) -> float:
    with get_connection(db_path) as connection:
        row = connection.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM expenses").fetchone()
    return float(row["total"])


def totals_income_in_range(start: DateLike, end: DateLike, db_path: Path | str = DEFAULT_DB_PATH) -> float:
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM income WHERE date >= ? AND date < ?",
            (_to_date_string(start), _to_date_string(end)),
        ).fetchone()
    return float(row["total"])


def totals_expenses_in_range(start: DateLike, end: DateLike, db_path: Path | str = DEFAULT_DB_PATH) -> float:
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE date >= ? AND date < ?",
            (_to_date_string(start), _to_date_string(end)),
        ).fetchone()
    return float(row["total"])


def expenses_by_category_in_range(
    start: DateLike, end: DateLike, db_path: Path | str = DEFAULT_DB_PATH
) -> Sequence[tuple[str, float]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                CASE
                    WHEN category IS NULL OR TRIM(category) = '' THEN '(uncategorized)'
                    ELSE TRIM(category)
                END AS category,
                SUM(amount) AS total
            FROM expenses
            WHERE date >= ? AND date < ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (_to_date_string(start), _to_date_string(end)),
        ).fetchall()
    return [(normalize_category(row["category"]), float(row["total"])) for row in rows]
