"""Configuração da conexão com o banco de dados."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gastos.db")

# Alguns serviços de deploy (Render, Heroku) entregam "postgres://",
# mas o SQLAlchemy espera "postgresql://".
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# O SQLite precisa dessa opção para funcionar com o FastAPI.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Classe base de todos os modelos (tabelas)."""


def get_db():
    """Abre uma sessão do banco para cada requisição e fecha no final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
