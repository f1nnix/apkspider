import logging
import typing as tp
from collections import deque
from logging import Logger

from crawler.config import config
from crawler.errors import DownloadError
from crawler.page import Page


class Spider:
    """
    DFS-based recursive crawler.

    Manages stack of Pages, which are queued for parsing.
    Initialized with one element in stack — root Page node.
    After fetching root Page contests, adds all new
    retrieved Pages to stack. Apps are piped to generator-like
    interface directly without actual storing in memory.

    If Page download error occures, DownloadError is raised.
    Page is re-scheduled to download to the bottom of the stack,
    increasing it's own retries_count. It retries_count >=
    max_retries_count, safely removes from Pages stack.

    @iterator
    """

    def __init__(self, root_path: str = '/', max_depth: int = 6, logger: Logger = None):
        self.stack: tp.Deque[Page] = deque()
        self.visited_pages: tp.Set[str] = set()
        self.max_depth: int = max_depth

        # Build and add root page to queue
        # as first node to start graph traverse
        root_page: Page = Page(path=root_path)
        self.visited_pages.add(root_path)
        self.stack.append(root_page)

        self.logger = logger
        if not self.logger:
            self.logger = logging.getLogger('spider')
            self.logger.setLevel(logging.DEBUG)

    def __iter__(self) -> tp.Generator[Page, None, None]:
        """
        Iterates over graph with DFS starting from `root_path`.

        On each iteration yields `Page` instance.
        """
        while self.stack:
            # Pop next page from top of stack
            page: Page = self.stack.popleft()
            self.logger.debug('Crawling page: %s' % page.path)

            try:
                page.fetch_body()
            except DownloadError:
                # If fetching data fails for some reason,
                # re-schedule page to the bottom of the stack
                # if max_retries_count allowes.
                if page.retries_count >= config.max_retries_count:
                    continue
                page.retries_count += 1
                self.stack.append(page)
            else:
                page.extract_links()

            # Do not append child to queue pages
            # deeper than max recursion depth
            for child in page.children():
                if child.path not in self.visited_pages and \
                        child.recursion_level <= config.max_depth:
                    self.visited_pages.add(child.path)
                    self.stack.appendleft(child)

            self.logger.info('Pages in queue: %s' % len(self.stack))
            yield page
