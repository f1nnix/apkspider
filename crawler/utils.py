import typing as tp
from urllib.parse import urlparse

from crawler.app import App
from crawler.config import config


def get_path_from_url(url: str) -> tp.Optional[str]:
    """
    Returns normalized parsed path part from absolute URL.
    Fragments or query parameters are stripped. E.g.:

        https://github.com/urllib/master => /urllib/master
    """
    scheme, netloc, path, params, query, fragment = \
        urlparse(url)

    # Don't allow external links
    if netloc and \
            not netloc.endswith(config.network_location):
        return None

    # If we got nothing as path,
    # consider we're fetched root node
    if not path:
        return '/'

    return path


def is_url_allowed(path: str) -> bool:
    """
    Return True, is path has prefix,
    whitelisted for crawling.
    """
    return path.startswith('/apk/') \
           or path.startswith('/page/')


def apps_iterator(pages: tp.Generator) -> tp.Generator[App, None, None]:
    """
    Helper iterator to generate Apps from Pages instances
    """
    for page in pages:
        yield from page
