from __future__ import annotations

from dataclasses import asdict
from datetime import date

import pandas as pd
import streamlit as st

from app.ui.forms import settings_form
from app.ui.metrics import render_metrics
from core.calculations import available_balance, current_balance
from core.dates import month_bounds
from db.queries import (
    get_settings,
    list_expenses,
    list_income,
    totals_expenses,
    totals_expenses_in_range,
    totals_income,
    totals_income_in_range,
    upsert_settings,
)

st.set_page_config(page_title="Finance Tracker", page_icon="💰", layout="wide")

st.title("💰 Finance Tracker")
st.write("Track your income and expenses locally with SQLite.")

settings = get_settings()
updated_settings = settings_form(settings)
if updated_settings:
    upsert_settings(updated_settings)
    st.success("Settings updated.")
    settings = updated_settings

month_start, next_month_start = month_bounds(date.today())

income_total = totals_income()
expense_total = totals_expenses()
current = current_balance(settings.initial_balance, income_total, expense_total)
available = available_balance(current, settings.reserve_amount)
spent_month = totals_expenses_in_range(month_start, next_month_start)
earned_month = totals_income_in_range(month_start, next_month_start)

render_metrics(current, available, spent_month, earned_month)

st.subheader("Recent expenses")
expenses = list_expenses(limit=10)
if expenses:
    st.dataframe(pd.DataFrame([asdict(expense) for expense in expenses]), use_container_width=True)
else:
    st.info("No expenses yet.")

st.subheader("Recent income")
income = list_income(limit=10)
if income:
    st.dataframe(pd.DataFrame([asdict(entry) for entry in income]), use_container_width=True)
else:
    st.info("No income yet.")
