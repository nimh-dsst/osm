import unittest
from click.testing import CliRunner
import os

from osm.cli import cli


class TestFileProcessing(unittest.TestCase):
    def setUp(self):
        # Create a temporary PDF file for testing
        self.pdfs_folder = 'docs/examples/pdf_inputs'
        self.file = 'test_sample.pdf'
        self.file_id = 'test_file_id'

        self.output_file = f'docs/examples/sciencebeam_xml_outputs/{self.file_id}.xml'

    def tearDown(self):
        # Remove the generated XML file
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_pdf_xml_command(self):
        runner = CliRunner()
        pdf_path = f'{self.pdfs_folder}/{self.file}'
        result = runner.invoke(cli, ['pdf-xml', pdf_path, self.file_id])

        # Check that the command executed successfully
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(self.output_file))


if __name__ == '__main__':
    unittest.main()
