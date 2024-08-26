import requests

from osm.schemas.custom_fields import LongBytes

from .core import Component

SCIENCEBEAM_URL = "http://localhost:8070/api/convert"


class NoopParser(Component):
    """Used if the input is xml and so needs no parsing."""

    def run(self, data: bytes) -> str:
        self.sample = LongBytes(data)
        return data.decode("utf-8")


class ScienceBeamParser(Component):
    def run(self, data: bytes) -> str:
        self.sample = LongBytes(data)
        headers = {"Accept": "application/tei+xml", "Content-Type": "application/pdf"}
        response = requests.post(SCIENCEBEAM_URL, data=data, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            response.raise_for_status()
