import logging
import typing as tp
from urllib.parse import urlunsplit

from bs4 import BeautifulSoup

from crawler.config import config
from crawler.errors import DownloadError
from crawler.http_client import SpoofedHTTPClient
from crawler.utils import get_url_path, is_url_allowed


class Page:
    def __init__(self, path: str, recursion_level: int = 0, logger: logging.Logger = None):
        self.path: str = path
        self.recursion_level: int = recursion_level
        self.html: str = ''
        self.app_links: tp.Set[str] = set()
        self.page_links: tp.Set[str] = set()

        self.logger = logger
        if not self.logger:
            self.logger = logging.getLogger('app')
            self.logger.setLevel(logging.DEBUG)

    def __hash__(self):
        return hash(self.path)

    def __str__(self):
        return self.path

    def fetch_body(self):
        with SpoofedHTTPClient(proxies=config.proxies) as session:
            response = session.get(self.absolute_url)
            if response.status_code != 200:
                raise DownloadError

            self.html = response.text

    def extract_links(self):
        assert self.html, 'page should have valid html'

        soup = BeautifulSoup(self.html, 'html.parser')
        link_tags = soup.find_all('a')

        for tag in link_tags:
            href = tag.attrs.get('href')
            if href is None:
                continue

            url_path = get_url_path(href)
            if url_path is None:
                continue

            if not is_url_allowed(url_path):
                continue

            if url_path.endswith('-download/'):
                self.app_links.add(url_path)
            else:
                self.page_links.add(url_path)

    @property
    def absolute_url(self):
        return urlunsplit(
            (config.scheme, config.network_location, self.path, None, None,))
