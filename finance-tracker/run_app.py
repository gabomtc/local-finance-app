#!/usr/bin/env python
from __future__ import annotations

import sys

from streamlit.web import cli as stcli


if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "app/main.py"]
    stcli.main()
