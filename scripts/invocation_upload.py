import argparse
import logging
import os
from pathlib import Path

import pyarrow.dataset as ds
import pymongo

from osm.schemas import Component, schema_helpers
from osm.schemas.schema_helpers import transform_data

DB_NAME = os.environ["DB_NAME"]
MONGODB_URI = os.environ["MONGODB_URI"]


rtrans_publication_kwargs = {
    "data_tags": ["PMC-OA 2020"],
    "user_comment": "Bulk upload of rtransparent publication data that processed all open access XMLs from pubmed central in 2020",
    "components": [Component(name="rtransparent-publication", version="x.x.x")],
}
irp_kwargs = {
    "data_tags": ["NIH-IRP"],
    "user_comment": "Bulk upload of NIH-IRP data",
    "components": [Component(name="Sciencebeam parser/RTransparent", version="x.x.x")],
}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
cols_mapping = {}


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
        default=[],
        help="Tags to apply to the uploaded data for filtering etc.",
    )
    parser.add_argument(
        "-c",
        "--custom-processing",
        help="Name of function that applies custom processing to the data",
    )
    return parser.parse_args()


def get_data(args):
    file_in = Path(args.input_file)
    if file_in.is_dir() or file_in.suffix == ".parquet":
        tb = ds.dataset(file_in, format="parquet").to_table()
    return tb


def get_upload_kwargs(args):
    if args.custom_processing:
        assert hasattr(
            schema_helpers, args.custom_processing
        ), f"Custom processing function {args.custom_processing} not found"
        if args.custom_processing == "rtransparent_pub_data_processing":
            kwargs = rtrans_publication_kwargs
        elif args.custom_processing == "irp_data_processing":
            kwargs = irp_kwargs
        else:
            raise ValueError(
                f"Kwargs associated with {args.custom_processing} not found"
            )
        kwargs.update(
            {
                "data_tags": [*kwargs["data_tags"], *args.tags],
                "custom_processing": args.custom_processing,
            }
        )
    return kwargs


def main():
    args = parse_args()
    tb = get_data(args)
    upload_kwargs = get_upload_kwargs(args)

    try:
        db = pymongo.MongoClient(MONGODB_URI).osm
        db.invocation.insert_many(transform_data(tb, **upload_kwargs), ordered=False)
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        raise e


if __name__ == "__main__":
    main()
