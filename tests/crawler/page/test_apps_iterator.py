from unittest.mock import patch, MagicMock

from crawler.page import Page

MOCK_PATH = 'foo'
MOCK_APP_PATH = 'bar'


@patch('crawler.page.App')
def test_basic(mock_app_constructor):
    app = MagicMock()
    mock_app_constructor.return_value = app

    page = Page(MOCK_PATH)
    page.app_links = [MOCK_APP_PATH] * 3

    yielded_apps = [app for app in page]
    assert len(yielded_apps) == 3
    for yielded_app in yielded_apps:
        assert yielded_app is app

    app.fetch_download_id.assert_called()
    app.download_file.assert_called()
