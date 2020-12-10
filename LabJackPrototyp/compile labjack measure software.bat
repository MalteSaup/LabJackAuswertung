pyinstaller --noconsole -i "./images/icon.ico" -n "Measure LabJack" main.py
xcopy "./images" "./dist/Measure LabJack" /i