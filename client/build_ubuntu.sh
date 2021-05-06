pyrcc5 client/resources.qrc -o client/resources.py
pyinstaller -wFy -n MiptCisDocs -i client/docs_icon.ico --add-data 'client/docs_icon.ico:.' client/main.py
