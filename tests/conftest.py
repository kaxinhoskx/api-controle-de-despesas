import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    """Cliente de teste com um banco SQLite em memória, limpo a cada teste."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def make_headers(client):
    """Cria um usuário, faz login e devolve o cabeçalho de autorização."""

    def _make(username="ana", password="senha123"):
        client.post("/auth/register", json={"username": username, "password": password})
        response = client.post(
            "/auth/login", data={"username": username, "password": password}
        )
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _make
