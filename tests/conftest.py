import socket
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests


@pytest.fixture
def mocked_socket():
    mock_sock_instance = MagicMock(spec=socket.socket)
    mock_sock_instance.connect.return_value = None  # Simulate successful connect

    # Handle context management
    mock_sock_instance.__enter__.return_value = mock_sock_instance
    mock_sock_instance.__exit__.return_value = None
    return mock_sock_instance


@pytest.fixture
def mocked_requests_post():
    tei_data = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <text>
            <body>
                <p>This is a mocked TEI response.</p>
            </body>
        </text>
    </TEI>
    """
    mock_requests_post = MagicMock(spec=requests.post)
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.text = tei_data
    mock_requests_post.return_value = mock_response
    return mock_requests_post


@pytest.fixture
def pdf_setup(tmp_path):
    pdfs_folder = Path("docs/examples/pdf_inputs")
    file_in = pdfs_folder / "test_sample.pdf"
    output = tmp_path / "test_output_file.xml"
    yield file_in, output
