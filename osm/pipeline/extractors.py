import json

import requests


def _extract(xml: bytes) -> str:
    """Extracts metrics from an XML.

    Args:
        xml: Raw bytes for an xml file.
    """
    headers = {"Content-Type": "application/octet-stream"}
    response = requests.post(
        "http://localhost:8071/extract-metrics", data=xml, headers=headers
    )
    if response.status_code == 200:
        return json.loads(response.json())[0]
    else:
        response.raise_for_status()


# import psutil
# # Adjust the logging level for rpy2
# rpy2_logger = logging.getLogger("rpy2")
# rpy2_logger.setLevel(logging.DEBUG)

# oddpub = importr("oddpub")
# future = importr("future")
# ro.r(f'Sys.setenv(VROOM_CONNECTION_SIZE = "{osm_config.vroom_connection_size}")')


# def oddpub_pdf_conversion(
#     pdf_dir: Path, text_dir: Path, workers: int = psutil.cpu_count()
# ):
#     future.plan(future.multisession, workers=workers)
#     oddpub.pdf_convert(str(pdf_dir), str(text_dir))


# def oddpub_metric_extraction(text_dir: Path, workers: int = psutil.cpu_count()):
#     future.plan(future.multisession, workers=workers)
#     pdf_sentences = oddpub.pdf_load(f"{text_dir}/")
#     open_data_results = oddpub.open_data_search(pdf_sentences)
#     with (ro.default_converter + pandas2ri.converter).context():
#         metrics = ro.conversion.get_conversion().rpy2py(open_data_results)

#     return metrics
