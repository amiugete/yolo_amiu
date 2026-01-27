import requests
from models.models import SegnalazioneImmagine
from engine.image_sensitive import is_image_sensitive
from logging import Logger
import shutil
from pathlib import Path


def writeImageOnFolderImages(session_with_token: requests.Session, segnalazione: SegnalazioneImmagine, images_folder:Path,logger: Logger):
    """Funzione per scaricare immagine e salvarla nella cartella delle immagini"""
    if segnalazione.url is None:
        logger.warning(f"Segnalazione {segnalazione.id_richiesta} immagine non valida")
        return
    
    #Chiamata API per scaricare l'immagine
    response = session_with_token.get(segnalazione.url)
    if response.status_code == 200:
        logger.info("Immagine scaricata con successo")
        image_path = images_folder / f"{str(segnalazione.id_richiesta)}.jpg"

        with open(image_path, "wb") as f:
            f.write(response.content)
            print(f"Immagine salvata in {image_path}")
    else:
        logger.warning(f"Errore durante il download dell'immagine: {response.status_code}")

### Funzione per verificare e processare le immagini scaricate nella cartella ###
def verify_and_process_images(images_folder:Path,ko_folder:Path,ok_folder:Path,logger: Logger):
    """Verifica con modello AI locale verificandone prima l'estensione e sposta le immagini nelle cartelle ok/ko"""
    #Prendi tutti i file immagine dalla cartella
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    image_files = [f for f in images_folder.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS and f.is_file()]
    if not image_files:
        logger.warning(f"Nessuna immagine trovata nella cartella '{images_folder}'")
    else:
        logger.info(f"Trovate {len(image_files)} immagini da processare")

        for image_path in image_files:
            sensitive, reason = is_image_sensitive(str(image_path), logger=logger)
            if sensitive:
                logger.warning(f"{image_path.name} - SCARTATA (rilevato: {reason})")
                # Copia l'immagine nella cartella ko
                destination = ko_folder / image_path.name
                shutil.copy2(image_path, destination)
                logger.info(f"Immagine spostata in: {destination}")
            else:
                logger.info(f"{image_path.name} - OK")
                # Copia l'immagine nella cartella ok
                destination = ok_folder / image_path.name
                shutil.copy2(image_path, destination)
                logger.info(f"Immagine spostata in: {destination}")

