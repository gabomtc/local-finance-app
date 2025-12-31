from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from db.queries import list_expenses, list_income


def export_csv(output_dir: Path, db_path: Path | str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    expenses_path = output_dir / f"expenses_{timestamp}.csv"
    income_path = output_dir / f"income_{timestamp}.csv"

    expenses = list_expenses(db_path=db_path)
    income = list_income(db_path=db_path)

    if expenses:
        with expenses_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=asdict(expenses[0]).keys())
            writer.writeheader()
            for expense in expenses:
                writer.writerow(asdict(expense))

    if income:
        with income_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=asdict(income[0]).keys())
            writer.writeheader()
            for entry in income:
                writer.writerow(asdict(entry))

    print(f"Exported {len(expenses)} expenses to {expenses_path}")
    print(f"Exported {len(income)} income entries to {income_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export finance data to CSV files.")
    parser.add_argument(
        "--db-path",
        default=Path(__file__).resolve().parents[1] / "data" / "finance.db",
        type=Path,
        help="Path to SQLite database file.",
    )
    parser.add_argument(
        "--output-dir",
        default=Path(__file__).resolve().parents[1] / "exports",
        type=Path,
        help="Directory for CSV exports.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    export_csv(args.output_dir, args.db_path)
