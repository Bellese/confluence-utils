from confluence_utils.markdown_parser import parse


def test_parse():
    front_matter, markdown = parse("test.md")
    assert front_matter == {
        "category": "standards",
        "date": "2020-06-12",
        "status": "Active",
        "title": "Test",
    }
