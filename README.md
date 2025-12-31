# Local Finance Tracker

A local personal finance tracker built with Python, Streamlit, and SQLite. Track expenses and income, view monthly reports, and export your data to CSV.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

## Run

```bash
streamlit run app/main.py
```

### Run without a Streamlit command

```bash
python run_app.py
```

On Linux Mint you can also make `run_app.py` executable and double-click it in your file manager.

## Tests

```bash
pytest
```

## Export CSV

```bash
python scripts/export_csv.py
```

Exports are written to the `exports/` directory with timestamped filenames.
