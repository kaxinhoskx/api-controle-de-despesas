"""Rotas de gastos (todas exigem login)."""

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/expenses", tags=["Gastos"])


def _get_own_expense(expense_id: int, db: Session, user: models.User) -> models.Expense:
    """Busca um gasto do usuário logado ou devolve 404."""
    expense = db.scalar(
        select(models.Expense).where(
            models.Expense.id == expense_id, models.Expense.user_id == user.id
        )
    )
    if expense is None:
        raise HTTPException(status_code=404, detail="Gasto não encontrado")
    return expense


@router.post("", response_model=schemas.ExpenseOut, status_code=201)
def create_expense(
    data: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    expense = models.Expense(**data.model_dump(), user_id=user.id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("", response_model=list[schemas.ExpenseOut])
def list_expenses(
    category: str | None = None,
    start: dt.date | None = Query(None, description="Data inicial (AAAA-MM-DD)"),
    end: dt.date | None = Query(None, description="Data final (AAAA-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Lista os gastos do usuário, com filtros e paginação."""
    query = select(models.Expense).where(models.Expense.user_id == user.id)
    if category:
        query = query.where(models.Expense.category == category)
    if start:
        query = query.where(models.Expense.date >= start)
    if end:
        query = query.where(models.Expense.date <= end)

    query = (
        query.order_by(models.Expense.date.desc(), models.Expense.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return db.scalars(query).all()


# Esta rota precisa vir ANTES de "/{expense_id}" para não ser confundida com ela.
@router.get("/summary", response_model=schemas.SummaryOut)
def summary(
    start: dt.date | None = Query(None, description="Data inicial (AAAA-MM-DD)"),
    end: dt.date | None = Query(None, description="Data final (AAAA-MM-DD)"),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Total gasto e total por categoria no período."""
    query = select(models.Expense.category, func.sum(models.Expense.amount)).where(
        models.Expense.user_id == user.id
    )
    if start:
        query = query.where(models.Expense.date >= start)
    if end:
        query = query.where(models.Expense.date <= end)
    query = query.group_by(models.Expense.category)

    by_category = {cat: round(total, 2) for cat, total in db.execute(query).all()}
    return {"total": round(sum(by_category.values()), 2), "by_category": by_category}


@router.get("/{expense_id}", response_model=schemas.ExpenseOut)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return _get_own_expense(expense_id, db, user)


@router.patch("/{expense_id}", response_model=schemas.ExpenseOut)
def update_expense(
    expense_id: int,
    data: schemas.ExpenseUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    expense = _get_own_expense(expense_id, db, user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    expense = _get_own_expense(expense_id, db, user)
    db.delete(expense)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
