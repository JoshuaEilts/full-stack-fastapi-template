import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.config import settings
from app.db.session import get_session
from app.main import app
from app.models import User
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, Any, None]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(app: FastAPI, session: Session) -> Generator[FastAPI, Any, None]:
    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override
    yield app
    app.dependency_overrides.clear()


@pytest.fixture(name="app")
def app_fixture() -> FastAPI:
    return app


@pytest.fixture(name="async_client")
async def async_client_fixture(
    client: FastAPI,
) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(app=client, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(name="superuser_token_headers")
async def superuser_token_headers_fixture(
    async_client: AsyncClient,
) -> dict[str, str]:
    return await get_superuser_token_headers(async_client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: FastAPI, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
