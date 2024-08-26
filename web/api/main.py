"""
Sets up a web API for uploading osm metrics to a centralized database

Usage along the lines of:

curl -X POST "http://localhost:80/upload/" \
    -H "Content-Type: application/json" \
    -d '{
        "osm_version": "1.0",
        "timestamp": "2024-07-24T12:00:00Z",
        "user_comment": "example comment",
        "work": {
            "user_defined_id": "123",
            "pmid": "pmid_example",
            "file": "example_file_content_base64_encoded",
            "content_hash": "example_hash",
            "timestamp": "2024-07-24T12:00:00Z"
        }
    }'
"""

import os

import motor.motor_asyncio
from fastapi import FastAPI, HTTPException
from odmantic import AIOEngine, ObjectId

from osm.schemas import Invocation, Quarantine

app = FastAPI()
dburi = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(dburi)
engine = AIOEngine(client=client, database="test")


@app.put("/upload/", response_model=Invocation)
async def upload_invocation(invocation: Invocation):
    await engine.save(invocation)
    return invocation


@app.put("/quarantine/", response_model=Quarantine)
async def upload_failed_invocation(quarantine: Quarantine):
    await engine.save(quarantine)
    return quarantine


@app.get("/invocations/{id}", response_model=Invocation)
async def get_invocation_by_id(id: ObjectId):
    invocation = await engine.find_one(Invocation, Invocation.id == id)
    if invocation is None:
        raise HTTPException(404)
    return invocation


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "logging.Formatter",
            "fmt": "%(levelname)s %(name)s@%(lineno)d %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "my_project.ColorStreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "TRACE"},
    },
}

if __name__ == "__main__":
    import asyncio

    import uvicorn

    loop = asyncio.get_event_loop()
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=80,
        root_path="/api",
        loop=loop,
        log_config=LOGGING_CONFIG,
    )
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())
