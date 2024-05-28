import pytest
from click.testing import CliRunner
from osm.cli import cli
import logging


@pytest.fixture
def runner():
    return CliRunner()


def test_pdf_to_xml(runner, caplog):
    caplog.set_level(logging.INFO)

    result = runner.invoke(
        cli, ['pdf-xml',
              "example_pdf_inputs/test.pdf",
              '123'
              ])

    assert result.exit_code == 0
    assert 'Converted: example_pdf_inputs/test.pdf with ID: 123 to XML' in caplog.text
