import socket
from abc import ABC, abstractmethod
from pathlib import Path

import requests

from osm.logging.logger import logger
from osm.utils.config import config


class Converter(ABC):
    @abstractmethod
    def convert(self, pdf_path) -> str:
        pass

    def handle_error(self, error):
        if isinstance(error, requests.RequestException):
            logger.error("Request error:", exc_info=error)
        else:
            logger.error("An error occurred:", exc_info=error)

        raise error


class PDFConverter(Converter):
    protocol: str = config.PROTOCOL
    host: str = config.HOST
    port: int = config.PORT

    def convert(self, pdf_path) -> str:
        """Convert a PDF file to XML using ScienceBeam Parser.

        Args:
            pdf_path: Path to the PDF file
        Returns:
            XML content as a string
        """
        sciencebeam_url: str = f"{self.protocol}://{self.host}:{self.port}/api/convert"
        with Path(pdf_path).open("rb") as pdf_file:
            files = {"file": pdf_file}
            headers = {"Accept": "application/tei+xml"}
            response = requests.post(sciencebeam_url, files=files, headers=headers)

            if response.status_code == 200:
                return response.text
            else:
                response.raise_for_status()

    def is_host_ready(self, timeout=3) -> bool:
        """Check if the host is ready to accept requests.
        Args:
            timeout: Timeout in seconds
        Returns:
            True if the docker is host is ready, False otherwise
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            try:
                sock.connect((self.host, self.port))
            except (socket.timeout, socket.error):
                return False
            return True


def convert_pdf_to_xml(file_path, output_file_path):
    """Converts a PDF file to XML and saves the output.

    Args:
        file_path (str): Path to the input PDF file.
        output_file_path (str): Path to the output XML file.
    """
    converter = PDFConverter()
    try:
        if not converter.is_host_ready():
            raise Exception("The converter server is offline")

        xml_content = converter.convert(file_path)

        # Save the converted xml contents
        Path(output_file_path).write_text(xml_content)
        logger.info(f"Converted: {file_path} to XML. Output file: {output_file_path}")

    except requests.RequestException as error:
        converter.handle_error(error)

    except Exception as error:
        converter.handle_error(error)
