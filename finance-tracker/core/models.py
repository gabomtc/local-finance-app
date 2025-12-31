from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Expense:
    id: Optional[int]
    name: str
    amount: float
    date: date
    category: Optional[str] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class Income:
    id: Optional[int]
    name: str
    amount: float
    date: date
    notes: Optional[str] = None


@dataclass(frozen=True)
class Settings:
    initial_balance: float
    reserve_amount: float
