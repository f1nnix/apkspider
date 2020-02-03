from itertools import islice

from crawler.config import config
from crawler.spider import Spider


def main():
    spider = Spider(root_path=config.root_path,
                    max_depth=config.max_depth)
    apps = islice(spider, 0, config.apps_to_fetch)

    for app in apps:
        app.fetch_download_id()
        app.download_file()

        with open('files.txt', 'w') as f:
            for file in app.read_archive_content():
                line = '{} – {} – {} - {}\n'.format(
                    file.archive_name, file.file_name,
                    file.mime_type, file.size_deflated)

                f.write(line)


if __name__ == '__main__':
    main()
