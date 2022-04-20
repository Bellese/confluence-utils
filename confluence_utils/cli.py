import os

import click


@click.group()
@click.version_option(prog_name="confluence-utils")
def cli() -> None:
    """Commandline interface for Confluence."""


@cli.command()
@click.option(
    "--url",
    required=True,
    help="The URL to the Confluence API. Optionally set with CONFLUENCE_URL.",
    envvar=["CONFLUENCE_API_URL"],
)
@click.option(
    "--space",
    required=True,
    help="Confluence API Space. Optionally set with CONFLUENCE_SPACE.",
    envvar=["CONFLUENCE_SPACE"],
)
@click.option(
    "--token",
    required=True,
    help="Confluence API Token. Optionally set with CONFLUENCE_TOKEN.",
    envvar=["CONFLUENCE_TOKEN"],
)
@click.argument("path", type=click.Path(exists=True, resolve_path=True))
def publish(path: click.Path, url: str, space: str, token: str) -> None:
    if os.path.isfile(path):
        click.echo(f"publishing file: {path}")
    else:
        click.echo(f"publishing directory: {path}")
    click.echo(url)
    click.echo(space)
    click.echo(token)
