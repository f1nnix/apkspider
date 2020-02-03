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
from crawler.http_client import SpoofedHTTPClient
from crawler.struct import File, AppState


class App:
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

    def fetch_download_id(self):

        assert self.state == AppState.INITIALIZED

        with SpoofedHTTPClient(proxies=config.proxies) as session:
            response = session.get(self.absolute_app_url)
            if response.status_code != 200:
                raise DownloadError

            self.download_id = self._extract_download_id(response.content)

        self.state = AppState.FETCHED

    def download_file(self):
        """
        We explicitly don't close tempfile until content is extracted
        or App instance will be force removed by garbage collector.

        :return:
        """
        assert self.state == AppState.FETCHED

        with SpoofedHTTPClient(proxies=config['proxies']) as session:
            response = session.get(self.absolute_download_url)
            assert response.status_code == 200

            self.tempfile = NamedTemporaryFile()
            self.tempfile.write(response.content)

        self.filename = self._extract_archive_name_from_url(response.url)
        self.state = AppState.DOWNLOADED

    def _extract_download_id(self, html: str) -> tp.Optional[int]:
        soup = BeautifulSoup(html, 'html.parser')
        wordpress_shortlink_tag: Tag = soup.find('link', rel='shortlink')
        shortlink_href = wordpress_shortlink_tag.attrs.get('href')
        if not shortlink_href:
            ...

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

    def read_archive_content(self) -> File:
        assert self.state == AppState.DOWNLOADED

        with ZipFile(self.tempfile) as zipfile:
            for zipinfo in zipfile.infolist():
                file: File = File()
                file.archive_name = self.filename
                file.file_name = zipinfo.filename
                file.mime_type = self._get_mime_type(zipinfo.filename)
                file.size_deflated = zipinfo.file_size
                file.size_compressed = zipinfo.compress_size

                yield file

        self.tempfile.close()

    @property
    def absolute_app_url(self):
        return urlunsplit(
            (config.scheme, config.network_location, self.path, None, None,))

    @property
    def absolute_download_url(self):
        query = f'id={self.download_id}'

        return urlunsplit(
            (config.scheme, config.network_location, config.download_handler_path, query, None,))
