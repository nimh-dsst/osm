import argparse
import logging
import os
from pathlib import Path

import pandas as pd
import pyarrow.dataset as ds
import pymongo
from pydantic import ValidationError

from osm import schemas

DB_NAME = os.environ["DB_NAME"]
MONGODB_URI = os.environ["MONGODB_URI"]
ERROR_CSV_PATH = Path("error_log.csv")
ERROR_LOG_PATH = Path("error.log")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
cols_mapping = {}


def custom_irp_data_processing(row):
    return row


def custom_rtransparent_pub_data_processing(row):
    row["is_open_code"] = row.pop("is_code_pred")
    row["is_open_data"] = row.pop("is_data_pred")
    row["pmid"] = None if pd.isnull(row.pmid) else int(row["pmid"])
    row["year_ppub"] = None if pd.isnull(row.year_ppub) else int(row["year_ppub"])
    row["year_epub"] = None if pd.isnull(row.year_epub) else int(row["year_epub"])
    row["year"] = None if pd.isnull(row.year) else int(row["year"])
    row["doi"] = None if pd.isnull(row.doi) else row["doi"]
    return row


def transform_data(df, tags=None, custom_processing=None) -> list[schemas.Invocation]:
    """Convert the dataframe to a list of Invocation objects"""
    tags = tags or []
    for index, row in df.iterrows():
        try:
            if custom_processing is not None:
                func = globals()[custom_processing]
                row = func(row)
            work = schemas.Work(
                user_defined_id=row.get("doi") or str(row.get("pmid")),
                pmid=row.get("pmid"),
                doi=row.get("doi"),
                openalex_id=None,
                scopus_id=None,
                filename=row.get("filename") or "",
                content_hash=None,
            )
            client = schemas.Client(compute_context_id=999, email=None)

            metrics = {**row.to_dict()}
            invocation = schemas.Invocation(
                metrics=metrics,
                osm_version="0.0.1",
                client=client,
                work=work,
                user_comment="Initial database seeding with publications from the NIH IRP",
                data_tags=["bulk_upload", *tags],
                funder=row.get("funder"),
                components=[
                    schemas.Component(name="Scibeam-parser/Rtransparent", version="NA")
                ],
            )
            yield invocation.model_dump(mode="json", exclude="id")

        except (KeyError, ValidationError, Exception) as e:
            breakpoint()
            logger.error(f"Error processing row {index}")
            write_error_to_file(row, e)


def write_error_to_file(row: pd.Series, error: Exception):
    with ERROR_CSV_PATH.open("a") as csv_file, ERROR_LOG_PATH.open("a") as log_file:
        # Write the problematic row data to the CSV, add header if not yet populated.
        row.to_csv(
            csv_file,
            header=not ERROR_CSV_PATH.exists() or ERROR_CSV_PATH.stat().st_size == 0,
            index=False,
        )

        # Drop string values as they tend to be too long
        display_row = (
            row.apply(lambda x: x if not isinstance(x, str) else None)
            .dropna()
            .to_dict()
        )
        log_file.write(f"Error processing data:\n {display_row}\nError: {error}\n\n")


def parse_args():
    parser = argparse.ArgumentParser(description="Invocation Upload")
    parser.add_argument(
        "-i",
        "--input_file",
        required=True,
        help="Path to the input file if it is feather (or a directory for chunked parquet)",
    )
    parser.add_argument(
        "-t",
        "--tags",
        nargs="+",
        help="Tags to apply to the uploaded data for filtering etc.",
    )
    parser.add_argument(
        "-c",
        "--custom-processing",
        help="Name of function that applies custom processing to the data",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    file_in = Path(args.input_file)
    if file_in.is_dir():
        df = ds.dataset(file_in, format="parquet").to_table().to_pandas()
    else:
        df = pd.read_feather(file_in, dtype_backend="pyarrow")

    if df.empty:
        raise Exception("Dataframe is empty")

    try:
        db = pymongo.MongoClient(MONGODB_URI).osm
        db.invocation.insert_many(
            transform_data(df, tags=args.tags, custom_processing=args.custom_processing)
        )
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        raise e


if __name__ == "__main__":
    main()
