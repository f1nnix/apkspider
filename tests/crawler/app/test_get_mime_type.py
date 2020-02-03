from crawler.config import config
from crawler.app import App


def test_basic():
    filename = 'image.png'
    expected_mime_type = 'image/png'

    assert App._get_mime_type(filename) == expected_mime_type


def test_unknown_extension():
    filename = 'model_empirical_uncal_high_stddev.binaryproto'
    expected_mime_type = 'application/binaryproto'

    assert App._get_mime_type(filename) == expected_mime_type


def test_no_extension():
    filename = 'file'
    expected_mime_type = config.unknown_mime_failback

    assert App._get_mime_type(filename) == expected_mime_type

def test_no_empty_extension():
    filename = 'file.'
    expected_mime_type = config.unknown_mime_failback

    assert App._get_mime_type(filename) == expected_mime_type
