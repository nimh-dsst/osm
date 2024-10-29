import asyncio
import datetime

import nest_asyncio
import pytest
from bson import ObjectId

from osm.schemas import Invocation

nest_asyncio.apply()
SIMPLE_DOC = {"work": {}, "client": {"compute_context_id": 1}}

SAMPLE_DOC = {
    "work": {"filename": "test_file"},
    "client": {"compute_context_id": 1},
    "osm_version": "1.0.0",
    "user_comment": "Test comment",
    "components": [
        {"name": "TestComponent", "version": "1.0", "sample": "bG9uZyB0ZXh0"}
    ],
    "funder": ["Test Funder"],
    "rtransparent_metrics": {
        "is_open_code": True,
        "is_open_data": False,
        "funding_text": "long text",
    },
    "data_tags": ["test_tag"],
    "created_at": datetime.datetime.now(datetime.UTC)
    .replace(microsecond=0)
    .isoformat(),
}


@pytest.mark.asyncio
async def test_upload_path(client, db):
    # from requests import post
    # response = post("/upload/", json=SAMPLE_DOC.model_dump(mode="json", exclude_none=True))
    # breakpoint()
    response = asyncio.run(
        client.post(
            "/upload/",
            json=SAMPLE_DOC,
        )
    )
    assert response.status_code == 201, response.text

    # Retrieve the saved invocation to verify it was saved correctly
    record = asyncio.run(
        db.invocations.find_one({"_id": ObjectId(response.json()["id"])})
    )
    breakpoint()
    assert record is not None, "Saved invocation not found"
    saved_invocation = Invocation(**record)
    assert saved_invocation.id is not None, "IDs should be created automatically"
    breakpoint()
    assert isinstance(saved_invocation.id, str), "ID should be a string"
    assert (
        saved_invocation.work.filename == SAMPLE_DOC.work.filename
    ), "Work data does not match"
    assert (
        saved_invocation.client.compute_context_id
        == SAMPLE_DOC.client.compute_context_id
    ), "Client data does not match"
    assert (
        saved_invocation.osm_version == SAMPLE_DOC.osm_version
    ), "OSM version does not match"
    assert (
        saved_invocation.user_comment == SAMPLE_DOC.user_comment
    ), "User comment does not match"
    assert (
        saved_invocation.components[0].name == SAMPLE_DOC.components[0].name
    ), "Component name does not match"
    assert (
        saved_invocation.components[0].version == SAMPLE_DOC.components[0].version
    ), "Component version does not match"
    assert saved_invocation.funder == SAMPLE_DOC.funder, "Funder does not match"
    assert saved_invocation.data_tags == SAMPLE_DOC.data_tags, "Data tags do not match"
    # TODO: fix tzinfo issue

    assert (
        saved_invocation.created_at == SAMPLE_DOC.created_at
    ), "Created at does not match"


@pytest.mark.parametrize("doc", [SIMPLE_DOC, SAMPLE_DOC])
@pytest.mark.asyncio
async def test_db_upload(db, doc):
    res = asyncio.run(db.invocations.insert_one(doc))
    saved_inv = asyncio.run(db.invocations.find_one({"_id": res.inserted_id}))
    assert saved_inv is not None
    assert saved_inv["client"]["compute_context_id"] == 1


@pytest.mark.asyncio
async def test_swagger_ui(client):
    response = await client.get("/docs")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "swagger-ui-dist" in response.text
    assert (
        "oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect'"
        in response.text
    )
