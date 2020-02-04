import typing as tp
from itertools import chain, islice

from crawler.app import App
from crawler.config import config
from crawler.page import Page
from crawler.spider import Spider


def main():
    spider: Spider = Spider(root_path=config.root_path,
                            max_depth=config.max_depth)

    # Build unique pages generator
    pages: tp.Generator[Page, None, None] = \
        (page for page in spider)

    # Build ranged apps generator
    apps: tp.Union[islice, tp.Iterator[App]] = \
        islice(chain.from_iterable(pages), config.apps_to_fetch)

    with open('files.txt', 'a') as f:
        for app in apps:
            for file in app:
                f.write(file.dumps())


if __name__ == '__main__':
    main()
