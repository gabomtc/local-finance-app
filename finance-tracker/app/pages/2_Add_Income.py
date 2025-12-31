from __future__ import annotations

from dataclasses import asdict

import pandas as pd
import streamlit as st

from app.ui.forms import income_form
from db.queries import insert_income, list_income

st.set_page_config(page_title="Add Income", page_icon="💵", layout="wide")

st.title("💵 Add Income")

income = income_form()
if income:
    insert_income(income)
    st.success("Income added.")

st.subheader("Latest income")
income_rows = list_income(limit=20)
if income_rows:
    st.dataframe(pd.DataFrame([asdict(item) for item in income_rows]), use_container_width=True)
else:
    st.info("No income recorded yet.")
