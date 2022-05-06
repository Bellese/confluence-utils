import os
import sys
from typing import List, Optional

import click
from atlassian import Confluence
from tabulate import tabulate

from . import __version__
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
@click.version_option(version=__version__, prog_name="confluence-utils")
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
@click.option(
    "--ignore-path",
    "ignore_paths",
    multiple=True,
    help="Paths to ignore when converting markdown",
    type=click.Path(exists=True, resolve_path=True),
)
def publish(
    path: str,
    url: str,
    space: str,
    token: str,
    ignore_paths: List[str] = [],
) -> None:
    try:
        confluence = Confluence(
            url=url,
            token=token,
        )

        space_information = confluence.get_space(space)
        homepage = space_information.get("homepage")
        homepage_id = None
        if homepage is not None:
            homepage_id = homepage.get("id")

        if (
            os.path.isfile(path)
            and path.endswith(".md")
            and not subpath_in_paths(ignore_paths, path)
        ):
            publish_files([path], space, confluence, homepage_id)

        elif os.path.isdir(path):
            publish_files(
                get_files(path, ".md", ignore_paths),
                space,
                confluence,
                homepage_id,
            )

    except click.ClickException as e:
        e.show()
        sys.exit(e.exit_code)


def publish_files(
    paths: List[str],
    space: str,
    confluence: Confluence,
    default_parent_id: Optional[str] = None,
) -> None:
    for path in paths:
        try:
            markdown_file = MarkdownFile(path)
            markdown_file.resolve_links()

            # maybe add space validation here
            if (
                markdown_file.parent is not None
                and markdown_file.parent.get_page_id_for_space(space) is None
            ):
                # check if the page exist but the page id is not set
                if confluence.page_exists(
                    space=space, title=markdown_file.parent.title
                ):
                    parent_page_id = confluence.get_page_id(
                        space, markdown_file.parent.title
                    )
                    markdown_file.parent.set_page_id_for_space(
                        parent_page_id, space
                    )
                else:
                    raise click.ClickException(
                        "Parent page does not exist:"
                        f" {markdown_file.parent_file_path}"
                    )

            page_with_title_exist = confluence.page_exists(
                space=space, title=markdown_file.title
            )

            if (
                not markdown_file.get_page_id_for_space(space)
                and page_with_title_exist
            ):
                page_id = confluence.get_page_id(space, markdown_file.title)
                markdown_file.set_page_id_for_space(page_id, space)
                confluence.update_page(
                    page_id=markdown_file.get_page_id_for_space(space),
                    title=markdown_file.title,
                    body=markdown_file.html,
                    parent_id=markdown_file.parent.get_page_id_for_space(space)
                    if markdown_file.parent
                    else default_parent_id,
                )
                click.echo(
                    "Updated page with page_id"
                    f" {markdown_file.get_page_id_for_space(space)}"
                )
            elif (
                markdown_file.get_page_id_for_space(space)
                and page_with_title_exist
            ):
                # this could be a rename operation validate valid name
                saved_page_id = confluence.get_page_id(
                    space, markdown_file.title
                )
                if markdown_file.get_page_id_for_space(space) != saved_page_id:
                    raise click.ClickException(
                        "Could not update to new title. Page with title"
                        f" {markdown_file.title} already exists"
                    )

                confluence.update_page(
                    page_id=markdown_file.get_page_id_for_space(space),
                    title=markdown_file.title,
                    body=markdown_file.html,
                    parent_id=markdown_file.parent.get_page_id_for_space(space)
                    if markdown_file.parent
                    else default_parent_id,
                )

                click.echo(
                    "Updated page with page_id"
                    f" {markdown_file.get_page_id_for_space(space)}"
                )
            else:
                create_page_response = confluence.create_page(
                    space=space,
                    title=markdown_file.title,
                    body=markdown_file.html,
                    parent_id=markdown_file.parent.get_page_id_for_space(space)
                    if markdown_file.parent
                    else default_parent_id,
                )
                page_id = create_page_response.get("id")
                markdown_file.set_page_id_for_space(page_id, space)

                click.echo(f"Created page with page_id {page_id}")

            if markdown_file.get_page_id_for_space(space):
                for attachment in markdown_file.attachments:
                    confluence.attach_file(
                        filename=attachment,
                        name=os.path.basename(attachment),
                        page_id=markdown_file.get_page_id_for_space(space),
                        space=space,
                    )

        except FileNotFoundError as e:
            raise click.FileError(path, hint=str(e))


def get_files(
    path: str,
    extension_filter: Optional[str] = None,
    ignore_paths: List[str] = [],
) -> List[str]:
    files = []
    for root, d_names, f_names in os.walk(path):
        for f in f_names:
            current_path = os.path.join(root, f)
            if subpath_in_paths(ignore_paths, current_path):
                continue
            else:
                files.append(current_path)

    if extension_filter:
        return [s for s in files if s.endswith(extension_filter)]
    else:
        return files


def subpath_in_paths(paths: List[str], subpath: str) -> bool:
    for path in paths:
        if os.path.commonpath([path]) == os.path.commonpath([path, subpath]):
            return True
    return False
