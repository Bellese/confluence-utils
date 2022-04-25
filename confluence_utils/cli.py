import os
from typing import List, Optional

import click
from atlassian import Confluence
from atlassian.errors import ApiError
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
        envvar=["CONFLUENCE_URL"],
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
        publish_file(path, space, confluence)
    elif os.path.isdir(path):
        for file in get_files(path, ".md"):
            publish_file(file, space, confluence)


def publish_file(path: str, space: str, confluence: Confluence) -> None:
    markdown_file = MarkdownFile.from_path(path, space)

    if markdown_file.parent_file_path is not None:
        parent_path = os.path.join(
            os.path.dirname(path),
            markdown_file.parent_file_path,
        )
        if not os.path.isfile(parent_path):
            click.echo(f"parent page does not exist skipping: {path}")
            return

        parent_file = MarkdownFile.from_path(parent_path, space)
        # maybe add space validation here
        if parent_file.page_id is not None:
            markdown_file.parent_id = parent_file.page_id
            markdown_file.update_front_matter(space)
        elif parent_file.page_id is None:
            # check if the page exist but the page id is not set
            if confluence.page_exists(space=space, title=parent_file.title):
                parent_id = confluence.get_page_id(space, parent_file.title)
                parent_file.page_id = parent_id
                markdown_file.parent_id = parent_id
                markdown_file.update_front_matter(space)
                parent_file.update_front_matter(space)
            else:
                click.echo(f"parent page does not exist skipping: {path}")
                return

    body, attachments = markdown_file.render_confluence_content()
    page_with_title_exist = confluence.page_exists(
        space=space, title=markdown_file.title
    )

    if not markdown_file.page_id and page_with_title_exist:
        page_id = confluence.get_page_id(space, markdown_file.title)
        markdown_file.page_id = page_id
        markdown_file.update_front_matter(space)
        update_page_response = confluence.update_page(
            page_id=markdown_file.page_id,
            title=markdown_file.title,
            body=body,
            parent_id=markdown_file.parent_id,
        )
        click.echo(
            f"Updated page with page_id {update_page_response.get('id')}"
        )
    elif markdown_file.page_id and page_with_title_exist:
        # look up page id to make sure confluence is aware of it
        checkedSpace = None
        try:
            checkedSpace = confluence.get_page_space(markdown_file.page_id)
        except ApiError:
            pass
        if checkedSpace is None or checkedSpace != space:
            # the page exist but the page id is bung so fix the page id
            page_id = confluence.get_page_id(space, markdown_file.title)
            markdown_file.page_id = page_id
            markdown_file.update_front_matter(space)

        update_page_response = confluence.update_page(
            page_id=markdown_file.page_id,
            title=markdown_file.title,
            body=body,
            parent_id=markdown_file.parent_id,
        )

        click.echo(
            f"Updated page with page_id {update_page_response.get('id')}"
        )
    else:
        create_page_response = confluence.create_page(
            space=space,
            title=markdown_file.title,
            body=body,
            parent_id=markdown_file.parent_id,
        )
        page_id = create_page_response.get("id")
        markdown_file.page_id = page_id
        markdown_file.update_front_matter(space)

    for attachment in attachments:
        attachment_absolution_path = os.path.join(
            markdown_file.directory_name, attachment
        )
        attachment_filename = os.path.basename(attachment_absolution_path)

        confluence.attach_file(
            filename=attachment_absolution_path,
            name=attachment_filename,
            page_id=page_id,
            space=space,
            parent_id=markdown_file.parent_id,
        )


def get_files(path: str, extension_filter: Optional[str] = None) -> List[str]:
    files = []
    for root, d_names, f_names in os.walk(path):
        for f in f_names:
            files.append(os.path.join(root, f))
    if extension_filter:
        return [s for s in files if s.endswith(extension_filter)]
    else:
        return files
