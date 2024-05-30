import unittest
from click.testing import CliRunner
import os

from commands.file_processing import pdf_xml


class TestFileProcessing(unittest.TestCase):
    def setUp(self):
        # Create a temporary PDF file for testing
        self.pdf_path = 'test_sample.pdf'
        with open(self.pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n%Test PDF content\n')

    def tearDown(self):
        # Remove the temporary PDF file and any generated XML file
        if os.path.exists(self.pdf_path):
            os.remove(self.pdf_path)
        xml_output = f"{self.pdf_path.replace('.pdf', '')}_test_file.xml"
        if os.path.exists(xml_output):
            os.remove(xml_output)

    def test_pdf_xml_command(self):
        runner = CliRunner()
        result = runner.invoke(pdf_xml, [self.pdf_path, 'test_file'])

        # Check that the command executed successfully
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Converted test_sample.pdf', result.output)


if __name__ == '__main__':
    unittest.main()
