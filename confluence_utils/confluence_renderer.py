import os
import textwrap
from typing import Optional
from urllib.parse import urlparse

import mistune
from mistune.directives import DirectiveToc


class DirectiveConfluenceToc(DirectiveToc):
    def __call__(self, md):  # type: ignore
        self.register_directive(md, "toc")
        self.register_plugin(md)

        if md.renderer.NAME == "html":
            md.renderer.register("toc", render_html_toc_confluence)


def render_html_toc_confluence(items, title, depth):  # type: ignore
    html = '<section class="toc">\n'
    if title:
        html += "<h1>" + title + "</h1>\n"

    toc_macro = """
<ac:structured-macro ac:name="toc" ac:schema-version="1">
<ac:parameter ac:name="exclude">^(Authors|Table of Contents)$</ac:parameter>
</ac:structured-macro>\n"""

    return html + toc_macro + "</section>\n"


class ConfluenceRenderer(mistune.HTMLRenderer):
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
        return tag_template.format(image_tag=image_tag)
