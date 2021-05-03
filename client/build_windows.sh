pyrcc5 client/resources.qrc -o client/resources.py
pyinstaller.exe -Fy --icon 'client/docs_icon.ico' --name MiptCisDocs --add-data 'client/docs_icon.ico;.' --resource client/docs_icon.ico  client/main.py
