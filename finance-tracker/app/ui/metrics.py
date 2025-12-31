from __future__ import annotations

import streamlit as st


def render_metrics(current_balance: float, available_balance: float, spent: float, earned: float) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current balance", f"${current_balance:,.2f}")
    col2.metric("Available", f"${available_balance:,.2f}")
    col3.metric("Spent this month", f"${spent:,.2f}")
    col4.metric("Earned this month", f"${earned:,.2f}")
