import argparse
import logging
import os
from pathlib import Path

import pyarrow.dataset as ds
import pymongo

from osm import schemas
from osm.schemas import Component, schema_helpers
from osm.schemas.schema_helpers import transform_data

logger = logging.getLogger(__name__)

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
theneuro_kwargs = {
    "data_tags": ["The Neuro"],
    "user_comment": "Bulk upload of The Neuro data containing OddPub metrics underlying RTransparent metrics for open code/data.",
    "components": [Component(name="TheNeuroOddPub", version="x.x.x")],
}
manual_scoring_kwargs = {
    "data_tags": ["Manual Annotation NIMH/DSST"],
    "user_comment": "Bulk upload of some manually scored  open code/data along with RTransparent extracted equivalents.",
    "components": [Component(name="ManualAnnotation-NIMHDSST", version="x.x.x")],
    "metrics_schema": schemas.ManualAnnotationNIMHDSST,
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
    else:
        raise ValueError("Only parquet files are supported")
    return tb


def get_upload_kwargs(args):
    if args.custom_processing:
        if not hasattr(schema_helpers, args.custom_processing):
            logger.warning(
                f"Custom processing function {args.custom_processing} not found"
            )
        if args.custom_processing == "rtransparent_pub_data_processing":
            kwargs = rtrans_publication_kwargs
        elif args.custom_processing == "irp_data_processing":
            kwargs = irp_kwargs
        elif args.custom_processing == "theneuro_data_processing":
            kwargs = theneuro_kwargs
        elif args.custom_processing == "manual_scoring_data_processing":
            kwargs = manual_scoring_kwargs
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
    schema = upload_kwargs.pop("metrics_schema", schemas.RtransparentMetrics)

    try:
        db = pymongo.MongoClient(MONGODB_URI).osm
        db.invocation.insert_many(
            transform_data(tb, metrics_schema=schema, **upload_kwargs), ordered=False
        )
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        raise e


if __name__ == "__main__":
    main()
