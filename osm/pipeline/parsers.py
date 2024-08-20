import requests

from .core import Component

SCIENCEBEAM_URL = "http://localhost:8070/api/convert"


class NoopParser(Component):
    def run(self, data: bytes) -> str:
        return data.decode("utf-8")


class ScienceBeamParser(Component):
    def run(self, data: bytes) -> str:
        headers = {"Accept": "application/tei+xml", "Content-Type": "application/pdf"}
        response = requests.post(SCIENCEBEAM_URL, data=data, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            response.raise_for_status()
