from confluence_utils.markdown_parser import parse


def test_parse():
    markdown, front_matter = parse("tests/test.md")
    assert front_matter == {
        "title": "TEST",
    }
