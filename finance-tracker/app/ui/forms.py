from __future__ import annotations

from datetime import date
from typing import Optional

import streamlit as st

from core.models import Expense, Income, Settings


def expense_form(default_date: Optional[date] = None) -> Optional[Expense]:
    """Render an expense form and return an Expense when submitted."""
    with st.form("expense_form", clear_on_submit=True):
        name = st.text_input("Expense name")
        amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
        expense_date = st.date_input("Date", value=default_date or date.today())
        category = st.text_input("Category (optional)")
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Add expense")

    if submitted and name:
        return Expense(
            id=None,
            name=name,
            amount=amount,
            date=expense_date,
            category=category or None,
            notes=notes or None,
        )
    if submitted:
        st.warning("Please provide an expense name.")
    return None


def income_form(default_date: Optional[date] = None) -> Optional[Income]:
    """Render an income form and return an Income when submitted."""
    with st.form("income_form", clear_on_submit=True):
        name = st.text_input("Income name")
        amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
        income_date = st.date_input("Date", value=default_date or date.today())
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Add income")

    if submitted and name:
        return Income(id=None, name=name, amount=amount, date=income_date, notes=notes or None)
    if submitted:
        st.warning("Please provide an income name.")
    return None


def settings_form(settings: Settings) -> Optional[Settings]:
    """Render settings form and return Settings when submitted."""
    with st.form("settings_form"):
        initial_balance = st.number_input(
            "Initial balance", min_value=0.0, step=0.01, format="%.2f", value=settings.initial_balance
        )
        reserve_amount = st.number_input(
            "Reserve amount", min_value=0.0, step=0.01, format="%.2f", value=settings.reserve_amount
        )
        submitted = st.form_submit_button("Save settings")

    if submitted:
        return Settings(initial_balance=initial_balance, reserve_amount=reserve_amount)
    return None
