import logging
import typing as tp
from collections import deque
from logging import Logger

from crawler.app import App
from crawler.errors import DownloadError
from crawler.page import Page


class Spider:
    """
    @iterator
    DFS-based recursive crawler.

    Manages stack of Pages, which queued to be parsed.
    Initialized with one element, root Page node, in stack.
    After fetching root Page contests, adds all newly
    retrieved Pages to stack. Apps are piped to generator-like
    interface directly without actual storing in memory.

    If Page download error occures, DownloadError is raised.
    Page is re-scheduled to download to the bottom of the stack,
    increasing it's own retries_count. It retries_count >=
    max_retries_count, safely removes from Pages stack.
    """

    def __init__(self, root_path: str = '/', max_depth: int = 6, logger: Logger = None):
        self.stack: tp.Deque[Page] = deque()
        self.visited_pages: tp.Set[str] = set()
        self.visited_apps: tp.Set[str] = set()
        self.max_depth: int = max_depth

        # Build and add root page to queue
        # as first node to start graph traverse
        root_page: Page = Page(path=root_path)
        self.stack.append(root_page)
        self.visited_pages.add(root_path)

        self.logger = logger
        if not self.logger:
            self.logger = logging.getLogger('spider')
            self.logger.setLevel(logging.DEBUG)

    def __iter__(self):
        """
        Iterates over graph with DFS starting from `root_path`.



        :return:
        """
        while self.stack:
            # Pop next page from top of stack
            current_page = self.stack.popleft()
            self.logger.debug('Crawling page: %s' % current_page.path)

            try:
                current_page.fetch_body()
            except DownloadError as exc:
                self.logger.error('Failed to crawl page: %s. Removing from queue' % current_page.path)
                continue

            current_page.extract_links()

            new_app_paths = tuple(
                p for p in current_page.app_links
                if p not in self.visited_apps
            )
            self.visited_apps.update(new_app_paths)
            self.logger.debug('Fetched %s new app links' % len(new_app_paths))
            yield from (App(path=p) for p in new_app_paths)

            # Do not append child to queue pages
            # deeper than max recursion depth
            if current_page.recursion_level >= self.max_depth:
                continue

            # Append to stack
            new_page_paths = tuple(
                p for p in current_page.page_links
                if p not in self.visited_pages
            )
            self.visited_pages.update(new_page_paths)
            self.stack.extendleft(
                Page(path, recursion_level=current_page.recursion_level + 1)
                for path in new_page_paths
            )
