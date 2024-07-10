from pathlib import Path
from typing import Tuple, Union

import fire

from osm.oddpub import oddpub_metric_extraction, oddpub_pdf_conversion
from osm.rtransparent import rtransparent_metric_extraction
from osm.sciencebeam import sciencebeam_pdf_conversion


def setup_dirs(
    input_dir: Union[str, Path], output_dir: Union[str, Path]
) -> Tuple[Path, Path]:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    if not input_dir.exists():
        raise ValueError(f"The path {input_dir} does not exist.")

    output_dir.mkdir(parents=True, exist_ok=True)

    return input_dir, output_dir


class OSM:
    def __init__(self):
        self.pdf_converters = {
            "sciencebeam": sciencebeam_pdf_conversion,
            "oddpub": oddpub_pdf_conversion,
        }
        self.metric_extractors = {
            "rtransparent": rtransparent_metric_extraction,
            "oddpub": oddpub_metric_extraction,
        }
        self._pdf_dir = None
        self._text_dir = None
        self._outdir = None

    def convert(
        self,
        *,
        pdf_dir: Union[str, Path],
        text_dir: Union[str, Path] = "./osm_output/pdf_texts",
        converter: str = "sciencebeam",
    ):
        """
        Convert PDFs to text using the specified converter.

        Args:
            pdf_dir: Directory containing PDF files.
            text_dir: Directory to store extracted text. Defaults to "./osm_output/pdf_texts".
            converter: PDF conversion method to use. Defaults to "sciencebeam".
        """
        self._pdf_dir, self._text_dir = setup_dirs(pdf_dir, text_dir)

        if converter not in self.pdf_converters:
            raise ValueError(f"Unknown converter: {converter}")

        self.pdf_converters[converter](self._pdf_dir, self._text_dir)
        return self

    def extract(
        self,
        *,
        text_dir: Union[str, Path] = None,
        outdir: Union[str, Path] = "./osm_output",
        extractor: str = "rtransparent",
    ):
        """
        Extract metrics from text using the specified extractor.

        Args:
            text_dir: Directory containing text files. If not provided, uses the last converted text directory.
            outdir: Directory to output results. Defaults to "./osm_output".
            extractor: Metric extraction method to use. Defaults to "rtransparent".
        """
        if text_dir is None:
            if self._text_dir is None:
                raise ValueError(
                    "No text_dir provided and no previous conversion found."
                )
            text_dir = self._text_dir

        self._text_dir, self._outdir = setup_dirs(text_dir, outdir)

        if extractor not in self.metric_extractors:
            raise ValueError(f"Unknown extractor: {extractor}")

        metrics = self.metric_extractors[extractor](self._text_dir)
        metrics.to_csv(self._outdir / "metrics.csv", index=False)
        return self


def osm():
    fire.Fire(
        {
            "convert": OSM().convert,
            "extract": OSM().extract,
        }
    )


if __name__ == "__main__":
    osm()
