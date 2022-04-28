import os

from mistune.directives import Directive, DirectiveToc


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


class DirectiveConfluenceStyles(Directive):
    def __init__(self, directory):  # type: ignore
        self.directory = directory

    def parse(self, block, m, state):  # type: ignore
        options = self.parse_options(m)
        if options:
            return {"type": "block_error", "raw": "Styles has no options"}
        path = os.path.join(self.directory, m.group("value"))
        return {
            "type": "styles",
            "raw": None,
            "params": (path,),
        }

    def __call__(self, md):  # type: ignore
        self.register_directive(md, "styles")

        if md.renderer.NAME == "html":
            md.renderer.register("styles", render_html_styles)


def render_html_styles(text, path):  # type: ignore
    css = open(path, "r").read()
    html = (
        '<ac:structured-macro ac:name="style" ><ac:plain-text-body><![CDATA['
    )
    html += css
    html += "]]></ac:plain-text-body></ac:structured-macro>\n"
    return html
