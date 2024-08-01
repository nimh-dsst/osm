import re
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from pydantic import ValidationError
from typing import List
import requests
import pandas as pd
import tempfile
import os
from osm.schemas import Work, Client, Invocation
import pytest
import asyncio
from requests.models import Response


class DataConverter:

    def __init__(self, path_to_file):
        self.data_path = path_to_file

    def read_data(self):
        try:
            if self.data_path.startswith("https"):
                csv = download_csv(self.data_path)
                df = pd.read_csv(csv)
            else:
                df = pd.read_feather(self.data_path)
            return df
        except FileNotFoundError as e:
            raise e

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Implement data cleaning logic here
            # Handle missing values, data type conversions, etc.
            # ...
            return df
        except Exception as e:
            print(f"Failed to clean data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame in case of failure

    def transform_data(self, df: pd.DataFrame) -> List[Invocation]:
        invocations = []
        for index, row in df.iterrows():
            try:
                work = Work(
                    user_defined_id="user_defined_id",  # no mapping
                    pmid=str(row["pmid"]),
                    doi=str(row["doi"]),
                    openalex_id=None,
                    scopus_id=None,
                    filename=row["filename"],
                    file="file",  # no mapping
                    content_hash="content_hash",  # no mapping
                )
                client = Client(
                    compute_context_id=0,  # no mapping
                    email="test@gmail.com"  # no mapping
                )

                metrics = {
                    "article": "tmph81dyo65",  # no mapping
                    "pmid": row["pmid"],
                    "is_coi_pred": row["is_coi_pred"],
                    "coi_text": row["coi_text"],
                    # not sure of mapping
                    "is_funded_pred": row["is_fund_pred"],
                    "funding_text": row["fund_text"],  # not sure of mapping
                    "support_1": row["support_1"],
                    "support_3": row["support_3"],
                    "support_4": row["support_4"],
                    "support_5": row["support_5"],
                    "support_6": row["support_6"],
                    "support_7": row["support_7"],
                    "support_8": row["support_8"],
                    "support_9": row["support_9"],
                    "support_10": row["support_10"],
                    "developed_1": row["developed_1"],
                    "received_1": row["received_1"],
                    "received_2": row["received_2"],
                    "recipient_1": row["recipient_1"],
                    "authors_1": row["authors_1"],
                    "authors_2": row["authors_2"],
                    "thank_1": row["thank_1"],
                    "thank_2": row["thank_2"],
                    "fund_1": row["fund_1"],
                    "fund_2": row["fund_2"],
                    "fund_3": row["fund_3"],
                    "supported_1": row["supported_1"],
                    "financial_1": row["financial_1"],
                    "financial_2": row["financial_2"],
                    "financial_3": row["financial_3"],
                    "grant_1": row["grant_1"],
                    "french_1": row["french_1"],
                    "common_1": row["common_1"],
                    "common_2": row["common_2"],
                    "common_3": row["common_3"],
                    "common_4": row["common_4"],
                    "common_5": row["common_5"],
                    "acknow_1": row["acknow_1"],
                    "disclosure_1": row["disclosure_1"],
                    "disclosure_2": row["disclosure_2"],
                    "is_register_pred": row["is_register_pred"],
                    "register_text": row["register_text"],
                    "is_relevant": False,  # no mapping
                    "is_method": row["is_method"],
                    "is_NCT": row["is_NCT"],
                    "is_explicit": -2147483648  # no mapping
                }

                invocation = Invocation(
                    metrics=metrics,
                    osm_version="0.1",  # no mapping
                    client=client,
                    work=work,
                    user_comment="user_comment"  # no mapping
                )
                invocations.append(invocation)
            except (KeyError, ValidationError) as e:
                # Optionally, you can differentiate the errors if needed
                if isinstance(e, KeyError):
                    raise KeyError(f"Error key not found in row {index}: {e}")
                elif isinstance(e, ValidationError):
                    raise e

        return invocations


async def upload_data(invocation: List[Invocation], mongo_uri: str, db_name: str):
    motor_client = AsyncIOMotorClient(mongo_uri)
    try:
        engine = AIOEngine(client=motor_client, database=db_name)
        await engine.save_all(invocation)
        return {
            "message": "upload successful"
        }
    except Exception as e:
        raise Exception(f"Failed to upload data: {e}")
    finally:
        motor_client.close()


def download_csv(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            temp_file, temp_file_path = tempfile.mkstemp(suffix='.csv')
            os.close(temp_file)  # Close the file descriptor
            with open(temp_file_path, 'wb') as file:
                file.write(response.content)
            return temp_file_path
        else:
            raise Exception(f"Failed to download CSV. Status code: {response.status_code}")
    except Exception as e:
        raise e


def main():
    converter = DataConverter(path_to_file="all_indicators.feather")
    try:
        df = converter.read_data()
        if not df.empty:
            invocations = converter.transform_data(df)
            res = asyncio.run(upload_data(
                invocations, "mongodb_uri", "db_name"))
            print(res)
        else:
            raise Exception("Dataframe is empy")
    except Exception as e:
        print(f"Failed to process data: {e}")


if __name__ == "__main__":
    main()

invocations_row = [{
    "article": "tmph81dyo65",
    "pmid": "/tmp/tmph81dyo65.xml",
    "is_coi_pred": False,
    "coi_text": "",
    "is_funded_pred": True,
    "fund_text": "fund_text",
    "funding_text": "<TEI xmlns=\"http://www.teic.org/ns/1.0\"><teiHeader><fileDesc><titleStmt><title level=\"a\" type=\"main\" coords=\"1,84.09,72.12,427.10,30.56\">Reliability and predictability of phenotype information from functional connectivity in large imaging datasets</title>...",
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
    "is_fund_pred": True
}]

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
    "filename"
]


class MockAIOEngine:
    def __init__(self, client, database):
        self.client = client
        self.database = database

    async def save_all(self, invocation):
        pass


class MockAsyncIOMotorClient:
    def __init__(self, uri):
        self.uri = uri

    def close(self):
        pass  # Simulate closing the connection


class TestUploadData:
    @pytest.fixture
    def mock_database(self, monkeypatch, mocker):
        # Mock AsyncIOMotorClient
        monkeypatch.setattr(
            'motor.motor_asyncio.AsyncIOMotorClient', MockAsyncIOMotorClient)
        # Mock AIOEngine
        monkeypatch.setattr('odmantic.AIOEngine', MockAIOEngine)

    @pytest.fixture
    def mock_data_converter(self, mocker):
        dataframe = pd.DataFrame(invocations_row, columns=columns)

        converter = DataConverter(path_to_file="all_indicators.feather")
        data = converter.transform_data(dataframe)

        # Mock DataConverter functions
        mocker.patch.object(DataConverter, 'read_data', return_value=dataframe)
        mocker.patch.object(DataConverter, 'transform_data', return_value=data)

    @pytest.fixture
    def mock_update_data(self, mocker):
        # Mock DataConverter functions
        mocker.patch(upload_data, return_value={
                     'message': 'upload successful'})

    @pytest.fixture
    def mock_response_success(self, monkeypatch):
        def mock_get(*args, **kwargs):
            mock_resp = Response()
            mock_resp.status_code = 200
            mock_resp._content = b"column1,column2\nvalue1,value2"
            return mock_resp

        monkeypatch.setattr("requests.get", mock_get)

    @pytest.fixture
    def mock_response_failure(self, monkeypatch):
        def mock_get(*args, **kwargs):
            mock_resp = Response()
            mock_resp.status_code = 400
            mock_resp._content = "something went wrong"
            return mock_resp

        monkeypatch.setattr("requests.get", mock_get)

    @pytest.fixture
    def mock_upload_data_success(self, monkeypatch, mocker):
        async def mock_upload(*args, **kwargs):
            return {'message': 'upload successful'}

        monkeypatch.setattr("invocation_upload.upload_data",
                            mocker.AsyncMock(side_effect=mock_upload))

    def test_read_data_from_url(self, mock_response_success):
        url = "https://example.com/data.csv"
        converter = DataConverter(path_to_file=url)
        df = converter.read_data()

        # Verify the DataFrame contents
        assert not df.empty
        assert (df.columns == ["column1", "column2"]).all()
        assert df.iloc[0]["column1"] == "value1"

    def test_read_data_from_url_failure(self, mock_response_failure):
        url = "https://example.com/data.csv"
        converter = DataConverter(path_to_file=url)

        # Verify the DataFrame contents
        with pytest.raises(Exception, match="Failed to download CSV. Status code: 400"):
            converter.read_data()

    def test_read_data_from_feather(self, tmp_path):
        # Create a temporary Feather file with sample data
        df_sample = pd.DataFrame(
            {"column1": ["value1"], "column2": ["value2"]})
        feather_file = tmp_path / "all_indicators.feather"
        df_sample.to_feather(feather_file)

        converter = DataConverter(path_to_file=str(feather_file))
        df = converter.read_data()

        # Verify the DataFrame contents
        assert not df.empty
        assert (df.columns == ["column1", "column2"]).all()
        assert df.iloc[0]["column1"] == "value1"

    def test_read_data_from_feather_failure(self):
        feather_file = "data.feather"

        converter = DataConverter(path_to_file=str(feather_file))

        # Verify the DataFrame contents
        with pytest.raises(FileNotFoundError, match=re.escape(
                "[Errno 2] No such file or directory: \'data.feather\'")):
            converter.read_data()

    def test_transform_data(self):
        dataframe = pd.DataFrame(invocations_row, columns=columns)
        converter = DataConverter(path_to_file="")
        data = converter.transform_data(dataframe)

        assert len(data) == 1
        assert isinstance(data, List), "Data is not a list"
        for item in data:
            assert isinstance(
                item, Invocation), "Item in list is not an instance of Invocation"

    def test_transform_data_wrong_dataframe(self):
        df_sample = pd.DataFrame(
            {"column1": ["value1"], "column2": ["value2"]})
        converter = DataConverter(path_to_file="")

        with pytest.raises(KeyError, match="Error key not found in row 0: \'pmid\'"):
            converter.transform_data(df_sample)

    def test_transform_data_validation_error(self):
        df_sample = pd.DataFrame({"pmid": [0], "doi": [0], "filename": [0]})
        converter = DataConverter(path_to_file="")

        with pytest.raises(ValidationError, match=re.escape(
                '1 validation error for Work\nfilename\n  Input should be a valid string [type=string_type, input_value=np.int64(0), input_type=int64]\n    For further information visit https://errors.pydantic.dev/2.8/v/string_type')):
            converter.transform_data(df_sample)

    @pytest.mark.asyncio
    async def test_upload_data(self, mock_database):
        # Define test data
        invocation_list = []
        mongo_uri = "mongodb://test_uri"
        db_name = "test_db"

        # Call the function under test
        result = await upload_data(invocation_list, mongo_uri, db_name)

        # Assertions
        assert result == {'message': 'upload successful'}

    def test_main(self, mock_data_converter, mock_upload_data_success, capfd):
        main()

        # Capture the printed output
        out, err = capfd.readouterr()

        # Assert the expected output was printed
        assert "{'message': 'upload successful'}" in out
        assert not err
