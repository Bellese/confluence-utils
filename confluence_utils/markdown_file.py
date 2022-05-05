import os
from io import BytesIO
from typing import List, Optional

import frontmatter
import mistune
from mistune.plugins import (
    plugin_abbr,
    plugin_def_list,
    plugin_table,
    plugin_task_lists,
)

from .confluence_directives import (
    DirectiveConfluenceStyles,
    DirectiveConfluenceToc,
)
from .confluence_renderer import ConfluenceRenderer
from .markdown_parser import parse


class MarkdownFile(object):
    def __init__(
        self,
        path: str,
    ) -> None:
        self.path = path

        raw_markdown, front_matter = parse(path)

        self._raw_markdown = raw_markdown
        self._front_matter = front_matter

        renderer = ConfluenceRenderer()

        md = mistune.Markdown(
            renderer,
            plugins=[
                plugin_task_lists,
                plugin_def_list,
                plugin_abbr,
                plugin_table,
                DirectiveConfluenceToc(),
                DirectiveConfluenceStyles(os.path.dirname(self.path)),
            ],
        )

        self.html = md(self._raw_markdown)
        self.links = {}
        for link in renderer.links:
            resolved_link = os.path.normpath(
                os.path.join(
                    os.path.dirname(self.path),
                    link,
                )
            )
            self.links[resolved_link] = renderer.links[link]

        self._attachments = renderer.attachments

    @property
    def title(self) -> Optional[str]:
        return self._get_attribute("title")

    @title.setter
    def title(self, title: str) -> None:
        self._set_attribute("title", title)

    @property
    def attachments(self) -> List[str]:
        return [
            os.path.normpath(
                os.path.join(os.path.dirname(self.path), attachment)
            )
            for attachment in self._attachments
        ]

    def _get_attribute(self, attribute_name: str) -> Optional[str]:
        return self._front_matter.get(attribute_name, None)

    def _set_attribute(self, attribute_name: str, value: str) -> None:
        self._front_matter[attribute_name] = value
        self._save()

    def _get_attribute_for_space(
        self, attribute_name: str, space_key: str
    ) -> Optional[str]:
        return (
            self._front_matter.get("spaces", {})
            .get(space_key, {})
            .get(attribute_name, None)
        )

    def _set_attribute_for_space(
        self, attribute_name: str, space_key: str, value: str
    ) -> None:
        spaces = self._front_matter.get("spaces", {})
        space = spaces.get(space_key, {})
        space[attribute_name] = value
        spaces[space_key] = space
        self._front_matter["spaces"] = spaces
        self._save()

    def get_page_id_for_space(self, space_key: str) -> Optional[str]:
        return self._get_attribute_for_space("page_id", space_key)

    def set_page_id_for_space(self, page_id: str, space_key: str) -> None:
        self._set_attribute_for_space("page_id", space_key, page_id)

    def get_parent_page_id_for_space(self, space_key: str) -> Optional[str]:
        return self._get_attribute_for_space("parent_page_id", space_key)

    def set_parent_page_id_for_space(
        self, parent_page_id: str, space_key: str
    ) -> None:
        self._set_attribute_for_space(
            "parent_page_id", space_key, parent_page_id
        )

    @property
    def parent_file_path(self) -> Optional[str]:
        parent_file_path = self._get_attribute("parent_file_path")
        return (
            os.path.normpath(
                os.path.join(
                    os.path.dirname(self.path),
                    parent_file_path,
                )
            )
            if parent_file_path is not None
            else None
        )

    @property
    def parent(self) -> Optional["MarkdownFile"]:
        return (
            MarkdownFile(self.parent_file_path)
            if self.parent_file_path is not None
            else None
        )

    def resolve_links(self) -> None:
        for link in self.links:
            temporary_file = MarkdownFile(link)
            self.html = self.html.replace(
                self.links[link], temporary_file.title
            )

    def _save(self) -> None:
        file = frontmatter.load(self.path)
        for key, value in self._front_matter.items():
            file.metadata[key] = value
        with open(self.path, "w") as update_file:
            f = BytesIO()
            frontmatter.dump(file, f)
            update_file.write(f.getvalue().decode("utf-8"))
        self._front_matter = file.metadata
