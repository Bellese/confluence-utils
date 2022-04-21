import os
import textwrap
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import mistune


def convert_to_confluence_content(
    markdown: str, front_matter: Optional[Dict[str, Any]] = None
) -> Tuple[str, List[Any]]:
    if front_matter is None:
        front_matter = {}
    author_keys = front_matter.get("author_keys", [])
    renderer = ConfluenceRenderer(authors=author_keys)
    content_html = mistune.markdown(markdown, renderer=renderer)
    page_html = renderer.single_column_layout(content_html)

    return page_html, renderer.attachments


class ConfluenceRenderer(mistune.HTMLRenderer):
    def __init__(self, authors: Optional[List[Any]] = None) -> None:
        if authors is None:
            authors = []
        self.attachments: List[Any] = []
        if authors is None:
            authors = []
        self.authors = authors
        self.has_toc = False
        super().__init__()

    def single_column_layout(self, content: Any) -> str:
        """Renders the final layout of the content. This includes a two-column
        layout, with the authors and ToC on the left, and the content on the
        right.

        The layout looks like this:

        ------------------------------------------
        |             |                          |
        |             |                          |
        | Sidebar     |         Content          |
        | (30% width) |      (800px width)       |
        |             |                          |
        ------------------------------------------

        Arguments:
            content {str} -- The HTML of the content
        """
        toc = textwrap.dedent(
            """
            <h1>Table of Contents</h1>
            <p><ac:structured-macro ac:name="toc" ac:schema-version="1">
                <ac:parameter ac:name="exclude">^(Authors|Table of Contents)$</ac:parameter>
            </ac:structured-macro></p>"""  # noqa: E501
        )
        # Ignore the TOC if we haven't processed any headers to avoid making a
        # blank one
        if not self.has_toc:
            toc = ""
        column = textwrap.dedent(
            """
            <ac:structured-macro ac:name="column" ac:schema-version="1">
                <ac:parameter ac:name="width">{width}</ac:parameter>
                <ac:rich-text-body>{content}</ac:rich-text-body>
            </ac:structured-macro>"""
        )
        main_content = column.format(width="100%", content=toc + content)
        return main_content

    def layout(self, content: str) -> str:
        """Renders the final layout of the content. This includes a two-column
        layout, with the authors and ToC on the left, and the content on the
        right.

        The layout looks like this:

        ------------------------------------------
        |             |                          |
        |             |                          |
        | Sidebar     |         Content          |
        | (30% width) |      (800px width)       |
        |             |                          |
        ------------------------------------------

        Arguments:
            content {str} -- The HTML of the content
        """
        toc = textwrap.dedent(
            """
            <h1>Table of Contents</h1>
            <p><ac:structured-macro ac:name="toc" ac:schema-version="1">
                <ac:parameter ac:name="exclude">^(Authors|Table of Contents)$</ac:parameter>
            </ac:structured-macro></p>"""  # noqa: E501
        )
        # Ignore the TOC if we haven't processed any headers to avoid making a
        # blank one
        if not self.has_toc:
            toc = ""
        authors = self.render_authors()
        column = textwrap.dedent(
            """
            <ac:structured-macro ac:name="column" ac:schema-version="1">
                <ac:parameter ac:name="width">{width}</ac:parameter>
                <ac:rich-text-body>{content}</ac:rich-text-body>
            </ac:structured-macro>"""
        )
        sidebar = column.format(width="30%", content=toc + authors)
        main_content = column.format(width="800px", content=content)
        return sidebar + main_content

    def heading(self, text: Any, level: Any) -> Any:
        """Processes a Markdown header.

        In our case, this just tells us that we need to render a TOC. We don't
        actually do any special rendering for headers.
        """
        self.has_toc = True
        return super().heading(text, level)

    def render_authors(self) -> str:
        """Renders a header that details which author(s) published the post.

        This is used since Confluence will show the post published as our
        service account.

        Arguments:
            author_keys {str} -- The Confluence user keys for each post author

        Returns:
            str -- The HTML to prepend to the post specifying the authors
        """
        author_template = """<ac:structured-macro ac:name="profile-picture" ac:schema-version="1">
                <ac:parameter ac:name="User"><ri:user ri:userkey="{user_key}" /></ac:parameter>
            </ac:structured-macro>&nbsp;
            <ac:link><ri:user ri:userkey="{user_key}" /></ac:link>"""  # noqa: E501
        author_content = "<br />".join(
            author_template.format(user_key=user_key)
            for user_key in self.authors
        )
        return "<h1>Authors</h1><p>{}</p>".format(author_content)

    def block_code(self, code: str, lang: Optional[str] = None) -> str:
        return textwrap.dedent(
            """\
            <ac:structured-macro ac:name="code" ac:schema-version="1">
                <ac:parameter ac:name="language">{l}</ac:parameter>
                <ac:plain-text-body><![CDATA[{c}]]></ac:plain-text-body>
            </ac:structured-macro>
        """
        ).format(c=code, l=lang or "")

    def image(
        self, src: str, alt: str = "", title: Optional[str] = None
    ) -> str:
        """Renders an image into XHTML expected by Confluence.

        Arguments:
            src {str} -- The path to the image
            title {str} -- The title attribute for the image
            alt_text {str} -- The alt text for the image

        Returns:
            str -- The constructed XHTML tag
        """
        # Check if the image is externally hosted, or hosted as a static
        # file within Journal
        is_external = bool(urlparse(src).netloc)
        tag_template = "<ac:image>{image_tag}</ac:image>"
        image_tag = '<ri:url ri:value="{}" />'.format(src)
        if not is_external:
            image_tag = '<ri:attachment ri:filename="{}" />'.format(
                os.path.basename(src)
            )
            self.attachments.append(src)
        return tag_template.format(image_tag=image_tag)
