import os
from typing import List, Optional

import click
from atlassian import Confluence
from tabulate import tabulate

from .markdown_file import MarkdownFile


def client_options(function):  # type: ignore
    function = click.option(
        "--url",
        required=True,
        help=(
            "The URL to the Confluence API. Optionally set with"
            " CONFLUENCE_URL."
        ),
        envvar=["CONFLUENCE_API_URL"],
    )(function)
    function = click.option(
        "--space",
        required=True,
        help="Confluence Space. Optionally set with CONFLUENCE_SPACE.",
        envvar=["CONFLUENCE_SPACE"],
    )(function)
    function = click.option(
        "--token",
        required=True,
        help="Confluence API Token. Optionally set with CONFLUENCE_TOKEN.",
        envvar=["CONFLUENCE_TOKEN"],
    )(function)
    return function


@click.group()
@click.version_option(prog_name="confluence-utils")
def cli() -> None:
    """Commandline utils for Confluence."""


@cli.command(name="list-pages")
@client_options
def list_pages(url: str, space: str, token: str) -> None:

    confluence = Confluence(
        url=url,
        token=token,
    )

    pages = confluence.get_all_pages_from_space(space)

    table = []

    for page in pages:
        table.append(
            {
                "id": page.get("id"),
                "title": page.get("title"),
                "url": page.get("_links").get("self"),
            }
        )

    click.echo(tabulate(table, headers="keys", tablefmt="fancy_grid"))


@cli.command()
@client_options
@click.argument("path", type=click.Path(exists=True, resolve_path=True))
def publish(path: str, url: str, space: str, token: str) -> None:
    confluence = Confluence(
        url=url,
        token=token,
    )

    if os.path.isfile(path) and path.endswith(".md"):

        markdown_file = MarkdownFile.from_path(path)

        click.echo(
            f"Publishing file: {markdown_file.filename} in"
            f" {markdown_file.directory_name}"
        )

        body, attachments = markdown_file.render_confluence_content()

        create_page_response = confluence.create_page(
            space=space, title=markdown_file.title, body=body
        )

        for attachment in attachments:
            attachment_absolution_path = os.path.join(
                markdown_file.directory_name, attachment
            )
            attachment_filename = os.path.basename(attachment_absolution_path)

            confluence.attach_file(
                filename=attachment_absolution_path,
                name=attachment_filename,
                page_id=create_page_response.get("page_id"),
                space=space,
            )
    else:
        click.echo(f"publishing directory: {path}")
        click.echo(get_files(path, ".md"))


def get_files(path: str, extension_filter: Optional[str] = None) -> List[str]:
    files = []
    for root, d_names, f_names in os.walk(path):
        for f in f_names:
            files.append(os.path.join(root, f))
    if extension_filter:
        return [s for s in files if s.endswith(extension_filter)]
    else:
        return files
