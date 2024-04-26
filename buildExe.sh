#!/bin/bash
pyinstaller --noconfirm --onefile --console --clean --icon "../drawing.ico" --distpath "./" --specpath "./build" "./main.py"
read