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
from fastapi import FastAPI
from odmantic import AIOEngine

from osm.schemas import Invocation

app = FastAPI()

client = motor.motor_asyncio.AsyncIOMotorClient(
    os.environ.get(
        "MONGODB_URI",
        "mongodb+srv://johnlee:<password>@cluster0.6xo8ws7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    )
)
engine = AIOEngine(client=client, database="test")


@app.put("/upload/", response_model=Invocation)
async def upload_invocation(invocation: Invocation):
    await engine.save(
        invocation
    )  # Save single invocation instance instead of using save_all
    return invocation
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
