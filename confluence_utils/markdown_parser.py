from typing import Any, Tuple

import frontmatter


def parse(path: str) -> Tuple[str, Any]:
    """Parses a markdown file at a given path and returns a
    tuple containing the frontmatter and markdown content.

    Arguments:
        path {str} -- The absolute path to the Markdown post
    """
    with open(path, "r") as post:
        obj = frontmatter.load(post)
        front_matter = obj.metadata
        markdown = obj.content

    return markdown, front_matter
