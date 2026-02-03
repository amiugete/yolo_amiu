@echo off
:: Naviga nella cartella del progetto (opzionale se il bat è già lì)
cd /d "C:\python\yolo_amiu"

:: Attiva l'ambiente virtuale
:: Nota: In Windows il percorso è Scripts (con la S finale)
call .venv\Scripts\activate

:: Avvia l'applicativo
python main.py

:: Mantiene la finestra aperta anche dopo la chiusura del programma Python
pause