pyrcc5 client/resourses.qrc -o client/resourses.py
pyinstaller.exe -wF -n MiptCisDocs -i client/docs_icon.ico --add-data 'client/docs_icon.ico;.' client/main.py
