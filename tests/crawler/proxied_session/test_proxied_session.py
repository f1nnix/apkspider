from unittest.mock import patch, MagicMock

import pytest

from crawler.proxied_session import ProxiedSession

SENTINEL = object()
from crawler.errors import DownloadError


@patch('crawler.proxied_session.requests.Session')
@patch('crawler.proxied_session._get_request_headers')
@patch('crawler.proxied_session.choice')
def test_basic(
        mock_choice,
        mock_get_request_headers,
        mock_session_factory
):
    MOCK_PROXY_URLS = ['foo']

    session = MagicMock()
    mock_session_factory.return_value = session
    mock_choice.return_value = SENTINEL
    mock_get_request_headers.return_value = SENTINEL

    with ProxiedSession(
            proxies=MOCK_PROXY_URLS
    ) as yielded_session:
        mock_choice.assert_called_with(MOCK_PROXY_URLS)
        assert yielded_session.headers is SENTINEL
        assert yielded_session.proxies == {
            'http': SENTINEL,
            'https': SENTINEL,
        }


def test_raises_download_error():
    MOCK_PROXY_URLS = ['foo']
    with pytest.raises(DownloadError):
        with ProxiedSession(
                proxies=MOCK_PROXY_URLS
        ) as yielded_session:
            raise DownloadError
