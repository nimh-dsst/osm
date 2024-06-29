import click

from osm.converters.converter import convert_pdf_to_xml


@click.group()
def osm():
    """Main command for OSM"""
    pass


@osm.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("output_file", type=str)
def pdf_xml(file_path, output_file):
    """This function converts a file from PDF to XML
    Args:
        file_path (string): an input file path
        output_file (string): an output file path
    Returns:
        Creates an XML file and saves it in the output file path
    """
    try:
        convert_pdf_to_xml(file_path, output_file)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)
