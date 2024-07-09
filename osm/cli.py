import click

from osm.converters import convert_pdf


@click.group()
def osm():
    """Main command for OSM"""
    pass


@osm.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("output_file", type=str)
def rtransparent(file_path, output_file):
    """Processes a biomedical publication. Writes out processed document and associated metrics."""
    convert_pdf(file_path, output_file)
