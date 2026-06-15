from pathlib import Path
import logging
import shutil
import os
from datetime import datetime
from config.commons import get_config_values_env

############################# Configura il logging ##################################
log_file = Path("logs") / f"rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_file.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}


def rollback_images(shared_path: Path, ok_path: Path, ko_path: Path):
    """Sposta tutti i file immagine da ok/ e ko/ di nuovo nella cartella padre shared_images."""
    moved = 0
    errors = 0

    for source_folder in (ok_path, ko_path):
        if not source_folder.exists():
            logger.warning(f"Cartella non trovata, saltata: '{source_folder}'")
            continue

        logger.info(f"Elaboro cartella: '{source_folder}'")
        with os.scandir(source_folder) as scanner:
            for entry in scanner:
                if not entry.is_file():
                    continue
                ext = os.path.splitext(entry.name)[1].lower()
                if ext not in IMAGE_EXTENSIONS:
                    logger.debug(f"Ignorato non-immagine: {entry.name}")
                    continue

                destination = shared_path / entry.name
                if destination.exists():
                    logger.warning(f"File già presente in shared_images, saltato: {entry.name}")
                    continue

                try:
                    shutil.move(str(entry.path), str(destination))
                    logger.info(f"Spostato: {source_folder.name}/{entry.name} -> {destination}")
                    moved += 1
                except Exception as e:
                    logger.error(f"Errore spostando {entry.name}: {e}")
                    errors += 1

    logger.info(f"Rollback completato: {moved} immagini ripristinate, {errors} errori.")


def main():
    _, _, _, _, _, OK_PATH, KO_PATH, SHARED_IMAGES_PATH = get_config_values_env()

    shared_path = Path(SHARED_IMAGES_PATH)
    ok_path = Path(OK_PATH)
    ko_path = Path(KO_PATH)

    if not shared_path.exists():
        logger.error(f"Cartella SHARED_IMAGES_PATH non trovata: '{shared_path}'")
        return

    logger.info(f"Rollback: ok='{ok_path}', ko='{ko_path}' -> shared='{shared_path}'")
    rollback_images(shared_path, ok_path, ko_path)


if __name__ == "__main__":
    main()
