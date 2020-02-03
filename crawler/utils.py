import typing as tp
from urllib.parse import urlparse


def get_url_path(url: str) -> tp.Optional[str]:
    url_path = urlparse(url)

    # Don't handle external links
    # if not url_path.hostname:
    #     import pdb; pdb.set_trace()
    if url_path.netloc and not url_path.netloc.endswith('apkmirror.com'):
        return None

    # Normalize root paths
    if not url_path.path:
        return '/'

    return url_path.path


def is_url_allowed(path: str) -> bool:
    return path.startswith('/apk') or path.startswith('/page')
