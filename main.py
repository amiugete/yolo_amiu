from pathlib import Path
import logging
from config.commons import get_config_values_env, config_folder
from datetime import datetime
from engine.write_image_business import verify_and_process_images

############################# Configura il logging ##################################
log_file = Path("logs") / f"image_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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

# Carica variabili d'ambiente dal file .env
LIMIT, USER, PWD, BASE_API_URL_AUTH, IMAGES_STORE_PATH, OK_PATH, KO_PATH, SHARED_IMAGES_PATH = get_config_values_env()


def main():
    # Crea cartelle per immagini ok e ko
    config_folder(SHARED_IMAGES_PATH, OK_PATH, KO_PATH)

    limit = None
    if LIMIT is not None:
        try:
            limit = int(LIMIT)
            logger.info(f"Limite immagini impostato a: {limit}")
        except ValueError:
            logger.warning(f"Valore LIMIT_ROWS non valido: '{LIMIT}'. Verrà usato nessun limite.")
            limit = None

    verify_and_process_images(Path(SHARED_IMAGES_PATH), Path(KO_PATH), Path(OK_PATH), logger, limit=limit)
    logger.info("Processamento completato")
#####################################################################################################


if __name__ == "__main__":
    main()



