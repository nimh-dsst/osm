from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from pydantic import ValidationError
from typing import List
import requests
import pandas as pd
import tempfile
import os
from osm.schemas import Work, Client, Invocation
from osm._utils import get_compute_context_id
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# NOTICE: items without mapping to the dataframe
unmapped = {
    "article": "",
    "is_relevant": None,
    "is_explicit": None,
    "user_comment": "",
    "osm_version": ""
}


def transform_data(df: pd.DataFrame) -> List[Invocation]:
    """Handles data transformation as well as mapping"""
    invocations = []
    for index, row in df.iterrows():
        try:
            work = Work(
                user_defined_id=str(row["doi"]),
                pmid=str(row["pmid"]),
                doi=str(row["doi"]),
                openalex_id=None,
                scopus_id=None,
                filename=row["filename"],
                file=None,
                content_hash=None,
            )
            client = Client(
                compute_context_id=get_compute_context_id(),
                email=None
            )

            metrics = {
                "article": unmapped["article"],
                "pmid": row["pmid"],
                "is_coi_pred": row["is_coi_pred"],
                "coi_text": row["coi_text"],
                "is_funded_pred": row["is_fund_pred"],
                "funding_text": row["fund_text"],
                "support_1": row["support_1"],
                "support_3": row["support_3"],
                "support_4": row["support_4"],
                "support_5": row["support_5"],
                "support_6": row["support_6"],
                "support_7": row["support_7"],
                "support_8": row["support_8"],
                "support_9": row["support_9"],
                "support_10": row["support_10"],
                "developed_1": row["developed_1"],
                "received_1": row["received_1"],
                "received_2": row["received_2"],
                "recipient_1": row["recipient_1"],
                "authors_1": row["authors_1"],
                "authors_2": row["authors_2"],
                "thank_1": row["thank_1"],
                "thank_2": row["thank_2"],
                "fund_1": row["fund_1"],
                "fund_2": row["fund_2"],
                "fund_3": row["fund_3"],
                "supported_1": row["supported_1"],
                "financial_1": row["financial_1"],
                "financial_2": row["financial_2"],
                "financial_3": row["financial_3"],
                "grant_1": row["grant_1"],
                "french_1": row["french_1"],
                "common_1": row["common_1"],
                "common_2": row["common_2"],
                "common_3": row["common_3"],
                "common_4": row["common_4"],
                "common_5": row["common_5"],
                "acknow_1": row["acknow_1"],
                "disclosure_1": row["disclosure_1"],
                "disclosure_2": row["disclosure_2"],
                "is_register_pred": row["is_register_pred"],
                "register_text": row["register_text"],
                "is_relevant": unmapped["is_relevant"],
                "is_method": row["is_method"],
                "is_NCT": row["is_NCT"],
                "is_explicit": unmapped["is_explicit"]
            }

            invocation = Invocation(
                metrics=metrics,
                osm_version=unmapped["osm_version"],
                client=client,
                work=work,
                user_comment=unmapped["user_comment"],
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
        engine = AIOEngine(client=motor_client, database=db_name)
        for invocation in invocations:
            await engine.save(invocation)
        logger.info({
            "message": "upload successful"
        })
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
            temp_file, temp_file_path = tempfile.mkstemp(suffix='.csv')
            os.close(temp_file)  # Close the file descriptor
            with open(temp_file_path, 'wb') as file:
                file.write(response.content)
            return temp_file_path
        else:
            raise Exception(f"Failed to download CSV. Status code: {response.status_code}")
    except Exception as e:
        raise e


def main(data_path="all_indicators.feather"):
    try:
        df = read_data(data_path)
        if not df.empty:
            invocations = transform_data(df)
            db_url = os.getenv("DATABASE_URL", None)
            db_name = os.getenv("DATABASE_NAME", None)
            asyncio.run(upload_data(invocations,
                                    db_url, db_name))
        else:
            raise Exception("Dataframe is empy")
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        raise e


if __name__ == "__main__":
    main()
