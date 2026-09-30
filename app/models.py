from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount_cents: Mapped[int]
    description: Mapped[str] = mapped_column(String(200))
    spent_on: Mapped[date] = mapped_column(index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))