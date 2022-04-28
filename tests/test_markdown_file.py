import os
import platform
import shutil
import tempfile
from pathlib import Path

from confluence_utils.markdown_file import MarkdownFile

tempdir = Path(
    "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
)


def test_properties():
    test_file_path = os.path.join(tempdir, "test.md")

    shutil.copy("tests/test.md", test_file_path)
    markdown_file = MarkdownFile(test_file_path)

    # title
    assert markdown_file.title == "TEST"
    markdown_file.title = "new title"
    assert markdown_file.title == "new title"

    # page_id
    assert markdown_file.get_page_id_for_space("test-space") is None
    markdown_file.set_page_id_for_space("123", "test-space")
    assert markdown_file.get_page_id_for_space("test-space") == "123"

    # parent_path
    assert markdown_file.parent_file_path is None

    # parent
    assert markdown_file.parent is None

    test_child_file_path = os.path.join(tempdir, "test_child.md")

    shutil.copy("tests/test_child.md", test_child_file_path)
    child_markdown_file = MarkdownFile(test_child_file_path)

    # parent
    assert child_markdown_file.parent is not None
    assert (
        child_markdown_file.parent.get_page_id_for_space("test-space") == "123"
    )

    os.remove(test_file_path)
    os.remove(test_child_file_path)
