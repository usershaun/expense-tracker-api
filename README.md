# Expense Tracker API

A REST API for recording personal expenses and summarising them by month and category.

## Problem

Spreadsheets work for tracking spending but are hard to query, validate and automate. This API stores expenses in a database with enforced rules (positive amounts, valid dates, existing categories) and exposes endpoints for filtering and summarising them.

## Features

- Create, read, update and delete expenses
- Create, list and delete categories (names are unique; a category that still has expenses cannot be deleted)
- List expenses filtered by date range and category, newest first, with limit/offset pagination
- Monthly summary: total, count and per-category breakdown
- Spending per category over an optional date range
- Input validation and consistent status codes (404, 409, 422)
- Interactive API documentation at `/docs`
- Automated tests (pytest)

## Tech Stack

- Python, FastAPI, Uvicorn
- SQLite with SQLAlchemy (ORM)
- Pydantic and pydantic-settings
- pytest for tests, Ruff for linting

## Setup

Requires Python 3.10 or newer.

```bash
git clone <repository-url>
cd expense-tracker-api
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install dependencies and start the server:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` for the interactive documentation.

The database is a SQLite file (`expenses.db`) created on first start. To change its location, copy `.env.example` to `.env` and edit `DATABASE_URL`.

## Usage

Create a category, then an expense in it:

```
POST /categories
{"name": "Food"}

POST /expenses
{"amount": "12.50", "description": "Lunch", "spent_on": "2026-09-30", "category_id": 1}
```

Query expenses and summaries:

```
GET /expenses?start=2026-09-01&end=2026-09-30&category_id=1&limit=20&o