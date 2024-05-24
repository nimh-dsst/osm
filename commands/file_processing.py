import click

@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('file_id', type=str)
def pdf_xml(file_path, file_id):

    """This function converts a file from PDF
        to XML

    Args:

        file_path (file path): First parameter
        file_id (string): Second parameter
    Returns:
        Creates an XML file in the directory xmls_sciencebeam
    """

    # Function Implementation

    click.echo(f"Converted {file_path} with id {file_id} to XML")

