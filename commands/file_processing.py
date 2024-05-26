import click
from logs.logger import logger

@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('file_id', type=str)
def pdf_xml(file_path, file_id):
    """This function converts a file from PDF
        to XML

    Args:
        file_paht (file path): First parameter
        file_id (string): Second parameter
    Returns:
        Creates an XML file in the directory xmls_sciencebeam
    """

    # Function Implementation
    logger.info(f'Converted: {file_path} with ID: {file_id} to XML')
