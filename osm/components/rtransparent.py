import json

import requests


def _extract(xml: bytes) -> str:
    """Extracts metrics from an XML.

    Args:
        xml: Raw bytes for an xml file.
    """
    headers = {"Content-Type": "application/octet-stream"}
    response = requests.post(
        "http://localhost:8071/extract-metrics", data=xml, headers=headers
    )
    if response.status_code == 200:
        return json.loads(response.json())[0]
    else:
        response.raise_for_status()
