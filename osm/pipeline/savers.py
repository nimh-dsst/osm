import base64
import hashlib
import json
import logging
import os
from pathlib import Path

import requests
from pydantic import ValidationError

from osm._utils import get_compute_context_id
from osm._version import __version__
from osm.schemas import Invocation

from .core import Component

logger = logging.getLogger(__name__)


class FileSaver(Component):
    def run(self, data: str, path: Path):
        path.write_text(data)


class JSONSaver(Component):
    def run(self, data: dict, path: Path):
        path.write_text(json.dumps(data))


class OSMSaver(Component):
    def __init__(self, comment, email, user_defined_id, filename):
        super().__init__()
        self.compute_context_id = get_compute_context_id()
        self.comment = comment
        self.email = email
        self.user_defined_id = user_defined_id
        self.filename = filename

    def run(self, file_in: bytes, metrics: dict, components: list):
        osm_api = os.environ.get("OSM_API", "http://localhost:80")
        # Build the payload
        payload = {
            "osm_version": __version__,
            "user_comment": self.comment,
            "work": {
                "user_defined_id": self.user_defined_id,
                "filename": self.filename,
                "file": base64.b64encode(file_in).decode("utf-8"),
                "content_hash": hashlib.sha256(file_in).hexdigest(),
            },
            "client": {
                "compute_context_id": self.compute_context_id,
                "email": self.email,
            },
            "metrics": metrics,
            "components": [comp.model_dump() for comp in components],
        }
        try:
            # Validate the payload
            validated_data = Invocation(**payload)
            # If validation passes, send POST request to OSM API. ID is not
            # serializable but can be excluded and created by the DB. All types
            # should be serializable. If they're not then a they should be encoded
            # as a string or something like that:  base64.b64encode(bytes).decode("utf-8")
            response = requests.put(
                f"{osm_api}/upload", json=validated_data.model_dump(exclude=["id"])
            )
            if response.status_code == 200:
                print("Invocation data uploaded successfully")
            else:
                raise ValueError(
                    f"Failed to upload invocation data: \n {response.text}"
                )
        except (ValidationError, ValueError) as e:
            breakpoint()
            try:
                payload["upload_error"] = str(e)
                # Quarantine the failed payload
                response = requests.put(f"{osm_api}/quarantine", json=payload)
                response.raise_for_status()
            except requests.exceptions.RequestException as qe:
                requests.put(
                    f"{osm_api}/quarantine",
                    json={
                        "upload_error": str(e),
                        "recovery_error": str(qe),
                    },
                )
            logger.warning(f"Validation failed: {e}")
