import os

from motor.motor_asyncio import AsyncIOMotorClient

DB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")


async def db_init(db_uri: str = DB_URI):
    # Create Motor client
    pass
    client = get_mongo_client()
    # yield client
    # client.close()
    db = client.get_database("osm")
    return db


def get_mongo_client():
    return AsyncIOMotorClient(DB_URI)


def get_mongo_db(mongo_client: AsyncIOMotorClient | None = None):
    if mongo_client is None:
        mongo_client = get_mongo_client()
    return mongo_client.get_database("osm")


def get_mongo_session(mongo_client: AsyncIOMotorClient):
    return mongo_client.start_session()
