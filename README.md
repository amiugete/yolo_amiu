# Controllo Immagini Sensibili

Questo progetto permette di **analizzare immagini presenti in una cartella e identificare quelle sensibili**. I risultati vengono registrati sia sul terminale sia su un file di log.

## Requisiti

* Python 3.8 o superiore
* Modulo `image_sensitive` (per rilevare contenuti sensibili)
* Librerie standard: `pathlib`, `logging`, `datetime`

## Installazione

1. Clona il repository o scarica i file.
2. Crea una cartella `images` nella stessa directory dello script.
3. Assicurati che il modulo `image_sensitive` sia installato:

```bash
pip install image_sensitive  # se disponibile tramite pip
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
