import os
from typing import List, Optional
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

    html += '<ac:structured-macro ac:name="toc" ac:schema-version="1">\n'
    html += '<ac:parameter ac:name="exclude">\n'
    html += "^(Authors|Table of Contents)$\n"
    html += "</ac:parameter>\n"
    html += "</ac:structured-macro>\n"

    return html + "</section>\n"


class ConfluenceRenderer(mistune.HTMLRenderer):
    def __init__(self) -> None:
        self.attachments: List[str] = []
        super().__init__()

    def block_code(self, code: str, lang: Optional[str] = None) -> str:
        html = '<ac:structured-macro ac:name="code" ac:schema-version="1">\n'
        html += '<ac:parameter ac:name="language">{l}</ac:parameter>\n'
        html += '<ac:parameter ac:name="theme">RDark</ac:parameter>\n'
        html += '<ac:parameter ac:name="linenumbers">'
        html += "true"
        html += "</ac:parameter>\n"
        html += "<ac:plain-text-body><![CDATA[{c}]]></ac:plain-text-body>\n"
        html += "</ac:structured-macro>\n"

        return html.format(
            c=code,
            l=lang or "",
        )

    def image(
        self, src: str, alt: str = "", title: Optional[str] = None
    ) -> str:
        is_external = bool(urlparse(src).netloc)

        if is_external:
            image_tag = '<ri:url ri:value="{}" />'.format(src)
        else:
            image_tag = '<ri:attachment ri:filename="{}" />'.format(
                os.path.basename(src)
            )
            self.attachments.append(src)

        return "<ac:image>{image_tag}</ac:image>".format(image_tag=image_tag)
