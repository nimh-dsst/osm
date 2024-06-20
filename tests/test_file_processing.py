import pytest
from click.testing import CliRunner
import os
import logging

from commands.file_processing import pdf_xml


@pytest.mark.usefixtures("caplog")
class TestFileProcessing:
    def setup_method(self):
        # Create a temporary PDF file for testing
        self.pdf_path = "test_sample.pdf"
        with open(self.pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n%Test PDF content\n")

    def teardown_method(self):
        # Remove the temporary PDF file and any generated XML file
        if os.path.exists(self.pdf_path):
            os.remove(self.pdf_path)
        xml_output = f"{self.pdf_path.replace('.pdf', '')}_test_file.xml"
        if os.path.exists(xml_output):
            os.remove(xml_output)

    def test_pdf_xml_command(self, caplog):
        caplog.set_level(logging.INFO)

        runner = CliRunner()
        result = runner.invoke(pdf_xml, [self.pdf_path, "test_file"])

        assert result.exit_code == 0
        assert f"Converted: {self.pdf_path}" in caplog.text
