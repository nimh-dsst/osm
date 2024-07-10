from pathlib import Path

import pandas as pd
import psutil
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

from osm.config import osm_config

ro.r(f'Sys.setenv(VROOM_CONNECTION_SIZE = "{osm_config.vroom_connection_size}")')


def rtransparent_metric_extraction(text_dir: Path, workers: int = psutil.cpu_count()):
    rtransparent = importr("rtransparent")
    future = importr("future")
    future.plan(future.multisession, workers=workers)
    metrics = []
    for file_path in text_dir.glob("*.txt"):
        with (ro.default_converter + pandas2ri.converter).context():
            metrics.append = ro.conversion.get_conversion().rpy2py(
                rtransparent.rt_data_code(file_path)
            )

    breakpoint()
    return pd.concat([row for row in metrics], ignore_index=True)
