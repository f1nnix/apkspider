import typing as tp
from contextlib import contextmanager
from random import choice

import requests
from user_agent import generate_user_agent

from crawler.errors import DownloadError

BASE_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Host': 'www.apkmirror.com',
    'Accept-Language': 'en-us',
    'Accept-Encoding': 'deflate',
    'Connection': 'keep-alive',

}


def _get_request_headers() -> dict:
    """
    Returns pseudo-unique request headers.

    :return: HTTP headers with random user agent string.
    """
    request_headers = BASE_REQUEST_HEADERS.copy()

    # UA may be auto-generated for each new session / request.
    random_user_agent = generate_user_agent()
    request_headers['User-Agent'] = random_user_agent

    return request_headers


@contextmanager
def SpoofedHTTPClient(proxies: tp.List[str]):
    assert proxies, 'should instantiate HTTP client with at least one proxy'

    request_headers = _get_request_headers()
    request_proxy = choice(proxies)
    with requests.Session() as session:
        session.headers = request_headers
        session.proxies = {
            'http': request_proxy,
            'https': request_proxy,
        }
        try:
            yield session
        except DownloadError as exc:
            raise DownloadError
