import click

from osm.converters.converter import convert_pdf_to_xml


@click.group()
def osm():
    """Main command for OSM"""
    pass


@osm.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("output_file", type=str)
def pdf_xml_json(file_path, output_file):
    """Converts a PDF file of a biomedical publication to JSON format
    Args:
        file_path (string): Path to the input PDF file
        output_file (string): an output file path
    Returns:
        Creates an JSON file containing bibliometric
        indicators and metadata and saves it in the
        output file path
    """
    try:
        convert_pdf_to_xml(file_path, output_file)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)
