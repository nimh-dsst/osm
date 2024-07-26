import argparse
import json
import logging
import shlex
import subprocess
import time
from pathlib import Path

import requests

from osm._utils import (
    DEFAULT_OUTPUT_DIR,
    _existing_file,
    _get_metrics_dir,
    _get_text_dir,
    _upload_data,
)
from osm.components.rtransparent import _extract
from osm.components.sciencebeam import _convert

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description=("""Manage the execution of osm."""))

    parser.add_argument(
        "-f",
        "--file",
        type=_existing_file,
        required=True,
        help="Specify the path to the pdf/xml for processing.",
    )
    parser.add_argument(
        "-u",
        "--uid",
        required=True,
        help="Specify a unique id for the work. This can be a DOI, PMID, OpenAlex ID, or Scopus ID.",
    )
    parser.add_argument(
        "--output_dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to store output.",
    )
    parser.add_argument(
        "--comment",
        required=False,
        help="Comment to provide more information about the provided publication.",
    )
    parser.add_argument(
        "--email",
        required=False,
        help="Email if you wish to be contactable for future data curation etc.",
    )
    parser.add_argument(
        "--user-managed-compose",
        action="store_true",
        help="""Disable starting and stopping the docker compose managed containers.
        Can be useful for debugging and repeatedly running the processing.""",
    )
    return parser.parse_args()


def wait_for_containers():
    while True:
        try:
            response = requests.get("http://localhost:8071/health")
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass

        time.sleep(1)


def compose_up():
    cmd = shlex.split("docker-compose up -d --build")
    subprocess.run(
        cmd,
        check=True,
    )


def compose_down():
    cmd = shlex.split("docker-compose down")
    subprocess.run(
        cmd,
        check=True,
    )


def _setup(args):
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    xml_out = _get_text_dir() / f"{args.uid}.xml"
    if args.file.name.endswith(".pdf"):
        if xml_out.exists():
            raise FileExistsError(xml_out)
    metrics_out = _get_metrics_dir() / f"{args.uid}.json"
    if metrics_out.exists():
        raise FileExistsError(metrics_out)
    if not args.user_managed_compose:
        compose_up()
    logger.info("Waiting for containers to be ready...")
    wait_for_containers()
    return xml_out, metrics_out


def main():
    args = parse_args()
    try:
        xml_out, metrics_out = _setup(args)
        file_in = args.file.read_bytes()

        if args.file.name.endswith(".pdf"):
            xml = _convert(file_in)
            xml_out.write_bytes(xml)
        else:
            xml = file_in
        extracted = _extract(xml)
        metrics_out.write_text(json.dumps(extracted))
        _upload_data(args, file_in, xml, extracted)

    finally:
        if not args.user_managed_compose:
            compose_down()
        pass


if __name__ == "__main__":
    main()
