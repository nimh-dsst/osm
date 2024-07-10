import socket
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests


def pytest_addoption(parser):
    parser.addoption(
        "--rs",
        "--run-slow",
        action="store_true",
        help="Run tests that take a long time >10s to complete",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "run_slow: test takes >10s to complete")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-slow"):
        for item in items:
            try:
                next(m for m in item.iter_markers() if m.name == "run_slow")
            except StopIteration:
                pass
            else:
                item.add_marker(pytest.mark.skip("run with --run-slow"))


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
def sample_pdf(tmp_path):
    pdfs_folder = Path("docs/examples/pdf_inputs")
    file_in = pdfs_folder / "test_sample.pdf"
    output = tmp_path / "test_output_file.xml"
    yield file_in, output
