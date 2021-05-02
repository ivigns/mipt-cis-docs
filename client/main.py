import faulthandler
import sys

import client.ui.app as app


def main():
    faulthandler.enable()
    docs_app = app.DocsApp()
    sys.exit(docs_app.exec())


if __name__ == '__main__':
    main()
