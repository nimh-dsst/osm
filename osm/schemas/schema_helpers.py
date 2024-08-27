import logging
import os
import warnings
from collections.abc import Iterator

import pandas as pd
import pyarrow as pa
from odmantic import SyncEngine
from pydantic import ValidationError
from pymongo import MongoClient

from osm import __version__, schemas
from osm._utils import flatten_dict
from osm.schemas import Client, Invocation, Work

logger = logging.getLogger(__name__)


def rtransparent_pub_data_processing(row):
    row["is_open_code"] = row.pop("is_code_pred")
    row["is_open_data"] = row.pop("is_data_pred")
    return row


def types_mapper(pa_type):
    if pa.types.is_int64(pa_type):
        # Map pyarrow int64 to pandas Int64 (nullable integer)
        return pd.Int64Dtype()
    elif pa.types.is_float64(pa_type):
        # Map pyarrow float64 to pandas Float64 (nullable float)
        return pd.Float64Dtype()
    elif pa.types.is_string(pa_type):
        # Map pyarrow string to pandas String (nullable string)
        return pd.StringDtype()
    else:
        return None


def odmantic_to_pyarrow(schema_dict):
    type_mapping = {
        "integer": pa.int64(),
        "number": pa.float64(),
        "string": pa.string(),
        "boolean": pa.bool_(),
        # We will handle None manually
        "null": pa.string(),
        "array": pa.list_(pa.string()),
        "object": pa.struct([]),
    }

    fields = []
    for prop, details in schema_dict["properties"].items():
        primary_type = "string"
        nullable = False

        if "anyOf" in details:
            primary_type = next(
                (t["type"] for t in details["anyOf"] if t["type"] != "null"), "string"
            )
            nullable = True
        else:
            primary_type = details.get("type", "string")

        pyarrow_type = type_mapping.get(primary_type, pa.string())
        fields.append(pa.field(prop, pyarrow_type, nullable=nullable))
    return pa.schema(fields)


def get_pyarrow_schema(metrics_schema="RtransparentMetrics"):
    odmantic_schema_json = getattr(schemas, metrics_schema).model_json_schema()
    pyarrow_schema = odmantic_to_pyarrow(odmantic_schema_json)
    return pyarrow_schema


def get_table_with_schema(
    df, other_fields=None, raise_error=True, metrics_schema="RtransparentMetrics"
):
    other_fields = other_fields or []
    pyarrow_schema = get_pyarrow_schema(metrics_schema)
    adjusted_schema = adjust_schema_to_dataframe(
        pyarrow_schema, df, other_fields=other_fields
    )

    # Find columns in the DataFrame that are not included in the adjusted schema
    missing_columns = set(df.columns) - set(adjusted_schema.names)

    if missing_columns:
        if raise_error:
            raise ValueError(
                f"The following columns are present in the DataFrame but are not included in the schema: {', '.join(missing_columns)}"
            )
        else:
            warnings.warn(
                f"The following columns are present in the DataFrame but will be dropped due to schema mismatch: {', '.join(missing_columns)}"
            )

    # Convert DataFrame to PyArrow Table with the adjusted schema
    return pa.Table.from_pandas(df, schema=adjusted_schema)


def adjust_schema_to_dataframe(schema, df, other_fields: list = None):
    fields = [field for field in schema if field.name in df.columns]

    if other_fields is not None:
        for f in other_fields:
            fields.append(f)

    return pa.schema(fields)


def transform_data(
    table: pa.Table, *, metrics_schema, raise_error=True, **kwargs
) -> Iterator[dict]:
    """
    Process each row in a PyArrow Table in a memory-efficient way and yield JSON payloads.
    """
    # Iterate over the table in batches
    for batch in table.to_batches(max_chunksize=500):
        # Convert the batch to a list of dictionaries (one row at a time)
        for row in batch.to_pylist():
            try:
                # Process each row using the existing get_invocation logic
                invocation = get_invocation(row, metrics_schema, **kwargs)
                yield invocation.model_dump(mode="json", exclude="id")
            except (KeyError, ValidationError) as e:
                if raise_error:
                    logger.error(f"Error processing row: {row}")
                    raise e
                logger.error(f"Skipping row due to error: {e}")
                continue


def get_invocation(row, metrics_schema, **kwargs):
    kwargs["data_tags"] = kwargs.get("data_tags") or []
    if kwargs.get("custom_processing") is not None:
        # hack to run custom processing functions from this module
        func = globals().get(kwargs["custom_processing"], lambda x: x)
        row = func(row)
    work = Work(
        user_defined_id=row.get("pmid"),
        pmid=row.get("pmid"),
        doi=row.get("doi"),
        openalex_id=None,
        scopus_id=None,
        filename=row.get("filename") or "",
        content_hash=None,
    )
    client = Client(
        compute_context_id=kwargs.get("compute_context_id", 999),
        email=kwargs.get("email"),
    )
    invocation = Invocation(
        metrics=metrics_schema(**row),
        osm_version=kwargs.get("osm_version", __version__),
        client=client,
        work=work,
        user_comment=kwargs.get("user_comment", ""),
        data_tags=[*kwargs["data_tags"]],
        funder=(
            [row.get("funder")]
            if isinstance(row.get("funder"), str)
            else row.get("funder")
        ),
        components=kwargs.get("components", []),
    )
    return invocation


def get_data_from_mongo(aggregation: list[dict] | None = None) -> Iterator[dict]:
    if aggregation is None:
        aggregation = [
            {
                "$match": {},
            },
            {
                "$project": {
                    # "osm_version": True,
                    "funder": True,
                    "data_tags": True,
                    "doi": True,
                    "metrics_group": True,
                    "work.pmid": True,
                    "metrics.year": True,
                    "metrics.is_open_data": True,
                    "metrics.is_open_code": True,
                    "metrics.manual_is_open_code": True,
                    "metrics.rtransparent_is_open_code": True,
                    "metrics.manual_is_open_data": True,
                    "metrics.rtransparent_is_open_data": True,
                    "metrics.affiliation_country": True,
                    "metrics.journal": True,
                    "created_at": True,
                },
            },
        ]
    client = MongoClient(os.environ["MONGODB_URI"])
    engine = SyncEngine(client=client, database="osm")
    matches = (
        engine.get_collection(schemas.Invocation).aggregate(aggregation).__iter__()
    )
    for match in matches:
        yield flatten_dict(match)


def infer_type_for_column(column):
    # Check if the entire column contains lists
    if column.apply(lambda x: isinstance(x, list)).all():
        # Further check if all elements within the lists are strings
        if (
            column.dropna()
            .apply(lambda x: all(isinstance(item, str) for item in x))
            .all()
        ):
            return pa.list_(pa.string())
        else:
            # Handle lists with mixed types or other complex structures
            return pa.list_(pa.null())
    elif column.apply(lambda x: isinstance(x, int) or pd.isna(x)).all():
        return pa.int64()
    elif column.apply(lambda x: isinstance(x, float) or pd.isna(x)).all():
        return pa.float64()
    elif column.apply(lambda x: isinstance(x, bool) or pd.isna(x)).all():
        return pa.bool_()
    elif column.apply(lambda x: isinstance(x, str) or pd.isna(x)).all():
        return pa.string()
    else:
        # Default to string for unexpected or mixed types
        return pa.string()


def matches_to_table(matches: Iterator[dict], batch_size: int = 1000) -> pa.Table:
    # Initialize an empty list to store batches of tables
    tables = []

    # Process the generator in batches
    while True:
        # Collect the next batch of rows
        batch = list(next(matches, None) for _ in range(batch_size))
        batch = [row for row in batch if row is not None]

        # Break the loop if no more data
        if not batch:
            break

        # Convert batch of dicts to DataFrame
        df = pd.DataFrame(batch)
        if "created_at" in df.columns and df["created_at"].dtype == "O":
            df["created_at"] = pd.to_datetime(
                df["created_at"], utc=True, format="ISO8601"
            )

        # Drop the `_id` column if it exists
        if "_id" in df.columns:
            df = df.drop(columns=["_id"])

        # Adjust schema according to pre-existing functionality
        pyarrow_schema = get_pyarrow_schema()  # Get the base schema
        adjusted_schema = adjust_schema_to_dataframe(
            pyarrow_schema, df
        )  # Adjust schema to match DataFrame

        # Extend schema to include any additional columns in the DataFrame
        extra_columns = [col for col in df.columns if col not in adjusted_schema.names]
        for col in extra_columns:
            if col == "funder":
                inferred_type = pa.list_(pa.string())
            elif col == "data_tags":
                inferred_type = pa.list_(pa.string())
            elif col == "affiliation_country":
                inferred_type = pa.list_(pa.string())
            elif col == "rtransparent_is_open_data":
                inferred_type = pa.bool
            elif col == "manual_is_open_data":
                inferred_type = pa.bool_()
            elif col == "created_at":
                inferred_type = pa.timestamp("ns")
            else:
                inferred_type = infer_type_for_column(df[col])
            adjusted_schema = adjusted_schema.append(pa.field(col, inferred_type))

        # Convert DataFrame to PyArrow Table with the extended schema
        table = pa.Table.from_pandas(df, schema=adjusted_schema, safe=False)

        # Append the table to the list
        tables.append(table)

    if not tables:
        raise ValueError("Matches generator is empty")

    # Concatenate all tables into one and return
    return pa.concat_tables(tables)
