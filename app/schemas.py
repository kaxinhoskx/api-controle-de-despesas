"""Schemas: definem o formato dos dados que entram e saem da API."""

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field


# ---------- Usuários e autenticação ----------
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=64)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Gastos ----------
class ExpenseCreate(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    amount: float = Field(gt=0, description="Valor do gasto (maior que zero)")
    category: str = Field(min_length=1, max_length=50)
    date: dt.date = Field(default_factory=dt.date.today)


class ExpenseUpdate(BaseModel):
    """Todos os campos são opcionais: só o que for enviado será alterado."""

    description: str | None = Field(default=None, min_length=1, max_length=200)
    amount: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    date: dt.date | None = None


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    amount: float
    category: str
    date: dt.date


class SummaryOut(BaseModel):
    total: float
    by_category: dict[str, float]
