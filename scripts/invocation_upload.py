import logging
import os
import pickle
import tempfile
from pathlib import Path
from typing import List

import pandas as pd
import requests

# from motor.motor_tornado import MotorClient
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import ValidationError

from osm.schemas import Client, Invocation, Work

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# NOTICE: output of rt_all without corresponding values in the all_indicators.csv from Rtransparent publication
unmapped = {
    "article": "",
    "is_relevant": None,
    "is_explicit": None,
}


def transform_data(df: pd.DataFrame) -> List[Invocation]:
    """Handles data transformation as well as mapping"""
    invocations = []
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

            invocations.append(invocation)
        except (KeyError, ValidationError) as e:
            if isinstance(e, KeyError):
                raise KeyError(f"Error key not found in row {index}: {e}")
            elif isinstance(e, ValidationError):
                raise e

    return invocations


def read_data(data_path: str):
    """Checks to see if url is a path or https to download or read file"""
    try:
        if data_path.startswith("https"):
            csv = download_csv(data_path)
            df = pd.read_csv(csv)
        else:
            df = pd.read_feather(data_path)
        return df
    except FileNotFoundError as e:
        raise e


async def upload_data(invocations: List[Invocation], mongo_uri: str, db_name: str):
    """upload invocations to MongoDB one after the other to prevent timeout"""
    motor_client = AsyncIOMotorClient(mongo_uri)
    try:
        engine = motor_client(client=motor_client, database=db_name)
        engine.save_all(invocations)
    except (TypeError, Exception) as e:
        if isinstance(e, TypeError):
            raise TypeError(e)
        elif isinstance(e, Exception):
            raise Exception(f"Failed to upload data: {e}")
    finally:
        motor_client.close()


def download_csv(url):
    """downloads file and store in a temp location"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            temp_file, temp_file_path = tempfile.mkstemp(suffix=".csv")
            os.close(temp_file)  # Close the file descriptor
            with open(temp_file_path, "wb") as file:
                file.write(response.content)
            return temp_file_path
        else:
            raise Exception(
                f"Failed to download CSV. Status code: {response.status_code}"
            )
    except Exception as e:
        raise e


def main(data_path="all_indicators.feather"):
    try:
        transformed_pickle = Path("invocations.pkl")
        if transformed_pickle.exists():
            df = pickle.loads(transformed_pickle.read_bytes())
        else:
            breakpoint()
            df = read_data(data_path)
            if not df.empty:
                invocations = transform_data(df)
                transformed_pickle.write_bytes(pickle.dumps(invocations))
            else:
                raise Exception("Dataframe is empty")
        db_url = os.getenv("DATABASE_URL", None)
        db_name = os.getenv("DATABASE_NAME", None)
        logger.warning(f"Uploading data to {db_url}")
        upload_data(invocations, db_url, db_name)
    except Exception as e:
        breakpoint()
        logger.error(f"Failed to process data: {e}")
        raise e


if __name__ == "__main__":
    main()
