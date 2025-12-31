from __future__ import annotations

from dataclasses import asdict

import pandas as pd
import streamlit as st

from app.ui.forms import expense_form
from db.queries import insert_expense, list_expenses

st.set_page_config(page_title="Add Expense", page_icon="🧾", layout="wide")

st.title("🧾 Add Expense")

expense = expense_form()
if expense:
    insert_expense(expense)
    st.success("Expense added.")

st.subheader("Latest expenses")
expenses = list_expenses(limit=20)
if expenses:
    st.dataframe(pd.DataFrame([asdict(item) for item in expenses]), use_container_width=True)
else:
    st.info("No expenses recorded yet.")
