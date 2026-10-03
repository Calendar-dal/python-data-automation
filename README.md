# Python Data Automation

Automates repetitive CSV cleanup and Excel delivery work in one command.

**Problem → Solution → Result:** Manually combining recurring exports is slow and error-prone. This tool validates compatible CSV files, merges and cleans them, then produces ready-to-use CSV and Excel files with an audit-friendly summary.

## Problem

Small teams often receive monthly or departmental CSV exports that must be checked, combined, deduplicated, cleaned, sorted, and delivered as Excel workbooks.

## Solution

The command-line workflow processes every CSV in an input directory and reports exactly how many files, rows, duplicates, and missing cells it handled.

## Features

- Batch loading with column-structure validation
- Clear errors for empty folders, malformed CSV files, and mismatched columns
- Duplicate removal and sensible missing-value filling
- Optional sorting by any available field
- CSV and `.xlsx` output
- Automated tests for the core workflow

## Tech Stack

Python 3.11+, pandas, openpyxl, pytest

## Project Structure

```text
python-data-automation/
├── input/              # Place working CSV files here
├── output/             # Generated files
├── sample_data/        # Four demonstration CSV files
├── src/main.py
├── tests/
├── requirements.txt
└── README.md
```

## Quick Start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python src/main.py --input-dir sample_data --output-dir output --sort-by order_date
```

Run the tests with `python -m pytest`.

## Example

```text
Processing complete
Input files: 4
Original rows: 12
Duplicate rows removed: 2
Missing values filled: 4
Final rows: 10
CSV output: output\cleaned_data.csv
Excel output: output\cleaned_data.xlsx
```

The included sample data represents customer orders. Text gaps become `Unknown`; numeric gaps use the column median.

## Use Cases

- Batch CSV processing
- Excel automation and recurring reports
- Data cleaning before import into another system
- Small-business back-office automation

## Possible Extensions

- Configurable column-specific cleanup rules
- Scheduled folder processing
- Summary sheets and charts in the Excel output
