from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.routers import categories, expenses


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Expense Tracker API", lifespan=lifespan)
app.include_router(categories.router)
app.include_router(expenses.router)


@app.get("/health")
def health():
    return {"status": "ok"}