import base64
import hashlib
import json
import logging
import os
from pathlib import Path

import dill
import requests
from pydantic import ValidationError

from osm import schemas
from osm._utils import get_compute_context_id
from osm._version import __version__

from .core import Component

logger = logging.getLogger(__name__)


class FileSaver(Component):
    """Basic saver that writes data to a file."""

    def _run(self, data: str, path: Path):
        """Write data to a file.

        Args:
            data (str): Some data.
            path (Path): A file path.
        """
        path.write_text(data)
        logger.info(f"Data saved to {path}")


class JSONSaver(Component):
    """Saver that writes JSON data to a file."""

    def _run(self, data: dict, path: Path):
        """Write output metrics to a JSON file for the user.

        Args:
            data (dict): Metrics conformant to a schema.
            path (Path): An output path for the metrics.
        """
        path.write_text(json.dumps(data))
        logger.info(f"Metrics saved to {path}")
        print(f"Metrics saved to {path}")


class OSMSaver(Component):
    """A class to gather savers to run a pipeline."""

    def __init__(self, comment, email, user_defined_id, filename):
        """Upload data to the OSM API.

        Args:
            comment (str): A comment from the user in inform downstream analysis.
            email (str): For users to be contactable for future data curation etc.
            user_defined_id (str): pmid, pmcid, doi, or other unique identifier.
            filename (str): Name of the file being processed.
        """
        super().__init__()
        self.compute_context_id = get_compute_context_id()
        self.comment = comment
        self.email = email
        self.user_defined_id = user_defined_id
        self.filename = filename

    def _run(self, data: bytes, metrics: dict, components: list[schemas.Component]):
        """Save the extracted metrics to the OSM API.

        Args:
            data: Component input.
            metrics: Schema conformant metrics.
            components: parsers, extractors, and savers that constitute the pipeline.
        """
        osm_api = os.environ.get("OSM_API", "https://osm.pythonaisolutions.com/api")
        print(f"Using OSM API: {osm_api}")
        # Build the payload
        payload = {
            "osm_version": __version__,
            "user_comment": self.comment,
            "work": {
                "user_defined_id": self.user_defined_id,
                "filename": self.filename,
                "content_hash": hashlib.sha256(data).hexdigest(),
            },
            "client": {
                "compute_context_id": self.compute_context_id,
                "email": self.email,
            },
            "metrics": schemas.RtransparentMetrics(**metrics),
            "components": [comp.orm_model for comp in components],
        }
        try:
            # Validate the payload
            validated_data = schemas.Invocation(**payload)
            # If validation passes, send POST request to OSM API. ID is not
            # serializable but can be excluded and created by the DB. All types
            # should be serializable. If they're not then they should be encoded
            # as a string or something like that: base64.b64encode(bytes).decode("utf-8")
            response = requests.put(
                f"{osm_api}/upload/",
                json=validated_data.model_dump(mode="json", exclude=["id"]),
            )
            if response.status_code == 200:
                print("Invocation data uploaded successfully")
            else:
                raise ValueError(
                    f"Failed to upload invocation data: \n {response.text}"
                )
        except requests.exceptions.ConnectionError:
            raise EnvironmentError(f"Cannot connect to OSM API ({osm_api})")
        except (ValidationError, ValueError) as e:
            try:
                # Quarantine the failed payload
                failure = schemas.Quarantine(
                    payload=base64.b64encode(dill.dumps(payload)).decode("utf-8"),
                    error_message=str(e),
                ).model_dump(mode="json", exclude=["id"])
                response = requests.put(f"{osm_api}/quarantine/", json=failure)
                response.raise_for_status()
                raise e
            except requests.exceptions.RequestException as qe:
                requests.put(
                    f"{osm_api}/quarantine/",
                    json=schemas.Quarantine(
                        error_message=str(e),
                        recovery_message=str(qe),
                    ).model_dump(mode="json", exclude=["id"]),
                )
                raise e
