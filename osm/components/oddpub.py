"""
Oddpub is being actively developed where as rtransparent has stagnated.
Oddpub implements parallelism and their interface does not easily allow working
with objects in memory so we will use that to reduce IO overhead.

The alternative would be to load the pdf file into memory (pdftools::pdf_data
and then pass that into oddpub private functions). This would make it easier to
manage the parallelism, troubleshoot, and define the interface but partially
reinvents the wheel.
"""

import logging
from pathlib import Path

import psutil
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

from osm.config import osm_config

logging.basicConfig(level=logging.DEBUG)

# Adjust the logging level for rpy2
rpy2_logger = logging.getLogger("rpy2")
rpy2_logger.setLevel(logging.DEBUG)

oddpub = importr("oddpub")
future = importr("future")
ro.r(f'Sys.setenv(VROOM_CONNECTION_SIZE = "{osm_config.vroom_connection_size}")')


def oddpub_pdf_conversion(
    pdf_dir: Path, text_dir: Path, workers: int = psutil.cpu_count()
):
    future.plan(future.multisession, workers=workers)
    oddpub.pdf_convert(str(pdf_dir), str(text_dir))


def oddpub_metric_extraction(text_dir: Path, workers: int = psutil.cpu_count()):
    future.plan(future.multisession, workers=workers)
    pdf_sentences = oddpub.pdf_load(f"{text_dir}/")
    open_data_results = oddpub.open_data_search(pdf_sentences)
    with (ro.default_converter + pandas2ri.converter).context():
        metrics = ro.conversion.get_conversion().rpy2py(open_data_results)

    return metrics
