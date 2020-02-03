import logging
import typing as tp
from urllib.parse import urlunsplit

from bs4 import BeautifulSoup

from crawler.app import App
from crawler.config import config
from crawler.errors import DownloadError
from crawler.proxied_session import ProxiedSession
from crawler.structs import PageState
from crawler.utils import get_path_from_url, is_url_allowed


class Page:
    """
    Downloads and analysis contests of fetched page.
    Provides iterator interfaces over:

    - self child nodes:Page;
    - self apps:App.

    Usage:

        path = '/apk/google-inc...'
        page: Page = Page(path=path, recursion_level=1)

        page.fetch_body()
        page.download_file()

        for app in page:
            ...
        for child in page:
            ...

    @iterable
    """

    def __init__(self, path: str, recursion_level: int = 0, logger: logging.Logger = None):
        self.path: str = path
        self.recursion_level: int = recursion_level

        self.app_links: tp.Set[str] = set()
        self.page_links: tp.Set[str] = set()
        self.html: str = ''

        self.state: PageState = PageState.INITIALIZED
        self.retries_count: int = 0

        self.logger = logger
        if not self.logger:
            self.logger = logging.getLogger('app')
            self.logger.setLevel(logging.DEBUG)

    def __hash__(self):
        return hash(self.path)

    def __str__(self):
        return self.path

    def __iter__(self) -> tp.Generator[App, None, None]:
        """
        Iterates over self app links, returning a new
        App object with prefetced APK file.
        """
        for app_path in self.app_links:
            app = App(path=app_path)

            # If we're unable to fetch app data,
            # skip it without retrying
            try:
                app.fetch_download_id()
                app.download_file()
            except DownloadError as exc:
                self.logger.error('Cant download app %s. Skipping.' % self.path)
            else:
                yield app

    def children(self) -> tp.Generator['Page', None, None]:
        """
        Iterates over self page links, returning a new
        Page object for children nodes on each iteration.
        """
        children: tp.Generator[Page, None, None] = \
            (self.__class__(
                path=path,
                recursion_level=self.recursion_level + 1
            ) for path in self.page_links)

        yield from children

    def fetch_body(self):
        with ProxiedSession(proxies=config.proxies) as session:
            response = session.get(self.absolute_url)
            if response.status_code != 200:
                self.logger.error('Failed to fetch page body: %s' % self.path)
                raise DownloadError

            self.html = response.text
            self.state = PageState.FETCHED

    def extract_links(self) -> None:
        """
        Parses self HTML and extracts links, matching
        allowed patterns to self.app_links and self.page_links.

        App links are determined by having DOWNLOAD_SUFFIX.
        """
        assert self.html, 'page should have valid html'

        soup = BeautifulSoup(self.html, 'html.parser')
        link_tags = soup.find_all('a')

        for tag in link_tags:
            href = tag.attrs.get('href')
            if href is None:
                continue

            url_path = get_path_from_url(href)
            if url_path is None:
                continue

            # Limited URL scope is allowed
            if not is_url_allowed(url_path):
                continue

            if url_path.endswith(config.download_app_page_suffix):
                self.app_links.add(url_path)
            else:
                self.page_links.add(url_path)

    @property
    def absolute_url(self) -> str:
        """
        Returns full absolute URL of Page
        instance, including domain and URL scheme.
        """
        return urlunsplit(
            (config.scheme, config.network_location, self.path, None, None,))
