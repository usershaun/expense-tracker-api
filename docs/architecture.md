# Architecture

## Request flow

```
HTTP request
  -> Pydantic schema (validates body / query parameters)
  -> router function (app/routers/*.py)
  -> SQLAlchemy session (from get_db)
  -> SQLite
```

Validation failures never reach the router function: FastAPI returns a 422 first. Everything after that point is ordinary Python calling the database.

## Data model

```
categories                 expenses
----------                 --------
id (PK)        <----+      id (PK)
name (UNIQUE)       +----  category_id (FK -> categories.id)
                           amount_cents (integer)
                           description
                           spent_on (date, indexed)
```

An expense belongs to exactly one category. `spent_on` is indexed because almost every query filters or sorts by date.

## Money

The database stores `amount_cents` as an integer. The API accepts and returns decimal strings such as `"12.50"`. Conversion happens in two places only, both in `app/routers/expenses.py`:

- `to_cents` (request to database)
- `to_read_model` (database to response), which also forces two decimal places so `1250` always returns as `"12.50"`

The summaries router has its own `cents_to_decimal` for the same conversion on summed values.

## Sessions and dependencies

`get_db` in `app/database.py` opens one session per request and closes it after the response, even if the endpoint raises. Endpoints receive it with `Depends(get_db)`.

The engine registers a connect listener that runs `PRAGMA foreign_keys=ON`, because SQLite does not enforce foreign keys by default.

## Summaries

Both summary endpoints use one shared function, `category_totals`, in `app/routers/summaries.py`. It joins `categories` to `expenses`, groups by category, and lets SQL do the `SUM` and `COUNT`. Because amounts are integer cents, the SQL sum is exact. The overall total is computed by adding the per-category totals, so the two can never disagree.

The monthly endpoint turns `(year, month)` into inclusive start and end dates with `calendar.monthrange`, which handles month lengths and leap years.

## Testing

`tests/conftest.py` builds a fresh in-memory SQLite database for every test and overrides `get_db` so the app uses it. The test database enables foreign keys the same way the real one does; without that, the "category in use" test would pass or fail for the wrong reason.