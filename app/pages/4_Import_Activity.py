from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from core.models import Expense, Income
from db.queries import insert_expense, insert_income

EXPECTED_COLUMNS = ["date", "description", "debit", "credit", "balance"]


def _clean_description(value: object) -> str:
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return "Account activity"
    return text


st.set_page_config(page_title="Import Activity", page_icon="📥", layout="wide")

st.title("📥 Import Account Activity")
st.write(
    "Upload a CSV with columns in this exact order: "
    "`date`, `description`, `debit`, `credit`, `balance`."
)

uploaded_file = st.file_uploader("Account activity CSV", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    normalized_columns = [column.strip().lower() for column in data.columns]

    if normalized_columns != EXPECTED_COLUMNS:
        st.error(
            "CSV columns must be: "
            "`date`, `description`, `debit`, `credit`, `balance` (in that order)."
        )
    else:
        data.columns = EXPECTED_COLUMNS
        data["date"] = pd.to_datetime(data["date"], errors="coerce").dt.date
        data["debit"] = pd.to_numeric(data["debit"], errors="coerce").fillna(0.0)
        data["credit"] = pd.to_numeric(data["credit"], errors="coerce").fillna(0.0)

        invalid_dates = data["date"].isna()
        negative_amounts = (data["debit"] < 0) | (data["credit"] < 0)

        if invalid_dates.any():
            st.error(
                f"Found {int(invalid_dates.sum())} rows with invalid dates. "
                "Please fix them before importing."
            )
        elif negative_amounts.any():
            st.error("Debit and credit values must be non-negative.")
        else:
            data["type"] = data.apply(
                lambda row: "expense" if row["debit"] > 0 else "income" if row["credit"] > 0 else "",
                axis=1,
            )
            st.dataframe(data, use_container_width=True)

            expenses = data[data["debit"] > 0]
            income = data[data["credit"] > 0]

            st.info(
                f"Ready to import {len(expenses)} expenses and {len(income)} income entries."
            )

            if st.button("Import activity"):
                with st.spinner("Importing activity..."):
                    for row in expenses.itertuples(index=False):
                        insert_expense(
                            Expense(
                                id=None,
                                name=_clean_description(row.description),
                                amount=float(row.debit),
                                date=row.date if isinstance(row.date, date) else date.today(),
                                category=None,
                                notes="Imported from account activity.",
                            )
                        )
                    for row in income.itertuples(index=False):
                        insert_income(
                            Income(
                                id=None,
                                name=_clean_description(row.description),
                                amount=float(row.credit),
                                date=row.date if isinstance(row.date, date) else date.today(),
                                notes="Imported from account activity.",
                            )
                        )
                st.success("Account activity imported.")
