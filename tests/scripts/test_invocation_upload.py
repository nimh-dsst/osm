import re
from typing import List

import pandas as pd
import pytest
from pydantic import ValidationError
from requests.models import Response

from osm.schemas import Invocation
from scripts.invocation_upload import read_data, transform_data, upload_data

invocations_row = [
    {
        "article": "tmph81dyo65",
        "pmid": "/tmp/tmph81dyo65.xml",
        "is_coi_pred": False,
        "coi_text": "",
        "is_funded_pred": True,
        "fund_text": "fund_text",
        "funding_text": '<TEI xmlns="http://www.teic.org/ns/1.0"><teiHeader><fileDesc><titleStmt><title level="a" type="main" coords="1,84.09,72.12,427.10,30.56">Reliability and predictability of phenotype information from functional connectivity in large imaging datasets</title>...',
        "support_1": True,
        "support_3": True,
        "support_4": False,
        "support_5": True,
        "support_6": False,
        "support_7": False,
        "support_8": False,
        "support_9": False,
        "support_10": False,
        "developed_1": False,
        "received_1": False,
        "received_2": False,
        "recipient_1": False,
        "authors_1": False,
        "authors_2": False,
        "thank_1": False,
        "thank_2": False,
        "fund_1": False,
        "fund_2": False,
        "fund_3": False,
        "supported_1": False,
        "financial_1": False,
        "financial_2": False,
        "financial_3": False,
        "grant_1": False,
        "french_1": False,
        "common_1": False,
        "common_2": False,
        "common_3": False,
        "common_4": False,
        "common_5": False,
        "acknow_1": False,
        "disclosure_1": False,
        "disclosure_2": False,
        "is_register_pred": False,
        "register_text": "",
        "is_relevant": True,
        "is_method": False,
        "is_NCT": -2147483648,
        "is_explicit": -2147483648,
        "doi": "test",
        "filename": "test",
        "is_fund_pred": True,
    }
]

# Define the list of column names based on the keys of the metrics dictionary
columns = [
    "article",  # no mapping
    "pmid",
    "is_coi_pred",
    "coi_text",
    "is_fund_pred",
    "is_funded_pred",
    "funding_text",
    "support_1",
    "support_3",
    "support_4",
    "support_5",
    "support_6",
    "support_7",
    "support_8",
    "support_9",
    "support_10",
    "developed_1",
    "received_1",
    "received_2",
    "recipient_1",
    "fund_text",
    "authors_1",
    "authors_2",
    "thank_1",
    "thank_2",
    "fund_1",
    "fund_2",
    "fund_3",
    "supported_1",
    "financial_1",
    "financial_2",
    "financial_3",
    "grant_1",
    "french_1",
    "common_1",
    "common_2",
    "common_3",
    "common_4",
    "common_5",
    "acknow_1",
    "disclosure_1",
    "disclosure_2",
    "is_register_pred",
    "register_text",
    "is_relevant",
    "is_method",
    "is_NCT",
    "is_explicit",
    "doi",
    "filename",
]


class MockAIOEngine:
    def __init__(self, client, database):
        self.client = client
        self.database = database

    async def save_all(self, invocation):
        pass

    async def save(self, invocation):
        pass


class MockAsyncIOMotorClient:
    def __init__(self, uri):
        self.uri = uri

    def close(self):
        pass  # Simulate closing the connection


@pytest.fixture
def mock_database(monkeypatch, mocker):
    # Mock AsyncIOMotorClient
    monkeypatch.setattr(
        "motor.motor_asyncio.AsyncIOMotorClient", MockAsyncIOMotorClient
    )
    # Mock AIOEngine
    monkeypatch.setattr("odmantic.AIOEngine", MockAIOEngine)


@pytest.fixture
def mock_read_data(mocker):
    dataframe = pd.DataFrame(invocations_row, columns=columns)
    mocker.patch("scripts.invocation_upload.read_data", return_value=dataframe)


@pytest.fixture
def mock_update_data(mocker):
    # Mock DataConverter functions
    mocker.patch(upload_data, return_value={"message": "upload successful"})


@pytest.fixture
def mock_response_success(monkeypatch):
    def mock_get(*args, **kwargs):
        mock_resp = Response()
        mock_resp.status_code = 200
        mock_resp._content = b"column1,column2\nvalue1,value2"
        return mock_resp

    monkeypatch.setattr("requests.get", mock_get)


@pytest.fixture
def mock_response_failure(monkeypatch):
    def mock_get(*args, **kwargs):
        mock_resp = Response()
        mock_resp.status_code = 400
        mock_resp._content = "something went wrong"
        return mock_resp

    monkeypatch.setattr("requests.get", mock_get)


@pytest.fixture
def mock_upload_data_success(monkeypatch, mocker):
    async def mock_upload(*args, **kwargs):
        print({"message": "upload successful"})

    monkeypatch.setattr(
        "scripts.invocation_upload.upload_data",
        mocker.AsyncMock(side_effect=mock_upload),
    )


def test_read_data_from_url(mock_response_success):
    url = "https://example.com/data.csv"
    df = read_data(url)

    # Verify the DataFrame contents
    assert not df.empty
    assert (df.columns == ["column1", "column2"]).all()
    assert df.iloc[0]["column1"] == "value1"


def test_read_data_from_url_failure(mock_response_failure):
    url = "https://example.com/data.csv"

    # Verify the DataFrame contents
    with pytest.raises(Exception, match="Failed to download CSV. Status code: 400"):
        read_data(url)


def test_read_data_from_feather(tmp_path):
    # Create a temporary Feather file with sample data
    df_sample = pd.DataFrame({"column1": ["value1"], "column2": ["value2"]})
    feather_file = tmp_path / "all_indicators.feather"
    df_sample.to_feather(feather_file)

    df = read_data(str(feather_file))

    # Verify the DataFrame contents
    assert not df.empty
    assert (df.columns == ["column1", "column2"]).all()
    assert df.iloc[0]["column1"] == "value1"


def test_read_data_from_feather_failure():
    feather_file = "data.feather"

    # Verify the DataFrame contents
    with pytest.raises(
        FileNotFoundError,
        match=re.escape("[Errno 2] No such file or directory: 'data.feather'"),
    ):
        read_data(str(feather_file))


def test_transform_data():
    dataframe = pd.DataFrame(invocations_row, columns=columns)
    data = transform_data(dataframe)

    assert len(data) == 1
    assert isinstance(data, List), "Data is not a list"
    for item in data:
        assert isinstance(
            item, Invocation
        ), "Item in list is not an instance of Invocation"


def test_transform_data_wrong_dataframe():
    df_sample = pd.DataFrame({"column1": ["value1"], "column2": ["value2"]})

    with pytest.raises(KeyError, match="Error key not found in row 0: 'doi'"):
        transform_data(df_sample)


def test_transform_data_validation_error():
    df_sample = pd.DataFrame({"pmid": [0], "doi": [0], "filename": [0]})

    with pytest.raises(
        ValidationError,
        match=re.escape(
            "1 validation error for Work\nfilename\n  Input should be a valid string [type=string_type, input_value=np.int64(0), input_type=int64]\n    For further information visit https://errors.pydantic.dev/2.8/v/string_type"
        ),
    ):
        transform_data(df_sample)


@pytest.mark.asyncio
async def test_upload_data_success(mock_database):
    # Define test data
    invocation_list = []
    MONGODB_URI = "mongodb://test_uri"
    db_name = "test_db"

    # If an exception is raised in the above call, the test will fail.
    # There's no need for a 'with not pytest.raises(Exception):' block.
    await upload_data(invocation_list, MONGODB_URI, db_name, "1/2")


@pytest.mark.asyncio
async def test_upload_data_failure(mock_database, caplog):
    invocation_list = []

    with pytest.raises(TypeError, match="NoneType' object is not iterable"):
        await upload_data(invocation_list, None, None, "1/2")
