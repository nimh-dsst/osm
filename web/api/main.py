"""
Sets up a web API for uploading osm metrics to a centralized database
"""

import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from osm import db as osm_db
from osm.schemas import Invocation, PayloadError, Quarantine


@asynccontextmanager
async def lifespan(app: FastAPI):
    await osm_db.db_init()
    yield


app = FastAPI(lifespan=lifespan)


@app.put("/upload/", response_model=Invocation)
async def upload_invocation(
    invocation: Invocation,
):
    db = osm_db.get_mongo_db()
    result = await db.invocations.insert_one(invocation.model_dump(mode="json"))
    inserted_invocation = await db.invocations.find_one({"_id": result.inserted_id})
    return Invocation(**{k: v for k, v in inserted_invocation.items() if k != "id"})


@app.put("/payload_error/", response_model=PayloadError)
async def upload_failed_payload_construction(payload_error: PayloadError):
    db = osm_db.get_mongo_db()
    result = await db.payload_errors.insert_one(payload_error.model_dump(mode="json"))
    inserted_payload_error = await db.payload_errors.find_one(
        {"_id": result.inserted_id}
    )
    return PayloadError(
        **{k: v for k, v in inserted_payload_error.items() if k != "id"}
    )


@app.put("/quarantine/", response_model=Quarantine)
async def upload_failed_invocation(quarantine: Quarantine):
    db = osm_db.get_mongo_db()
    result = await db.quarantines.insert_one(quarantine.model_dump(mode="json"))
    inserted_quarantine = await db.quarantines.find_one({"_id": result.inserted_id})
    return Quarantine(**{k: v for k, v in inserted_quarantine.items() if k != "id"})


@app.put("/quarantine2/")
async def upload_failed_quarantine(
    file: UploadFile = File(...), error_message: str = Form(...)
):
    db = osm_db.get_mongo_db()
    quarantine = Quarantine(payload=file.file.read(), error_message=error_message)
    result = await db.quarantines.insert_one(quarantine.model_dump(mode="json"))
    await db.quarantines.find_one({"_id": result.inserted_id})
    return JSONResponse(
        content={"message": "Success", "id": str(result.inserted_id)}, status_code=200
    )


@app.get("/invocations/{id}", response_model=Invocation)
async def get_invocation_by_id(id: str):
    invocation = await Invocation.find_one(id)
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
            "class": "osm.ColorStreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "TRACE"},
    },
}


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=80,
        root_path="/api",
        loop=loop,
    )
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())
