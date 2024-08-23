import argparse
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from osm import schemas


def odmantic_to_pyarrow(schema_dict):
    # Type mapping from JSON schema types to pyarrow types
    type_mapping = {
        "integer": pa.int64(),
        "number": pa.float64(),
        "string": pa.string(),
        "boolean": pa.bool_(),
        # For simplicity, map null to string, but this will not be used
        "null": pa.string(),
        "array": pa.list_(pa.string()),  # Assuming array of strings; adjust as needed
        "object": pa.struct([]),  # Complex types can be handled differently
    }

    fields = []

    for prop, details in schema_dict["properties"].items():
        if "anyOf" in details:
            # Handle 'anyOf' by selecting the first non-null type
            primary_type = next(
                (t["type"] for t in details["anyOf"] if t["type"] != "null"), "string"
            )
            pyarrow_type = type_mapping[primary_type]
            nullable = True  # If 'anyOf' contains 'null', the field should be nullable
        else:
            # Directly map the type if 'anyOf' is not present
            pyarrow_type = type_mapping.get(details["type"], pa.string())
            nullable = False  # Assume fields without 'anyOf' are non-nullable

        # Create the field with the appropriate nullability
        fields.append(pa.field(prop, pyarrow_type, nullable=nullable))

    return pa.schema(fields)


def read_parquet_chunks_and_combine(chunk_dir, pyarrow_schema):
    chunk_dir = Path(chunk_dir)
    all_files = sorted(chunk_dir.glob("*.parquet"))

    dfs = []
    for file in all_files:
        df = pd.read_parquet(file, schema=pyarrow_schema)
        dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df


def save_combined_df_as_feather(df, output_file):
    df.reset_index(drop=True).to_feather(output_file)


def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_path", help="Path to the dataset file")
    args = parser.parse_args()
    dset_path = Path(args.dataset_path)
    dataset = pd.read_feather(dset_path, dtype_backend="pyarrow")
    if str(dset_path) == "tempdata/sharestats.feather":
        dataset = dataset.rename(columns={"article": "pmid"})

    df = pd.read_csv("tempdata/pmid-funding-matrix.csv")
    funder_columns = df.columns.difference(["pmid"])
    df["funder"] = df[funder_columns].apply(
        lambda x: funder_columns[x].tolist(), axis=1
    )
    funder = df.loc[df["funder"].astype(bool), ["pmid", "funder"]]
    return dataset, funder, dset_path


def merge_funder(row, funder):
    pmid = row["pmid"]
    funder_info = funder[funder["pmid"] == pmid]

    if not funder_info.empty:
        row["funder"] = funder_info.iloc[0]["funder"]
    else:
        row["funder"] = []

    return row


def subset_schema_to_dataframe(schema, df):
    # Filter schema fields to only those present in the DataFrame
    fields = [field for field in schema if field.name in df.columns]
    return pa.schema(fields)


def main():
    odmantic_schema_json = schemas.RtransparentMetrics.model_json_schema()
    pyarrow_schema = odmantic_to_pyarrow(odmantic_schema_json)

    dataset, funder, dset_path = setup()

    adjusted_schema = subset_schema_to_dataframe(pyarrow_schema, dataset)

    output_dir = Path(f"tempdata/{dset_path.stem}-chunks")
    output_dir.mkdir(parents=True, exist_ok=True)

    chunk_index = 0
    collected_rows = []

    for _, row in dataset.iterrows():
        fixed_row = merge_funder(row, funder)
        collected_rows.append(fixed_row)

        if len(collected_rows) >= 1000:
            chunk_file = output_dir / f"chunk_{chunk_index}.parquet"
            pq.write_table(
                pa.Table.from_pandas(
                    pd.DataFrame(collected_rows), schema=adjusted_schema
                ),
                chunk_file,
                compression="snappy",
            )
            collected_rows = []
            chunk_index += 1

    if collected_rows:
        chunk_file = output_dir / f"chunk_{chunk_index}.parquet"
        try:
            pq.write_table(
                pa.Table.from_pandas(
                    pd.DataFrame(collected_rows), schema=adjusted_schema
                ),
                chunk_file,
                compression="snappy",
            )
        except ValueError:
            breakpoint()

    df_out = read_parquet_chunks_and_combine(output_dir, adjusted_schema)
    save_combined_df_as_feather(
        df_out, dset_path.parent / f"{dset_path.stem}-with-funder.feather"
    )


if __name__ == "__main__":
    main()
