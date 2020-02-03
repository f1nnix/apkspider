import typing as tp
from dataclasses import dataclass


@dataclass
class Config:
    # A list of HTTP proxies, which should be
    # used to fetch data. Good choice: https://tinyproxy.github.io.
    # E.g: ['http://77.88.55.77:8081', 'http://77.88.55.70:8081']
    proxies: tp.List[str] = None

    # Amount of hops from root node to fetch,
    # not actual depth of tree
    max_depth: int = 5

    # Domain settings to crawl
    scheme: str = 'http'
    network_location: str = 'www.apkmirror.com'

    # How much targer URLs to process
    apps_to_fetch: int = 2000

    # Root node path to traverse from
    root_path: str = '/'

    # How much times to re-download Page
    max_retries_count: int = 3

    # Will be used, when file in archive
    # has neither known mime-type nor extension
    # ref:http://www.rfc-editor.org/rfc/rfc2046.txt
    unknown_mime_failback = 'application/octet-stream'

    # Site-specific settings, may be different for other instances
    download_handler_path = '/wp-content/themes/APKMirror/download.php'
    download_app_page_suffix = '-download/'


config = Config(proxies=[
    ...
])
