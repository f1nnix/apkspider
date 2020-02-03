import logging
import mimetypes
import pathlib
import typing as tp
from logging import Logger
from os.path import basename
from tempfile import NamedTemporaryFile
from urllib.parse import urlunsplit, urlsplit
from zipfile import ZipFile

from bs4 import BeautifulSoup
from bs4.element import Tag

from crawler.config import config
from crawler.errors import DownloadError
from crawler.proxied_session import ProxiedSession
from crawler.structs import File, AppState


class App:
    """
    Downloads and analysis contests of fetched APK.
    Provides APK contents as iterable Generator[File].

    Usage:

        path = '/apk/google-inc...'
        app: App = App(path=path)

        app.fetch_download_id()
        app.download_file()

        for file in app:
            ...

    @iterable
    """

    def __init__(self, path: str, logger: Logger = None):
        self.path: str = path
        self.download_id: tp.Optional[int] = None
        self.filename: tp.Optional[str] = ''

        self.tempfile: tp.Optional[NamedTemporaryFile] = None
        self.files: tp.List[File] = []

        self.state: AppState = AppState.INITIALIZED

        self.logger = logger
        if not self.logger:
            self.logger = logging.getLogger('app')
            self.logger.setLevel(logging.DEBUG)

    def __hash__(self):
        return hash(self.path)

    def __str__(self):
        return self.path

    def __iter__(self) -> tp.Generator[File, None, None]:
        """
        Iterates over fulfilled File object
        and yields each file info of downloaded APK.
        """
        with ZipFile(self.tempfile) as zipfile:
            for zipinfo in zipfile.infolist():
                file: File = File()

                file.archive_name = self.filename
                file.file_name = zipinfo.filename
                file.mime_type = self._get_mime_type(zipinfo.filename)
                file.size_deflated = zipinfo.file_size
                file.size_compressed = zipinfo.compress_size

                yield file

        # FIXME: this may be swallowed by context manager
        self.tempfile.close()

    def fetch_download_id(self) -> None:
        """
        APKMirror uses proxy pages to provide links for downloading APK.
        Target path looks like '/wp-content/themes/APKMirror/download.php?id=<download_id>'

        <download_id> is simply WordPress post ID.

        To obtain real Wordpress post ID we need to download proxy page.
        After which Wordpress ID be trivially retrieved from 'shortlink'
        link meta tag of proxy page.

        ref:self._extract_download_id
        """
        # assert self.state == AppState.INITIALIZED

        with ProxiedSession(proxies=config.proxies) as session:
            response = session.get(self.absolute_app_url)
            if response.status_code != 200:
                raise DownloadError

            self.download_id = self._extract_download_id(response.content)

        self.logger.info('Fetched download ID for app %s' % self.path)
        self.state = AppState.FETCHED

    def download_file(self) -> None:
        """
        We explicitly don't close tempfile until:

        - content is extracted;
        - App instance will be force removed by garbage collector.
        """
        # assert self.state == AppState.FETCHED

        with ProxiedSession(proxies=config.proxies) as session:
            response = session.get(self.absolute_download_url)
            assert response.status_code == 200

            self.tempfile = NamedTemporaryFile()
            self.tempfile.write(response.content)

        self.filename = self._extract_archive_name_from_url(response.url)
        self.state = AppState.DOWNLOADED
        self.logger.info('Downloaded new APK: %s' % self.filename)

    def _extract_download_id(self, html: str) -> tp.Optional[int]:
        """
        Extracts actual Wordpress ID for APK attachment
        from download proxy page HTML contests from 'shortlink'
        link meta tag.
        """
        soup = BeautifulSoup(html, 'html.parser')
        wordpress_shortlink_tag: Tag = soup.find('link', rel='shortlink')

        shortlink_href = wordpress_shortlink_tag.attrs.get('href')
        if not shortlink_href:
            return None

        query_param, download_id = shortlink_href.split('=')
        try:
            return int(download_id)
        except ValueError as exc:
            return None

    @staticmethod
    def _extract_archive_name_from_url(url: str) -> str:
        scheme, netloc, path, query, fragment = urlsplit(url)
        return basename(path)

    @staticmethod
    def _get_mime_type(filename: str) -> str:
        mime_type, _ = mimetypes.guess_type(filename, strict=True)
        if mime_type:
            return mime_type

        # If filename has extension, describe it
        # as custom "application/%s" mime-type
        suffix = pathlib.Path(filename).suffix
        if suffix:
            return 'application/{}'.format(
                suffix[1:]  # Strip the leading dot from extension
            )

        return config.unknown_mime_failback

    @property
    def absolute_app_url(self):
        if not self.path:
            return None

        return urlunsplit(
            (config.scheme, config.network_location, self.path, None, None,))

    @property
    def absolute_download_url(self):
        if not self.download_id:
            return None

        query = f'id={self.download_id}'
        return urlunsplit(
            (config.scheme, config.network_location, config.download_handler_path, query, None,))
