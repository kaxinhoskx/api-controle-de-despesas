"""Ponto de entrada da API."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth, expenses


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas no banco ao iniciar a aplicação.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API de Controle de Gastos",
    description="API REST para registrar e analisar gastos pessoais, "
    "com autenticação JWT.",
    version="1.0.0",
    lifespan=lifespan,
)

# Libera o acesso de um front-end (ex.: seu projeto em JS).
# Em produção, defina ALLOWED_ORIGINS com o endereço do seu site.
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(expenses.router)


@app.get("/", tags=["Status"])
def health_check():
    return {"status": "ok", "docs": "/docs"}
