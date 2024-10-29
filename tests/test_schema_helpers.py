import pandas as pd
import pyarrow as pa

from osm._utils import camel_to_snake
from osm.schemas import RtransparentMetrics
from osm.schemas import schema_helpers as osh


def test_transform_data():
    # Create mock data for testing
    schema_name = "RtransparentMetrics"
    schema_field = camel_to_snake(schema_name)
    data = {
        "pmid": [27458207],
        "funder": [["National Institutes of Health"]],  # Funder as a list of strings
        "is_open_data": [True],
        "is_open_code": [False],
    }

    # Convert the mock data to a DataFrame
    df = pd.DataFrame(data)

    # Use the existing get_table_with_schema function to create the PyArrow Table
    funder_field = pa.field("funder", pa.list_(pa.string()), nullable=True)
    table = osh.get_table_with_schema(
        df, schema_name=schema_name, other_fields=[funder_field]
    )

    # Mock parameters for the transform_data function
    kwargs = {
        "data_tags": ["bulk_upload", "NIH-IRP"],
        "user_comment": "Bulk upload of NIH-IRP data",
        "components": [{"name": "Sciencebeam parser/RTransparent", "version": "x.x.x"}],
        "custom_processing": "irp_data_processing",
    }

    # Execute the transform_data function
    results = list(
        osh.transform_data(table, metrics_schema=RtransparentMetrics, **kwargs)
    )

    # Check that the result is as expected
    assert len(results) == 1  # Ensure we got one transformed result

    result = results[0]

    # Check individual fields in the result
    assert result[schema_field]["is_open_code"] is False
    assert result[schema_field]["is_open_data"] is True
    assert result[schema_field]["pmid"] == 27458207
    assert result[schema_field]["open_code_statements"] is None
    assert result["funder"] == [
        "National Institutes of Health"
    ]  # Ensure 'funder' is correctly handled as a list
    assert result["data_tags"] == ["bulk_upload", "NIH-IRP"]
    assert result["user_comment"] == "Bulk upload of NIH-IRP data"
    assert result["components"][0]["name"] == "Sciencebeam parser/RTransparent"
    assert result["components"][0]["version"] == "x.x.x"
