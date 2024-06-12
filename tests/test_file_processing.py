import logging

import pytest
from click.testing import CliRunner
from pathlib import Path

from osm.cli.main import pdf_xml


@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "test_sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%Test PDF content\n")
    yield pdf_path
    pdf_path.unlink()


def test_pdf_converter(caplog, sample_pdf):
    caplog.set_level(logging.INFO)
    file_id = "test_file"
    output_file = f'docs/examples/sciencebeam_xml_outputs/{file_id}.xml'
    runner = CliRunner()
    result = runner.invoke(pdf_xml, [str(sample_pdf), file_id])
    assert result.exit_code == 0
    assert f"Converted: {sample_pdf}" in caplog.text
    assert Path(output_file).exists()

