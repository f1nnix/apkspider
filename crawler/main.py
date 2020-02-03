import typing as tp
from itertools import islice

from crawler.app import App
from crawler.config import config
from crawler.page import Page
from crawler.spider import Spider
from crawler.utils import apps_iterator


def main():
    spider: Spider = Spider(root_path=config.root_path,
                            max_depth=config.max_depth)

    # Build unique pages generator
    pages: tp.Generator[Page, None, None] = \
        (page for page in spider)

    # Build ranged apps generator
    apps: tp.Generator[App, None, None] = \
        apps_iterator(pages)
    ranged_apps: tp.Union[islice, tp.Iterator[App]] = \
        islice(apps, config.apps_to_fetch)

    with open('files.txt', 'a') as f:
        for app in ranged_apps:
            for file in app:
                f.write(file.dumps())


if __name__ == '__main__':
    main()
