from crawler.page import Page


def test_basic():
    MOCK_PATH = 'bar'

    page = Page('foo')
    page.recursion_level = 1
    page.page_links = [MOCK_PATH]

    children = [c for c in page.children()]
    assert len(children) == 1

    child = children[0]
    assert isinstance(child, Page)
    assert child.recursion_level == 2
    assert child.path == MOCK_PATH
