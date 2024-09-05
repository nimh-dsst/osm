import asyncio

import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

from web.api.main import app as fastapi_app

db_uri = "mongodb://localhost:27017"


@pytest_asyncio.fixture(scope="function")
async def mongodb_client():
    client = AsyncIOMotorClient(db_uri)
    yield client
    client.close()


@pytest_asyncio.fixture(scope="function")
async def db(mongodb_client):
    database = mongodb_client.get_database("osm")
    asyncio.run(database.invocations.estimated_document_count())
    yield database
    # Clean up the database after each test
    collections = await database.list_collection_names()
    for collection in collections:
        await database[collection].delete_many({})


@pytest_asyncio.fixture(scope="function")
async def app():
    async with LifespanManager(fastapi_app) as manager:
        yield manager.app


@pytest_asyncio.fixture(scope="function")
async def client(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        yield client


def pytest_exception_interact(node, call, report):
    error_class = call.excinfo.type
    is_mongo_issue = issubclass(error_class, ServerSelectionTimeoutError)
    if is_mongo_issue:
        pytest.exit(
            "Failed to connect to MongoDB, check the container locally, or your IP for remote connection.",
            1,
        )
