from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Expense
from app.schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate

router = APIRouter(prefix="/expenses", tags=["expenses"])


def to_cents(amount: Decimal) -> int:
    return int(amount * 100)


def to_read_model(expense: Expense) -> ExpenseRead:
    return ExpenseRead(
        id=expense.id,
                amount=(Decimal(expense.amount_cents) / 100).quantize(Decimal("0.01")),
        description=expense.description,
        spent_on=expense.spent_on,
        category_id=expense.category_id,
    )


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(data: ExpenseCreate, db: Session = Depends(get_db)):
    if db.get(Category, data.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")

    expense = Expense(
        amount_cents=to_cents(data.amount),
        description=data.description,
        spent_on=data.spent_on,
        category_id=data.category_id,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return to_read_model(expense)

@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return to_read_model(expense)

@router.put("/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: int, data: ExpenseUpdate, db: Session = Depends(get_db)
):
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    if db.get(Category, data.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")

    expense.amount_cents = to_cents(data.amount)
    expense.description = data.description
    expense.spent_on = data.spent_on
    expense.category_id = data.category_id
    db.commit()
    db.refresh(expense)
    return to_read_model(expense)