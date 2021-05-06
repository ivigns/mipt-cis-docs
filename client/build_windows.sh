pyrcc5 client/resources.qrc -o client/resources.py
pyinstaller.exe -wFy --icon 'client/docs_icon.ico' --name MiptCisDocs --add-data 'client/docs_icon.ico;.' --resource client/docs_icon.ico --version-file 'client/versionfile.py'  client/main.py
