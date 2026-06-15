import csv
import os
import requests
from models.models import SegnalazioneImmagine
from engine.image_sensitive import is_image_sensitive
from logging import Logger
import shutil
from pathlib import Path


def _append_image_metadata_csv(images_folder: Path, segnalazione: SegnalazioneImmagine, nome_file: str, logger: Logger):
    data_folder = images_folder / "dati_immagini"
    data_folder.mkdir(parents=True, exist_ok=True)
    csv_path = data_folder / "dati_immagini.csv"
    write_header = not csv_path.exists()

    try:
        with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if write_header:
                writer.writerow(["id_richiesta", "descrizione_richiesta", "nome_file"])
            writer.writerow([
                segnalazione.id_richiesta if segnalazione.id_richiesta is not None else "",
                segnalazione.descrizione_richiesta if segnalazione.descrizione_richiesta is not None else "",
                nome_file
            ])
        logger.info(f"Riga aggiunta a {csv_path}")
    except Exception as e:
        logger.warning(f"Impossibile scrivere su CSV {csv_path}: {e}")


def writeImageOnFolderImages(session_with_token: requests.Session, segnalazione: SegnalazioneImmagine, images_folder:Path,logger: Logger):
    """Funzione per scaricare immagine e salvarla nella cartella delle immagini"""
    if segnalazione.url is None:
        logger.warning(f"Segnalazione {segnalazione.id_richiesta} immagine non valida")
        return
    
    # Chiamata API per scaricare l'immagine
    logger.info(f"GET image URL: {segnalazione.url}")
    logger.info(f"Session headers: {dict(session_with_token.headers)}")
    response = session_with_token.get(segnalazione.url)
    logger.info(f"Request headers sent: {dict(response.request.headers)}")
    if response.status_code == 200:
        logger.info("Immagine scaricata con successo")
        image_path = images_folder / f"{str(segnalazione.id_richiesta)}.jpg"

        with open(image_path, "wb") as f:
            f.write(response.content)
            logger.info(f"Immagine salvata in {image_path}")
    else:
        logger.warning(f"Errore durante il download dell'immagine: {response.status_code}")
        
def writeImageOnFolderImages_update_csv(session_with_token: requests.Session, segnalazione: SegnalazioneImmagine, images_folder: Path, logger: Logger, image_index: int = 1):
    """Funzione per scaricare immagine, salvarla nella cartella delle immagini e aggiungere metadata al CSV"""
    if segnalazione.url is None:
        logger.warning(f"Segnalazione {segnalazione.id_richiesta} immagine non valida")
        return False
    
    # Chiamata API per scaricare l'immagine
    logger.info(f"GET image URL: {segnalazione.url}")
    logger.info(f"Session headers: {dict(session_with_token.headers)}")
    response = session_with_token.get(segnalazione.url)
    logger.info(f"Request headers sent: {dict(response.request.headers)}")
    if response.status_code == 200:
        logger.info("Immagine scaricata con successo")
        nome_file = f"{str(segnalazione.id_richiesta)}_{image_index}.jpg"
        image_path = images_folder / nome_file
        images_folder.mkdir(parents=True, exist_ok=True)

        with open(image_path, "wb") as f:
            f.write(response.content)
            logger.info(f"Immagine salvata in {image_path}")

        _append_image_metadata_csv(images_folder, segnalazione, nome_file, logger)
    else:
        logger.warning(f"Errore durante il download dell'immagine: {response.status_code}")
        return False
    
    return True

### Funzione per verificare e processare le immagini scaricate nella cartella ###
def verify_and_process_images(images_folder:Path,ko_folder:Path,ok_folder:Path,logger: Logger, limit=None, allowed_ids=None):
    """Verifica con modello AI locale verificandone prima l'estensione e copia le immagini nelle cartelle ok/ko.
    Se limit è fornito, processa al massimo quel numero di immagini.
    Se allowed_ids è fornito, processa solo i file le cui basi iniziano con uno degli id_richiesta."""
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}

    if not images_folder.exists() or not images_folder.is_dir():
        logger.warning(f"Cartella immagini inesistente o non valida: '{images_folder}'")
        return

    if limit is not None:
        try:
            limit = int(limit)
            if limit <= 0:
                logger.warning(f"Limite non valido ({limit}), considera nessun limite.")
                limit = None
            else:
                logger.info(f"Limite di immagini da processare: {limit}")
        except ValueError:
            logger.warning(f"Limite non valido: '{limit}'. Verrà usato nessun limite.")
            limit = None

    allowed_ids_set = None
    if allowed_ids is not None:
        allowed_ids_set = {str(i) for i in allowed_ids}
        logger.info(f"Filtro id_richiesta attivo: {len(allowed_ids_set)} id forniti")
        logger.debug(f"ID consentiti: {sorted(allowed_ids_set)}")
    else:
        logger.info("Nessun filtro id_richiesta fornito: processerò tutte le immagini supportate")

    def _matches_allowed_ids(filename: str) -> bool:
        if allowed_ids_set is None:
            return True
        stem = os.path.splitext(filename)[0]
        file_id = stem.split('_', 1)[0].split('.', 1)[0]
        match = file_id in allowed_ids_set
        logger.debug(f"Verifica file '{filename}' -> id='{file_id}' -> {'OK' if match else 'SKIP'}")
        return match

    processed_count = 0
    skipped_non_matching = 0
    skipped_non_image = 0
    scanned_count = 0

    logger.info(f"Inizio scansione cartella immagini: '{images_folder}'")

    with os.scandir(images_folder) as scanner:
        for entry in scanner:
            if limit is not None and processed_count >= limit:
                logger.info(f"Limite raggiunto: {processed_count} immagini processate")
                break

            scanned_count += 1
            if not entry.is_file():
                logger.debug(f"Ignorato non-file: {entry.name}")
                continue

            extension = os.path.splitext(entry.name)[1].lower()
            if extension not in IMAGE_EXTENSIONS:
                skipped_non_image += 1
                logger.debug(f"Ignorato estensione non immagine: {entry.name}")
                continue

            if not _matches_allowed_ids(entry.name):
                skipped_non_matching += 1
                continue

            image_path = images_folder / entry.name
            logger.info(f"Processo immagine: {entry.name}")
            sensitive, reason = is_image_sensitive(str(image_path), logger=logger)
            if sensitive:
                logger.warning(f"{entry.name} - SCARTATA (rilevato: {reason})")
                destination = ko_folder / entry.name
                shutil.move(str(image_path), destination)
                logger.info(f"Immagine spostata in: {destination}")
            else:
                logger.info(f"{entry.name} - OK")
                destination = ok_folder / entry.name
                shutil.move(str(image_path), destination)
                logger.info(f"Immagine spostata in: {destination}")
            processed_count += 1

    logger.info(f"Scansione completata: file esaminati={scanned_count}, immagini processate={processed_count}, immagini non matching={skipped_non_matching}, non immagini={skipped_non_image}")

    if processed_count == 0:
        if skipped_non_matching > 0:
            logger.warning(f"Nessuna immagine corrispondente agli id_richiesta trovata in '{images_folder}'")
        else:
            logger.warning(f"Nessuna immagine trovata nella cartella '{images_folder}'")
        return

    logger.info(f"Trovate {processed_count} immagini da processare")

