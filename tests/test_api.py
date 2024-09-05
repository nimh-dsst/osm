import asyncio
import datetime

import nest_asyncio
import pytest

from osm.schemas import Client, Component, Invocation, RtransparentMetrics, Work

nest_asyncio.apply()
SIMPLE_INV = Invocation(
    work=Work(),
    client=Client(compute_context_id=1),
)
SAMPLE_INV = Invocation(
    work=Work(filename="test_file"),
    client=Client(compute_context_id="1"),
    osm_version="1.0.0",
    user_comment="Test comment",
    components=[Component(name="TestComponent", version="1.0", sample=b"long text")],
    funder=["Test Funder"],
    rtransparent_metrics=RtransparentMetrics(
        is_open_code=True, is_open_data=False, funding_text="long text"
    ),
    data_tags=["test_tag"],
    created_at=datetime.datetime.now(datetime.UTC).replace(microsecond=0),
)


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


@pytest.mark.parametrize("_", [x for x in range(3)])
@pytest.mark.asyncio
async def test_db_upload(db, _):
    asyncio.run(db.invocations.insert_one(SIMPLE_INV.model_dump(mode="json")))
    saved_inv = asyncio.run(db.invocations.find_one())
    assert saved_inv is not None
    assert saved_inv["client"]["compute_context_id"] == 1


@pytest.mark.asyncio
async def test_upload_path(client, db):
    response = asyncio.run(
        client.put(
            "/upload/",
            json=SAMPLE_INV.model_dump(mode="json", exclude_none=True),
        )
    )

    assert response.status_code == 200, response.text

    # Retrieve the saved invocation to verify it was saved correctly
    saved_invocation = asyncio.run(db.invocations.find_one())
    assert saved_invocation is not None, "Saved invocation not found"
    assert saved_invocation["id"] == SAMPLE_INV.id, "IDs do not match"
    assert (
        saved_invocation["work"]["filename"] == SAMPLE_INV.work.filename
    ), "Work data does not match"
    assert (
        saved_invocation["client"]["compute_context_id"]
        == SAMPLE_INV.client.compute_context_id
    ), "Client data does not match"
    assert (
        saved_invocation["osm_version"] == SAMPLE_INV.osm_version
    ), "OSM version does not match"
    assert (
        saved_invocation["user_comment"] == SAMPLE_INV.user_comment
    ), "User comment does not match"
    assert (
        saved_invocation["components"][0]["name"] == SAMPLE_INV.components[0].name
    ), "Component name does not match"
    assert (
        saved_invocation["components"][0]["version"] == SAMPLE_INV.components[0].version
    ), "Component version does not match"
    assert saved_invocation["funder"] == SAMPLE_INV.funder, "Funder does not match"
    assert (
        saved_invocation["data_tags"] == SAMPLE_INV.data_tags
    ), "Data tags do not match"
    # TODO: fix tzinfo issue
    # assert saved_invocation["created_at"] == SAMPLE_INV.created_at, "Created at does not match"
