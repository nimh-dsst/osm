import logging

import requests

from osm.schemas.custom_fields import LongBytes

from .core import Component

logger = logging.getLogger(__name__)


class RTransparentExtractor(Component):
    def _run(self, data: bytes, parser: str = None) -> dict:
        self.sample = LongBytes(data)
        headers = {"Content-Type": "application/octet-stream"}
        response = requests.post(
            "http://localhost:8071/extract-metrics",
            data=data,
            headers=headers,
            params={"parser": parser},
        )
        if response.status_code == 200:
            metrics = response.json()
            # pmid only exists when input filename is correct
            metrics.pop("pmid")
            #  replace bizarre sentinel value
            for k, v in metrics.items():
                if v == -2147483648:
                    metrics[k] = None
            return metrics
        else:
            logger.error(f"Error: {response.text}")
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
