import mistune
from mistune.plugins import plugin_abbr, plugin_def_list, plugin_task_lists

from confluence_utils.confluence_directives import DirectiveConfluenceToc
from confluence_utils.confluence_renderer import ConfluenceRenderer
from tests import BaseTestCase


class TestPluginToc(BaseTestCase):
    @staticmethod
    def parse(text):
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
        html = markdown(text)
        return html

    def assert_case(self, name, text, html):
        result = self.parse(text)
        self.assertEqual(result, html)


TestPluginToc.load_fixtures("toc.txt")
