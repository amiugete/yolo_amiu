# Controllo Immagini Sensibili

Questo progetto permette di **analizzare immagini presenti in una cartella e identificare quelle sensibili**. I risultati vengono registrati sia sul terminale sia su un file di log.
Le immagine che vengono scartate sono quelle di cui verranno rilevate presenza di persone o veicoli

## Requisiti

* Python 3.10 versione esatta nel requirements per evitare conflitti con pytorch
* Modulo `image_sensitive` (per rilevare contenuti sensibili)
* Librerie standard: `pathlib`, `logging`, `datetime`

## Librerie
certifi==2026.1.4
charset-normalizer==3.4.4
contourpy==1.3.3
cycler==0.12.1
filelock==3.20.3
fonttools==4.61.1
fsspec==2026.1.0
idna==3.11
Jinja2==3.1.6
kiwisolver==1.4.9
MarkupSafe==3.0.3
matplotlib==3.10.8
mpmath==1.3.0
networkx==3.6.1
numpy==1.26.4
opencv-python==4.13.0.90
opencv-python-headless==4.11.0.86
packaging==26.0
pillow==10.2.0
polars==1.37.1
polars-runtime-32==1.37.1
psutil==7.2.1
pyparsing==3.3.2
python-dateutil==2.9.0.post0
PyYAML==6.0.3
requests==2.32.5
scipy==1.17.0
six==1.17.0
sympy==1.14.0
torch==2.1.2
torchvision==0.16.2
typing_extensions==4.15.0
ultralytics==8.4.7
ultralytics-thop==2.0.18
urllib3==2.6.3

## Installazione

1. Clona il repository o scarica i file.
2. Crea una cartella `images` nella stessa directory dello script.
3. Assicurati che il modulo `image_sensitive` sia installato:

```bash
```

## Struttura del progetto

```
.
├── images/                 # Immagini da analizzare
├── logs/                   # File di log generati dallo script
├── image_sensitive.py      # Modulo per rilevamento immagini sensibili
└── main.py                 # Script principale
```

## Come usare

1. Inserisci le immagini da controllare nella cartella `images`.
2. Esegui lo script:

```bash
python main.py
```

3. Lo script:

* Crea la cartella `logs` se non esiste.
* Genera un file di log con timestamp.
* Analizza immagini con estensioni supportate: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.webp`.
* Segnala sul terminale e nel log:

  * `OK` → immagine sicura
  * `SCARTATA` → immagine sensibile, con motivo

## Esempio di output

```
2026-01-26 14:32:01 - INFO - Trovate 5 immagini da processare
2026-01-26 14:32:02 - INFO - immagine1.jpg - OK
2026-01-26 14:32:02 - WARNING - immagine2.png - SCARTATA (rilevato: nudità)
2026-01-26 14:32:03 - INFO - Processamento completato
```

## Personalizzazione

* Cambia la cartella delle immagini modificando `images_folder`.
* Modifica le estensioni supportate tramite `image_extensions`.
* Cambia il livello di logging (`INFO`, `DEBUG`, `WARNING`) nel `basicConfig`.



