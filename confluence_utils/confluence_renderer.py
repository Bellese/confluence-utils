import os
import uuid
from typing import Dict, List, Optional
from urllib.parse import urlparse

import mistune


class ConfluenceRenderer(mistune.HTMLRenderer):
    def __init__(self) -> None:
        self.attachments: List[str] = []
        self.links: Dict[str, str] = {}
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

    def link(
        self,
        link: str,
        text: Optional[str] = None,
        title: Optional[str] = None,
    ) -> str:
        is_external = bool(urlparse(link).netloc)
        if not is_external:
            replacement_text = str(uuid.uuid4())
            self.links[link] = replacement_text
            link = replacement_text
        return super().link(link, text, title)

    def image(
        self, src: str, alt: str = "", title: Optional[str] = None
    ) -> str:

        html = "<ac:image>\n"

        is_external = bool(urlparse(src).netloc)
        if is_external:
            image_tag = '<ri:url ri:value="{}" />'.format(src)
        else:
            self.attachments.append(src)
            image_tag = '<ri:attachment ri:filename="{}" />\n'.format(
                os.path.basename(src)
            )

        html += image_tag
        html += "</ac:image>\n"
        return html
