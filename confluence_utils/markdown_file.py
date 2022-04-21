import os
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple

import frontmatter
import mistune
from mistune.plugins import plugin_abbr, plugin_def_list, plugin_task_lists

from .confluence_renderer import ConfluenceRenderer, DirectiveConfluenceToc
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
        page_id: Optional[str] = None,
        parent_file_path: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> None:
        self.absolute_path = absolute_path
        self.filename = filename
        self.directory_name = directory_name
        self.title = title
        self.front_matter = front_matter
        self.markdown_content = markdown_content
        self.page_id = page_id
        self.parent_file_path = parent_file_path
        self.parent_id = parent_id

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
            page_id=front_matter.get("page_id"),
            parent_file_path=front_matter.get("parent_file_path"),
            parent_id=front_matter.get("parent_id"),
        )

    def update_front_matter(self) -> None:
        file = frontmatter.load(self.absolute_path)
        file.metadata["page_id"] = self.page_id
        file.metadata["parent_id"] = self.parent_id
        with open(self.absolute_path, "w") as update_file:
            f = BytesIO()
            frontmatter.dump(file, f)
            update_file.write(f.getvalue().decode("utf-8"))

    def render_confluence_content(self) -> Tuple[str, List[str]]:
        renderer = ConfluenceRenderer()
        markdown = mistune.Markdown(
            renderer,
            plugins=[
                plugin_task_lists,
                plugin_def_list,
                plugin_abbr,
                DirectiveConfluenceToc(),
            ],
        )
        body = markdown(self.markdown_content)
        attachments: List[str] = []

        return body, attachments
