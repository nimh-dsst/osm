import requests

SCIENCEBEAM_URL = "http://localhost:8070/api/convert"


def _convert(pdf: bytes) -> str:
    """Converts a PDF to a an XML.

    Args:
        pdf: Path to the input PDF file.
    """
    headers = {"Accept": "application/tei+xml", "Content-Type": "application/pdf"}
    response = requests.post(SCIENCEBEAM_URL, data=pdf, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        response.raise_for_status()
