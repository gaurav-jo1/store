"""Pytest configuration file."""

import logging
import os
from typing import AsyncGenerator, Generator, cast

import pytest
from _pytest.python import Function
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from httpx._transports.asgi import _ASGIApp
from moto.server import ThreadedMotoServer
from pytest_mock.plugin import AsyncMockType, MockerFixture, MockType

os.environ["ENVIRONMENT"] = "local"


def pytest_collection_modifyitems(items: list[Function]) -> None:
    items.sort(key=lambda x: x.get_closest_marker("slow") is not None)


@pytest.fixture(autouse=True)
def mock_aws() -> Generator[None, None, None]:
    server: ThreadedMotoServer | None = None

    # logging.getLogger("botocore").setLevel(logging.DEBUG)
    logging.getLogger("botocore").setLevel(logging.WARN)

    try:
        # Starts a local AWS server.
        server = ThreadedMotoServer(port=0)
        server.start()
        host, port = server.get_host_and_port()
        endpoint = f"http://{host}:{port}"
        os.environ["AWS_ENDPOINT_URL"] = endpoint
        os.environ["AWS_ENDPOINT_URL_DYNAMODB"] = endpoint
        os.environ["AWS_ENDPOINT_URL_S3"] = endpoint

        yield

    finally:
        if server is not None:
            server.stop()


@pytest.fixture()
async def app_client() -> AsyncGenerator[AsyncClient, None]:
    from www.main import app

    transport = ASGITransport(cast(_ASGIApp, app))

    async with AsyncClient(transport=transport, base_url="http://test") as app_client:
        yield app_client


@pytest.fixture()
def test_client() -> Generator[TestClient, None, None]:

    from www.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def mock_send_email(mocker: MockerFixture) -> MockType:
    mock = mocker.patch("www.utils.email.send_email")
    mock.return_value = None
    return mock


@pytest.fixture(autouse=True)
def mock_get_user(mocker: MockerFixture) -> AsyncMockType:
    mock = mocker.patch("www.auth._decode_user_from_token")

    from www.auth import User

    mock.return_value = User(
        id="test_user",
        is_admin=True,
        can_upload=True,
        can_test=True,
    )
    return mock


@pytest.fixture(autouse=True)
def mock_get_user_info(mocker: MockerFixture) -> AsyncMockType:
    mock = mocker.patch("www.auth._decode_user_info_from_token")

    from www.auth import UserInfo

    mock.return_value = UserInfo(
        email="test@example.com",
        email_verified=True,
    )
    return mock
