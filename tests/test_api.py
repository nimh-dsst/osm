import asyncio
import datetime

import nest_asyncio
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from osm.schemas import Client, Component, Invocation, Work

nest_asyncio.apply()


@pytest.fixture(scope="function")
def test_engine():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    test_db = client["test_db"].name
    engine = AIOEngine(client=client, database=test_db)
    yield engine
    engine.database.drop_collection("invocation")
    client.close()


# @pytest.mark.asyncio
def test_engine_save(test_engine):
    # Create a sample invocation object
    sample_invocation = Invocation(
        work=Work(filename="test_file"),
        client=Client(compute_context_id=1),
        osm_version="1.0.0",
        user_comment="Test comment",
        components=[Component(name="TestComponent", version="1.0")],
        funder=["Test Funder"],
        data_tags=["test_tag"],
        created_at=datetime.datetime.now(datetime.UTC).replace(microsecond=0),
    )

    # Save the sample invocation to the database
    asyncio.run(test_engine.save(sample_invocation))

    # Retrieve the saved invocation to verify it was saved correctly
    saved_invocation = test_engine.find_one(
        Invocation, Invocation.id == sample_invocation.id
    )
    assert saved_invocation is not None, "Saved invocation not found"
    assert saved_invocation.id == sample_invocation.id, "IDs do not match"

    # Retrieve the saved invocation to verify it was saved correctly
    saved_invocation = test_engine.find_one(
        Invocation, Invocation.id == sample_invocation.id
    )
    assert saved_invocation is not None, "Saved invocation not found"
    assert saved_invocation.id == sample_invocation.id, "IDs do not match"
    assert (
        saved_invocation.work.filename == sample_invocation.work.filename
    ), "Work data does not match"
    assert (
        saved_invocation.client.compute_context_id
        == sample_invocation.client.compute_context_id
    ), "Client data does not match"
    assert (
        saved_invocation.osm_version == sample_invocation.osm_version
    ), "OSM version does not match"
    assert (
        saved_invocation.user_comment == sample_invocation.user_comment
    ), "User comment does not match"
    assert (
        saved_invocation.components[0].name == sample_invocation.components[0].name
    ), "Component name does not match"
    assert (
        saved_invocation.components[0].version
        == sample_invocation.components[0].version
    ), "Component version does not match"
    assert saved_invocation.funder == sample_invocation.funder, "Funder does not match"
    assert (
        saved_invocation.data_tags == sample_invocation.data_tags
    ), "Data tags do not match"
    assert (
        saved_invocation.created_at == sample_invocation.created_at
    ), "Created at does not match"
