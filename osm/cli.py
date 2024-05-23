import click
from commands.file_processing import pdf_xml

@click.group()
def cli():
    """Main command group."""
    pass

# Add commands to the main group
cli.add_command(pdf_xml)

if __name__ == '__main__':
    cli()