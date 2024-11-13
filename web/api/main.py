"""
Sets up a web API for uploading osm metrics to a centralized database
"""

import os

import motor.motor_asyncio
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from odmantic import AIOEngine, ObjectId
from pydantic import BaseModel

from osm.schemas import Invocation, PayloadError, Quarantine

app = FastAPI()
dburi = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(dburi)
engine = AIOEngine(client=client, database="osm")


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")


@app.put("/upload/", response_model=Invocation)
async def upload_invocation(invocation: Invocation):
    await engine.save(invocation)
    return invocation


@app.put("/payload_error/", response_model=PayloadError)
async def upload_failed_payload_construction(payload_error: PayloadError):
    await engine.save(payload_error)
    return payload_error


@app.put("/quarantine/", response_model=Quarantine)
async def upload_failed_invocation(quarantine: Quarantine):
    await engine.save(quarantine)
    return quarantine


@app.put("/quarantine2/")
async def upload_failed_quarantine(
    file: UploadFile = File(...), error_message: str = Form(...)
):
    await engine.save(Quarantine(payload=file.file.read(), error_message=error_message))
    return JSONResponse(content={"message": "Success"}, status_code=200)


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
        loop=loop,
        log_config=LOGGING_CONFIG,
    )
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())
