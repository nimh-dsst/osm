from pathlib import Path

import pytest
from click.testing import CliRunner

from osm.cli.main import pdf_xml_json


@pytest.fixture
def mock_socket(mocker):
    mock_socket = mocker.patch("socket.socket")
    mock_sock_instance = mock_socket.return_value.__enter__.return_value
    yield mock_sock_instance


@pytest.fixture
def mock_requests_convert(mocker):
    yield mocker.patch("requests.post")


@pytest.fixture
def setup_and_teardown():
    # Setup: Create a temporary PDF file for testing
    pdfs_folder = "docs/examples/pdf_inputs"
    file = "test_sample.pdf"
    output_file = "test_output_file.xml"

    yield pdfs_folder, file, output_file

    # Teardown: Remove the generated XML file
    output_file_path = Path(output_file)
    if output_file_path.exists():
        output_file_path.unlink()


def test_pdf_xml_command(setup_and_teardown, mock_socket, mock_requests_convert):
    pdfs_folder, file, output_file = setup_and_teardown

    mock_socket.connect.return_value = None  # Simulate successful connect

    tei_data = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <text>
        <body>
          <p>This is a mocked TEI response.</p>
        </body>
      </text>
    </TEI>
    """
    mock_requests_convert.return_value.status_code = 200
    mock_requests_convert.return_value.text = tei_data

    runner = CliRunner()
    pdf_path = f"{pdfs_folder}/{file}"
    result = runner.invoke(pdf_xml_json, [str(pdf_path), output_file])

    # Check that the command executed successfully
    assert result.exit_code == 0
    assert Path(output_file).exists()
