import pytest
from click.testing import CliRunner
import os

from osm.cli import cli


@pytest.fixture
def setup_and_teardown():
    # Setup: Create a temporary PDF file for testing
    pdfs_folder = 'docs/examples/pdf_inputs'
    file = 'test_sample.pdf'
    file_id = 'test_file_id'
    output_file = f'docs/examples/sciencebeam_xml_outputs/{file_id}.xml'

    yield pdfs_folder, file, file_id, output_file

    # Teardown: Remove the generated XML file
    if os.path.exists(output_file):
        os.remove(output_file)


def test_pdf_xml_command(setup_and_teardown):
    pdfs_folder, file, file_id, output_file = setup_and_teardown

    runner = CliRunner()
    pdf_path = f'{pdfs_folder}/{file}'
    result = runner.invoke(cli, ['pdf-xml', pdf_path, file_id])

    # Check that the command executed successfully
    assert result.exit_code == 0
    assert os.path.exists(output_file)
