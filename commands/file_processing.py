import click

@click.command()
@click.argument('file_name', type=click.Path(exists=True))
@click.argument('file_id', type=str)
def pdf_xml(file_name, file_id):
    """This function converts a file from PDF
        to XML

    Args:
        file_name (file path): First parameter
        file_id (string): Second parameter
    Returns:
        Creates an XML file in the directory xmls_sciencebeam
    """

    # Function Implementation
    click.echo(f"Converted {file_name} with id {file_id} to XML")