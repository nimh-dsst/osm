import pandas as pd
import pyarrow as pa

from osm.schemas import schema_helpers as osh


def test_transform_data():
    # Create mock data for testing
    data = {
        "is_open_code": [False],
        "is_open_data": [True],
        "pmid": [27458207],
        "open_code_statements": [None],
        "open_data_category": ["data availability statement"],
        "open_data_statements": [
            "deposited data https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE12345"
        ],
        "funder": [["National Institutes of Health"]],  # Funder as a list of strings
    }

    # Convert the mock data to a DataFrame
    df = pd.DataFrame(data)

    # Use the existing get_table_with_schema function to create the PyArrow Table
    funder_field = pa.field("funder", pa.list_(pa.string()), nullable=True)
    table = osh.get_table_with_schema(df, [funder_field])

    # Mock parameters for the transform_data function
    kwargs = {
        "data_tags": ["bulk_upload", "NIH-IRP"],
        "user_comment": "Bulk upload of NIH-IRP data",
        "components": [{"name": "Sciencebeam parser/RTransparent", "version": "x.x.x"}],
        "custom_processing": "irp_data_processing",
    }

    # Execute the transform_data function
    results = list(osh.transform_data(table, **kwargs))

    # Check that the result is as expected
    assert len(results) == 1  # Ensure we got one transformed result

    result = results[0]

    # Check individual fields in the result
    assert result["metrics"]["is_open_code"] is False
    assert result["metrics"]["is_open_data"] is True
    assert result["metrics"]["pmid"] == 27458207
    assert result["metrics"]["open_code_statements"] is None
    assert result["metrics"]["open_data_category"] == "data availability statement"
    assert (
        result["metrics"]["open_data_statements"]
        == "deposited data https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE12345"
    )
    assert result["funder"] == [
        "National Institutes of Health"
    ]  # Ensure 'funder' is correctly handled as a list
    assert result["data_tags"] == ["bulk_upload", "NIH-IRP"]
    assert result["user_comment"] == "Bulk upload of NIH-IRP data"
    assert result["components"][0]["name"] == "Sciencebeam parser/RTransparent"
    assert result["components"][0]["version"] == "x.x.x"


# Run the test
test_transform_data()
