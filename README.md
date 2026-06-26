# yolo_amiu

Questo repository contiene script Python per gestire immagini sensibili, migrare immagini da un sistema esterno, ripristinare immagini, e anonimizzare/mettere in ordine file CSV.

## Panorama generale

- `main.py` = controlla immagini nella cartella condivisa e le sposta in `ok/` o `ko/`.
- `migration_img.py` = scarica immagini da API/database e le salva nella cartella condivisa, aggiornando un CSV di metadati.
- `sanate.py` = ripristina il flag di archiviazione nel database per le richieste non presenti nel CSV.
- `rollback.py` = riporta le immagini da `ok/` e `ko/` nella cartella `shared_images`.
- `censura_descrizioni.py` = anonimizza contenuti sensibili in un file CSV.
- `dupplicati.py` = elimina righe duplicate da un file CSV.

## Cosa fa ogni script

### `main.py`
- Legge la configurazione dal file `.env`.
- Crea le cartelle `ok/` e `ko/` dentro `SHARED_IMAGES_PATH`.
- Scorre le immagini valide nella cartella condivisa.
- Usa il modello di rilevamento per decidere se un’immagine è sensibile.
- Sposta le immagini sensibili in `ko/` e le altre in `ok/`.
- Scrive log su file e console.

### `migration_img.py`
- Si autentica via API usando le credenziali in `.env`.
- Esegue query per recuperare segnalazioni immagini dal database.
- Scarica le immagini remote e le salva in `SHARED_IMAGES_PATH`.
- Scrive un file CSV `dati_immagini/dati_immagini.csv` con `id_richiesta`, `descrizione_richiesta`, `nome_file`.
- Aggiorna il flag `FLG_ARCHIVIATA = 1` per le immagini archiviate.

### `sanate.py`
- Legge il CSV generato nella cartella condivisa.
- Estrae gli `id_richiesta` presenti nel CSV.
- Chiama una funzione per resettare `FLG_ARCHIVIATA = 0` nel database per tutte le richieste non presenti nel CSV.
- Utile quando si vuole correggere lo stato di archiviazione dopo una migrazione o un errore.

### `rollback.py`
- Legge la configurazione dal file `.env`.
- Sposta tutti i file immagine da `OK_PATH` e `KO_PATH` nella cartella `SHARED_IMAGES_PATH`.
- Salta i file che non sono immagini o che già esistono nella cartella di destinazione.
- Serve a ripristinare le immagini nella cartella condivisa.

### `censura_descrizioni.py`
- Prende in input un CSV con colonne come `id_richiesta`, `descrizione_richiesta`, `nome_file`.
- Anonimizza il testo in `descrizione_richiesta`, censurando:
  - persone, organizzazioni, luoghi
  - indirizzi
  - email
  - numeri di telefono
  - nomi in maiuscolo e nomi dopo "di"
- Salva i risultati in un nuovo file con suffisso `_censurato`.
- Usa spaCy per il riconoscimento entità in italiano.

### `dupplicati.py`
- Legge un file CSV e controlla le righe duplicate.
- Usa la colonna `nome_file` (default) per identificare i duplicati.
- Riscrive il CSV senza duplicati e crea un backup con estensione `.bak`.
- Utile per pulire CSV di metadati prima di usarli in altri script.

## Requisiti principali

- Python 3.10
- `pytorch`
- `ultralytics`
- `spacy`
- `oracledb`
- `requests`
- `python-dotenv`

Installa le dipendenze con:

```bash
python -m pip install -r requirements.txt
```

## Configurazione

Crea un file `.env` con almeno queste variabili:

- `LIMIT_ROWS`
- `USER_AUTH_API`
- `USER_AUTH_PWD`
- `BASE_API_URL_AUTH`
- `SHARED_IMAGES_PATH`
- `IMAGES_STORE_PATH`

`config.commons` legge queste variabili per definire:
- `SHARED_IMAGES_PATH`
- `OK_PATH`
- `KO_PATH`

## Esempi d’uso

```bash
python main.py
python migration_img.py
python rollback.py
python censura_descrizioni.py --csv path/to/file.csv
python dupplicati.py path/to/file.csv
```

## Log

- Gli script scrivono i log nella cartella `logs/`.
- I file di log includono un timestamp nel nome.

## Note rapide

- `main.py` elabora immagini già presenti in `SHARED_IMAGES_PATH`.
- `migration_img.py` scarica immagini remote e aggiorna il CSV.
- `sanate.py` corregge lo stato dei flag nel database.
- `rollback.py` ripristina immagini in `shared_images`.
- `censura_descrizioni.py` anonimizza descrizioni CSV.
- `dupplicati.py` rimuove righe duplicate da un CSV.



