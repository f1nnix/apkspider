from crawler.proxied_session import _get_request_headers


def test_basic():
    headers = _get_request_headers()
    assert 'User-Agent' in headers
    assert headers['User-Agent']


def test_headers_randomized():
    headers_1 = _get_request_headers()
    headers_2 = _get_request_headers()
    assert 'User-Agent' in headers_1
    assert 'User-Agent' in headers_2

    ua_1 = headers_1['User-Agent']
    ua_2 = headers_2['User-Agent']
    assert ua_1 != ua_2
