from pydantic import FilePath
import requests

from commands.converters.converter import Converter


class PDFConverter(Converter):
    sciencebeam_url: str = 'http://localhost:8080/api/convert'

    def convert(self, pdf_path: FilePath):
        """Convert a PDF file to XML using ScienceBeam Parser.

        Args:
            pdf_path: Path to the PDF file
        Returns:
            XML content as a string
        """
        with open(pdf_path, 'rb') as pdf_file:
            files = {'file': pdf_file}
            headers = {'Accept': 'application/tei+xml'}
            response = requests.post(self.sciencebeam_url, files=files, headers=headers)

            if response.status_code == 200:
                return response.text
            else:
                response.raise_for_status()
