import logging
from pathlib import Path

import pytest
from click.testing import CliRunner

from osm_cli.cli.file_processing import pdf_xml


@pytest.fixture
def sample_pdf():
    pdf_path = Path("test_sample.pdf")
    pdf_path.write_bytes(b"%PDF-1.4\n%Test PDF content\n")
    yield pdf_path
    pdf_path.unlink()


def test_pdf_converter(caplog, sample_pdf):
    caplog.set_level(logging.INFO)
    runner = CliRunner()
    result = runner.invoke(pdf_xml, [str(sample_pdf), "test_file"])
    assert result.exit_code == 0
    assert f"Converted: {sample_pdf}" in caplog.text
