import logging
import faulthandler
import os
import sys

from client.ui import app
from client.data_manage import data_dir


def _redirect_streams():
    logs_dir = data_dir.get_data_dir()
    sys.stdout = open(os.path.join(logs_dir, 'info.log'), 'w')
    sys.stderr = open(os.path.join(logs_dir, 'error.log'), 'w')


def _get_logger() -> logging.Logger:
    _redirect_streams()  # comment to watch logs in console
    formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s')
    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    result = logging.getLogger('client')
    result.setLevel(logging.INFO)
    result.addHandler(info_handler)
    result.addHandler(error_handler)
    return result


logger = _get_logger()


def main():
    faulthandler.enable()
    logger.info('Starting app')
    docs_app = app.DocsApp()
    sys.exit(docs_app.exec())


if __name__ == '__main__':
    main()
