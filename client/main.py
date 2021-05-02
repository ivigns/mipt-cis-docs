import sys

import client.ui.app as app


def main():
    docs_app = app.DocsApp()
    sys.exit(docs_app.exec())


if __name__ == '__main__':
    main()
