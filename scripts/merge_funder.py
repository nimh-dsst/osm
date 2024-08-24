import argparse
import logging
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.dataset as ds
import pyarrow.parquet as pq

from osm.schemas.schema_helpers import get_table_with_schema, types_mapper

logging.basicConfig(level=logging.INFO)


def setup(dset_path, funder_path):
    dataset = pd.read_feather(dset_path, dtype_backend="pyarrow")

    if str(dset_path) == "tempdata/sharestats.feather":
        dataset = dataset.rename(columns={"article": "pmid"})
    funder = pd.read_feather(funder_path)
    return dataset, funder


def create_funders():
    """Not explicitly used but here to record the process of creating the funders file"""
    import pandas as pd

    id_cols = "pmid pmcid_pmc".split()
    df = (
        ds.dataset("tempdata/all_indicators_fully_typed-chunks/", format="parquet")
        .to_table()
        .to_pandas(types_mapper=types_mapper)
    )
    funding_mat = pd.read_csv("tempdata/take2-pmcid-funding-matrix.csv")
    with_pmid = funding_mat.merge(df[id_cols], on="pmcid_pmc", how="left")
    funder_columns = with_pmid.columns.difference(id_cols)
    df_fund = with_pmid[id_cols].assign(
        funder=with_pmid[funder_columns].apply(
            lambda x: sorted(funder_columns[x].tolist()), axis=1
        )
    )
    df_fund.to_feather("tempdata/funders.feather")


def get_user_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_path", help="Path to the dataset file")
    parser.add_argument("merge_col", default="pmcid_pmc", help="Column to merge on")
    parser.add_argument(
        "--funder_path",
        help="Path to the funders file",
        default="tempdata/funders.feather",
    )
    return parser.parse_args()


def merge_funder(funder, tb, merge_col):
    funder.funder = funder.funder.apply(lambda x: ",".join(x))
    tb = tb.drop_columns("funder").join(
        pa.Table.from_pandas(funder[["funder", merge_col]]), merge_col
    )
    split_col = pc.split_pattern(
        pc.if_else(pc.is_null(tb["funder"]), pa.scalar(""), tb["funder"]), pattern=","
    )

    # Replace the original column with the split column
    tb = tb.set_column(
        tb.column_names.index("funder"),
        "funder",
        pa.array(split_col, type=pa.list_(pa.string())),
    )
    return tb


def main():
    args = get_user_args()
    dset_path = Path(args.dataset_path)
    outpath = Path(f"tempdata/{dset_path.stem}-with-funder.parquet")
    dataset, funder = setup(dset_path, args.funder_path)

    print("Converting to pyarrow...")
    funder_field = pa.field("funder", pa.list_(pa.string()), nullable=True)
    tb = get_table_with_schema(dataset.assign(funder=None), [funder_field])

    print("Merging with funders...")
    merge_funder(funder, tb, args.merge_col)

    print("Writing output...")
    pq.write_table(
        tb,
        outpath,
        compression="snappy",
    )
    print(f"Data written to {outpath}")


if __name__ == "__main__":
    main()
