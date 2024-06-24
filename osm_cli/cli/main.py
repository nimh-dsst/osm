import click

from osm_cli.logging.logger import logger


@click.group()
def osm():
    """Main command for OSM"""
    pass


@osm.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("file_id", type=str)
def pdf_xml(file_path, file_id):
    """This function converts a file from PDF to XML"""
    # Function Implementation
    logger.info(f"Converted: {file_path} with ID: {file_id} to XML")
