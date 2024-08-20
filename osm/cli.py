import argparse

from osm._utils import DEFAULT_OUTPUT_DIR, _existing_file, _setup, compose_down
from osm.pipeline.core import Pipeline, Savers
from osm.pipeline.extractors import RTransparentExtractor
from osm.pipeline.parsers import NoopParser, ScienceBeamParser
from osm.pipeline.savers import FileSaver, JSONSaver, OSMSaver

PARSERS = {
    "sciencebeam": ScienceBeamParser,
    "no-op": NoopParser,
}
EXTRACTORS = {
    "rtransparent": RTransparentExtractor,
}


def parse_args():
    parser = argparse.ArgumentParser(description=("""Manage the execution of osm."""))

    parser.add_argument(
        "-f",
        "--filepath",
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
        "--parser",
        choices=PARSERS.keys(),
        default=["sciencebeam"],
        nargs="+",
        help="Select the tool for parsing the input document. Default is 'sciencebeam'.",
    )
    parser.add_argument(
        "--metrics-type",
        choices=EXTRACTORS.keys(),
        default=["rtransparent"],
        nargs="+",
        help="Select the tool for extracting the output metrics. Default is 'rtransparent'.",
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


def main():
    args = parse_args()
    try:
        xml_path, metrics_path = _setup(args)

        pipeline = Pipeline(
            filepath=args.filepath,
            xml_path=xml_path,
            metrics_path=metrics_path,
            parsers=[PARSERS[p]() for p in args.parser],
            extractors=[EXTRACTORS[m]() for m in args.metrics_type],
            savers=Savers(
                file_saver=FileSaver(),
                json_saver=JSONSaver(),
                osm_saver=OSMSaver(
                    comment=args.comment,
                    email=args.email,
                    user_defined_id=args.uid,
                    filename=args.filepath.name,
                ),
            ),
        )
        pipeline.run()
    finally:
        if not args.user_managed_compose:
            compose_down()


if __name__ == "__main__":
    main()
