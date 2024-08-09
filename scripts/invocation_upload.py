import logging
import os
from typing import List

import pandas as pd
import pymongo
from pydantic import ValidationError

from osm.schemas import Client, Invocation, Work

DB_NAME = os.environ["DB_NAME"]
MONGO_URI = os.environ["MONGO_URI"]
ERROR_CSV_PATH = "error_log.csv"
ERROR_LOG_PATH = "error.log"
# NOTICE: output of rt_all without corresponding values in the all_indicators.csv from Rtransparent publication
unmapped = {
    "article": "",
    "is_relevant": None,
    "is_explicit": None,
}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def transform_data(df) -> List[Invocation]:
    """Convert the dataframe to a list of Invocation objects"""
    for index, row in df.iterrows():
        try:
            work = Work(
                user_defined_id=str(row["doi"]),
                pmid=str(row.pop("pmid")),
                doi=str(row.pop("doi")),
                openalex_id=None,
                scopus_id=None,
                filename=row.pop("filename"),
                file=None,
                content_hash=None,
            )
            client = Client(compute_context_id=999, email=None)

            metrics = {**unmapped, **row.to_dict()}
            invocation = Invocation(
                metrics=metrics,
                osm_version="0.0.1",
                client=client,
                work=work,
                user_comment="Initial database seeding with data from Rtransparent publication",
            )
            yield invocation.dict()

        except (KeyError, ValidationError) as e:
            logger.error(f"Error processing row {index}")
            write_error_to_file(invocation, e)


def write_error_to_file(invocation: Invocation, error: Exception):
    with open(ERROR_CSV_PATH, "a") as csv_file, open(ERROR_LOG_PATH, "a") as log_file:
        # Write the problematic invocation data to the CSV
        row_dict = {
            **invocation.metrics,
            **invocation.work.dict(),
            **invocation.client.dict(),
        }
        pd.DataFrame([row_dict]).to_csv(
            csv_file, header=csv_file.tell() == 0, index=False
        )

        # Log the error details
        log_file.write(f"Error processing invocation: {invocation}\nError: {error}\n\n")


def main():
    df = pd.read_feather("all_indicators.feather", dtype_backend="pyarrow")
    if df.empty:
        raise Exception("Dataframe is empty")
    try:
        db = pymongo.MongoClient(MONGO_URI).osm
        db.invocation.insert_many(transform_data(df))
    except Exception as e:
        breakpoint()
        logger.error(f"Failed to process data: {e}")
        # raise e
    breakpoint()


if __name__ == "__main__":
    main()
