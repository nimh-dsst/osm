import socket
from abc import ABC, abstractmethod
from pathlib import Path

import requests

from osm.config import osm_config
from osm.logging import logger


class Converter(ABC):
    @abstractmethod
    def convert(self, pdf_path) -> str:
        pass


class PDFConverter(Converter):
    sb_protocol: str = osm_config.sb_protocol
    sb_host: str = osm_config.sb_host
    sb_port: int = osm_config.sb_port

    def convert(self, pdf_path) -> str:
        """Convert a PDF file to XML using ScienceBeam Parser.

        Args:
            pdf_path: Path to the PDF file
        Returns:
            XML content as a string
        """
        sciencebeam_url: str = (
            f"{self.sb_protocol}://{self.sb_host}:{self.sb_port}/api/convert"
        )
        if not self._is_host_ready():
            raise Exception(
                f"Cannot access the ScienceBeam Parser service:\n {sciencebeam_url}"
            )
        headers = {"Accept": "application/tei+xml", "Content-Type": "application/pdf"}
        response = requests.post(
            sciencebeam_url, data=Path(pdf_path).read_bytes(), headers=headers
        )

        if response.status_code == 200:
            return response.text
        else:
            response.raise_for_status()

    def _is_host_ready(self, timeout=3) -> bool:
        """Check if the host is ready to accept requests.
        Args:
            timeout: Timeout in seconds
        Returns:
            True if the server host is ready, False otherwise
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            try:
                sock.connect((self.sb_host, self.sb_port))
            except (socket.timeout, socket.error):
                return False
            return True


def convert_pdf(file_path, output_file_path):
    """Converts a PDF file to XML and saves the output.

    Args:
        file_path (str): Path to the input PDF file.
        output_file_path (str): Path to the output XML file.
    """
    converter = PDFConverter()
    xml_content = converter.convert(file_path)

    # Save the converted xml contents
    Path(output_file_path).write_text(xml_content)
    logger.info(f"Converted: {file_path} to XML. Output file: {output_file_path}")
