import os
from typing import Any, Dict, List, Tuple

import mistune

from .confluence_renderer import ConfluenceRenderer
from .markdown_parser import parse


class MarkdownFile:
    def __init__(
        self,
        absolute_path: str,
        filename: str,
        directory_name: str,
        title: str,
        front_matter: Dict[str, Any],
        markdown_content: str,
    ) -> None:
        self.absolute_path = absolute_path
        self.filename = filename
        self.directory_name = directory_name
        self.title = title
        self.front_matter = front_matter
        self.markdown_content = markdown_content

    @classmethod
    def from_path(cls, absolute_path: str) -> "MarkdownFile":
        markdown_content, front_matter = parse(absolute_path)
        return MarkdownFile(
            absolute_path=absolute_path,
            filename=os.path.basename(absolute_path),
            directory_name=os.path.dirname(absolute_path),
            title=front_matter.get("title"),
            front_matter=front_matter,
            markdown_content=markdown_content,
        )

    def render_confluence_content(self) -> Tuple[str, List[str]]:
        author_keys = self.front_matter.get("author_keys", [])
        renderer = ConfluenceRenderer(authors=author_keys)
        html_content = mistune.markdown(
            self.markdown_content, renderer=renderer
        )
        body = renderer.single_column_layout(html_content)
        attachments = renderer.attachments

        return body, attachments
