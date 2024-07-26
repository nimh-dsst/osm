import argparse
from pathlib import Path

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
