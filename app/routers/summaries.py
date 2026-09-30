import calendar
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Expense
from app.schemas import CategoryTotal, MonthlySummary

router = APIRouter(prefix="/summaries", tags=["summaries"])


def cents_to_decimal(cents: int) -> Decimal:
    return (Decimal(cents) / 100).quantize(Decimal("0.01"))


def category_totals(db: Session, start: date | None, end: date | None):
    query = (
        select(
            Category.id,
            Category.name,
            func.sum(Expense.amount_cents),
            func.count(Expense.id),
        )
        .join(Expense, Expense.category_id == Category.id)
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Expense.amount_cents).desc(), Category.name)
    )
    if start is not None:
        query = query.where(Expense.spent_on >= start)
    if end is not None:
        query = query.where(Expense.spent_on <= end)

    return [
        CategoryTotal(
            category_id=category_id,
            category_name=name,
            total=cents_to_decimal(total_cents),
            count=count,
        )
        for category_id, name, total_cents, count in db.execute(query).all()
    ]


@router.get("/monthly", response_model=MonthlySummary)
def monthly_summary(
    year: int = Query(ge=2000, le=2100),
    month: int = Query(ge=1, le=12),
    db: Session = Depends(get_db),
):
    last_day = calendar.monthrange(year, month)[1]
    by_category = category_totals(
        db, date(year, month, 1), date(year, month, last_day)
    )
    return MonthlySummary(
        year=year,
        month=month,
        total=sum((c.total for c in by_category), Decimal("0.00")),
        count=sum(c.count for c in by_category),
        by_category=by_category,
    )