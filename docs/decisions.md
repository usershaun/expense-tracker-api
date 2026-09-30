# Decisions

Short notes on choices that could reasonably have gone another way.

## Integer cents instead of Decimal or float in the database

Floats drift (0.1 + 0.2). `Decimal` is exact in Python, but SQLite has no decimal type and would store it as a float, so SQL `SUM()` could be slightly wrong. Integer cents are exact and sum correctly in SQL.
Cost: a conversion at the API boundary, kept in two small functions.

## Categories as a table

A table with a foreign key prevents typos and makes renaming possible in one place. Cost: an extra join in summaries, and a rule that a category in use cannot be deleted (409).

## Database-level foreign key enforcement

The 409 rule does not rely only on application code. With `PRAGMA foreign_keys=ON`, the database itself refuses to delete a referenced category, and the endpoint translates that `IntegrityError` into a readable response.

## PUT for updates, not PATCH

A full replacement reuses the create validation exactly and avoids having to distinguish "field omitted" from "field set to null". Cost: clients must send every field to change one.

## Filtering returns an empty list, creating returns 404

`GET /expenses?category_id=999` returns `[]`, because "no matching expenses" is a valid answer to a question. `POST /expenses` with `category_id=999` returns 404, because the request tries to attach data to something that does not exist.

## No service layer

The plan included a `services/` folder, but each endpoint turned out short enough to stay in its router, and the only complex query is one function in `summaries.py`. Splitting it out would have added files without adding clarity. If a router outgrows this, that is where to split.

## Limit/offset pagination

It maps directly onto SQL `LIMIT` and `OFFSET`. Known weakness: rows added between requests can cause an item to appear twice or be skipped. Acceptable for a single-user app.

## Ruff configuration for FastAPI

Ruff's B008 rule flags `Depends(...)` and `Query(...)` used as default values. That is the normal way to write FastAPI endpoints, so `ruff.toml` marks those two calls as safe instead of rewriting every endpoint.

## httpx2 as the test client dependency

Starlette's `TestClient` now prefers `httpx2` (Pydantic's maintained fork of httpx) and warns when only `httpx` is installed. `requirements-dev.txt` lists `httpx2`. It is a test-only dependency.