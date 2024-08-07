import argparse
import base64
import hashlib
import os
from pathlib import Path

import requests

from osm._version import __version__

DEFAULT_OUTPUT_DIR = "./osm_output"


def _get_metrics_dir(output_dir: Path = DEFAULT_OUTPUT_DIR) -> Path:
    metrics_dir = Path(output_dir) / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    return metrics_dir


def _get_text_dir(output_dir: Path = DEFAULT_OUTPUT_DIR) -> Path:
    text_dir = Path(output_dir) / "pdf_texts"
    text_dir.mkdir(parents=True, exist_ok=True)
    return text_dir


def _existing_file(path_string):
    path = Path(path_string)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"The path {path} does not exist.")
    return path


def get_compute_context_id():
    return hash(f"{os.environ.get('HOSTNAME')}_{os.environ.get('USERNAME')}")


def _upload_data(args, file_in, xml, extracted):
    """
    TODO: add in derivatives and components
    """
    osm_api = os.environ.get("OSM_API", "http://localhost:80")

    payload = {
        "osm_version": __version__,
        "user_comment": args.comment,
        "work": {
            "user_defined_id": args.uid,
            "filename": args.file.name,
            "file": base64.b64encode(file_in).decode("utf-8"),
            "content_hash": hashlib.sha256(file_in).hexdigest(),
        },
        "client": {
            "compute_context_id": get_compute_context_id(),
            "email": args.email,
        },
        "metrics": extracted,
    }
    # Send POST request to OSM API
    response = requests.put(f"{osm_api}/upload", json=payload)

    # Check response status code
    if response.status_code == 200:
        print("Invocation data uploaded successfully")
    else:
        print(f"Failed to upload invocation data: \n {response.text}")
