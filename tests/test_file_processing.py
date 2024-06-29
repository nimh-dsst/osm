from pathlib import Path

import pytest
from click.testing import CliRunner

from osm.cli.main import pdf_xml


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


def test_pdf_xml_command(setup_and_teardown):
    pdfs_folder, file, output_file = setup_and_teardown

    runner = CliRunner()
    pdf_path = f"{pdfs_folder}/{file}"
    result = runner.invoke(pdf_xml, [str(pdf_path), output_file])

    # Check that the command executed successfully
    assert result.exit_code == 0
    assert Path(output_file).exists()
