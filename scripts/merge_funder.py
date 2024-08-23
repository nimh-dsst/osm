import argparse
import logging
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq

from osm import schemas

logging.basicConfig(level=logging.INFO)


def odmantic_to_pyarrow(schema_dict):
    type_mapping = {
        "integer": pa.int64(),
        "number": pa.float64(),
        "string": pa.string(),
        "boolean": pa.bool_(),
        "null": pa.string(),  # We will handle None manually
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


def read_parquet_chunks_and_combine(chunk_dir, pyarrow_schema):
    dataset = ds.dataset(chunk_dir, format="parquet")

    # Select and order columns as per the pyarrow schema
    table = dataset.to_table(columns=pyarrow_schema.names)

    # Convert the PyArrow table to a Pandas DataFrame
    return table.to_pandas()


def save_combined_df_as_feather(df, output_file):
    df.reset_index(drop=True).to_feather(output_file)


def setup(dset_path, funder_path, merge_col):
    dataset = pd.read_feather(dset_path, dtype_backend="pyarrow")

    if str(dset_path) == "tempdata/sharestats.feather":
        dataset = dataset.rename(columns={"article": "pmid"})

    # Read the CSV, allowing pmid to be float64 to handle .0 cases
    df = pd.read_csv(funder_path, dtype={merge_col: float})

    # Convert merge_col to nullable integer type after handling any potential NaNs
    df[merge_col] = pd.to_numeric(
        df[merge_col], downcast="integer", errors="coerce"
    ).astype("Int64")

    funder_columns = df.columns.difference([merge_col])
    df["funder"] = df[funder_columns].apply(
        lambda x: funder_columns[x].tolist(), axis=1
    )
    funder = df.loc[df["funder"].astype(bool), [merge_col, "funder"]].set_index(
        merge_col
    )

    return dataset, funder, dset_path


def clean_funder_column(merged_df):
    def clean_funder(funder):
        if isinstance(funder, list):
            return sorted([str(f) for f in funder])
        return []

    merged_df["funder"] = merged_df["funder"].apply(clean_funder)
    return merged_df


def merge_funder(df, funder, merge_col):
    merged_df = df.merge(funder, on=merge_col, how="left")
    merged_df = clean_funder_column(merged_df)
    return merged_df


def subset_schema_to_dataframe(schema, df):
    fields = [field for field in schema if field.name in df.columns]
    # Adjust the schema again to include the 'funder' column
    funder_field = pa.field("funder", pa.list_(pa.string()), nullable=True)
    fields.append(funder_field)

    return pa.schema(fields)


def get_user_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_path", help="Path to the dataset file")
    parser.add_argument("funder_path", help="Path to the funders file")
    parser.add_argument("merge_col", default="pmcid_pmc", help="Column to merge on")
    return parser.parse_args()


def main():
    args = get_user_args()
    dset_path = Path(args.dataset_path)
    odmantic_schema_json = schemas.RtransparentMetrics.model_json_schema()
    pyarrow_schema = odmantic_to_pyarrow(odmantic_schema_json)
    dataset, funder, dset_path = setup(dset_path, args.funder_path, args.merge_col)

    # Convert float NaNs to None and enforce correct data types
    dataset = dataset.where(pd.notna(dataset), None)

    # Convert specific columns to nullable integers, ensuring proper conversion of NA to None
    for col in ["year", "year_ppub", "year_epub", "pmid"]:
        if col in dataset.columns:
            dataset[col] = pd.to_numeric(dataset[col], errors="coerce").astype("Int64")

            # Explicitly replace pd.NA with None after conversion
            dataset[col] = dataset[col].apply(lambda x: None if pd.isna(x) else int(x))

    adjusted_schema = subset_schema_to_dataframe(pyarrow_schema, dataset)

    output_dir = Path(f"tempdata/{dset_path.stem}-chunks")
    output_dir.mkdir(parents=True, exist_ok=True)

    chunk_size = 400000
    for i in range(0, len(dataset), chunk_size):
        print(f"{i} / {len(dataset)}")
        chunk = dataset.iloc[i : i + chunk_size]
        chunk = merge_funder(chunk, funder, args.merge_col)
        chunk_file = output_dir / f"chunk_{i // chunk_size}.parquet"
        pq.write_table(
            pa.Table.from_pandas(chunk, schema=adjusted_schema),
            chunk_file,
            compression="snappy",
        )

    df_out = read_parquet_chunks_and_combine(output_dir, adjusted_schema)
    save_combined_df_as_feather(
        df_out, dset_path.parent / f"{dset_path.stem}-with-funder.feather"
    )


if __name__ == "__main__":
    main()
