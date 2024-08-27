import requests

from osm.schemas.custom_fields import LongBytes

from .core import Component
import io

SCIENCEBEAM_URL = "http://localhost:8070/api/convert"


class NoopParser(Component):
    """Used if the input is xml and so needs no parsing."""

    def _run(self, data: bytes) -> bytes:
        return data


class PMCParser(NoopParser):
    """
    Used if the input is a PMC derived XML and so needs no parsing. PMC
    parsed XMLs can have unique features. For example RTransparent extracts
    additional metadata from them aided by the document structure. Sometimes
    data sharing statements etc. may not be in the PMC parsed XML despite being
    in the pdf version of the publication.
    """

    pass


class ScienceBeamParser(Component):
    def _run(self, data: bytes) -> str:
        self.sample = LongBytes(data)
        headers = {"Accept": "application/tei+xml", "Content-Type": "application/pdf"}
        files = {'file': ('input.pdf', io.BytesIO(data), 'application/pdf')}

        response = requests.post(SCIENCEBEAM_URL, files=files, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            response.raise_for_status()
