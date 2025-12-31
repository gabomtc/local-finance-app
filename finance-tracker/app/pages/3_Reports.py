from __future__ import annotations

from dataclasses import asdict
from datetime import date

import pandas as pd
import streamlit as st

from app.ui.metrics import render_metrics
from core.calculations import available_balance, current_balance
from core.dates import month_bounds
from db.queries import (
    expenses_by_category_in_range,
    get_settings,
    list_expenses,
    list_income,
    totals_expenses,
    totals_expenses_in_range,
    totals_income,
    totals_income_in_range,
)

st.set_page_config(page_title="Reports", page_icon="📊", layout="wide")

st.title("📊 Reports")

settings = get_settings()
month_start, next_month_start = month_bounds(date.today())

income_total = totals_income()
expense_total = totals_expenses()
current = current_balance(settings.initial_balance, income_total, expense_total)
available = available_balance(current, settings.reserve_amount)
spent_month = totals_expenses_in_range(month_start, next_month_start)
earned_month = totals_income_in_range(month_start, next_month_start)

render_metrics(current, available, spent_month, earned_month)

st.subheader("Monthly category breakdown")
category_totals = expenses_by_category_in_range(month_start, next_month_start)
if category_totals:
    category_df = pd.DataFrame(category_totals, columns=["category", "total"])
    st.dataframe(category_df, use_container_width=True)
else:
    st.info("No expenses this month.")

st.subheader("Transaction filter")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start date", value=month_start)
with col2:
    end_date = st.date_input("End date", value=date.today())

st.markdown("### Expenses in range")
expenses = list_expenses(start_date=start_date, end_date=end_date)
if expenses:
    st.dataframe(pd.DataFrame([asdict(item) for item in expenses]), use_container_width=True)
else:
    st.info("No expenses in this range.")

st.markdown("### Income in range")
income = list_income(start_date=start_date, end_date=end_date)
if income:
    st.dataframe(pd.DataFrame([asdict(item) for item in income]), use_container_width=True)
else:
    st.info("No income in this range.")
