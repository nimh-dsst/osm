import socket

import docker
from docker.errors import DockerException
from pydantic import FilePath
import requests

from osm_cli.converters.converter import Converter
from osm_cli.utils.config import config


class PDFConverter(Converter):
    protocol: str = config.PROTOCAL
    host: str = config.HOST
    port: int = config.PORT

    def convert(self, pdf_path: FilePath) -> str:
        """Convert a PDF file to XML using ScienceBeam Parser.

        Args:
            pdf_path: Path to the PDF file
        Returns:
            XML content as a string
        """
        sciencebeam_url: str = f'{self.protocol}://{self.host}:{self.port}/api/convert'
        with open(pdf_path, 'rb') as pdf_file:
            files = {'file': pdf_file}
            headers = {'Accept': 'application/tei+xml'}
            response = requests.post(
                sciencebeam_url, files=files, headers=headers)

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

    def is_docker_running(self):
        """Check if the docker image exists.
        Returns:
            True if the docker image exists, False otherwise
        """
        try:
            client = docker.from_env()
            client.images.get('elifesciences/sciencebeam-parser')
            return True
        except DockerException:
            return False
