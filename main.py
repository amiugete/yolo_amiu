from engine.image_sensitive import is_image_sensitive
from pathlib import Path
import logging
from repository.segnalazioni_immagini_repo import get_segnalazioni_immagini
from config.database.database import execute_query,execute_transaction_immagini
from rest.client import get_auth_session
from config.commons import get_config_values_env,config_folder
from models.models import SegnalazioneImmagine
from datetime import datetime
from engine.write_image_business import writeImageOnFolderImages,verify_and_process_images

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
LIMIT, USER, PWD, BASE_API_URL_AUTH, IMAGES_STORE_PATH, OK_PATH, KO_PATH = get_config_values_env()
# Crea cartelle per immagini ok e ko
config_folder(IMAGES_STORE_PATH, OK_PATH, KO_PATH)

# Strappo il token di autenticazione per le chiamate API
session_with_token = get_auth_session(USER, PWD, BASE_API_URL_AUTH)

#Esegue query per prendere le immagini da processare
sql = get_segnalazioni_immagini()
resultSet = execute_query(sql, {"limit": LIMIT})
segnalazioniImmagini = [SegnalazioneImmagine(**row) for row in resultSet.mappings()]
logger.info("Esecuzione query per recuperare immagini da processare")

if segnalazioniImmagini is not None and len(segnalazioniImmagini) > 0:
    for segnalazione in segnalazioniImmagini:
        writeImageOnFolderImages(session_with_token, segnalazione, Path(IMAGES_STORE_PATH),logger)
    verify_and_process_images(Path(IMAGES_STORE_PATH), Path(KO_PATH), Path(OK_PATH),logger)
    listaId = [segnalazione.id_richiesta for segnalazione in segnalazioniImmagini]
    esito = execute_transaction_immagini(listaId)
    if esito:
        logger.info("Aggiornamento flag lettura immagini avvenuto con successo")
    else:
        logger.error("Errore durante l'aggiornamento flag lettura immagini")

else:
    logger.info("Nessuna immagine da processare")

logger.info("Processamento completato")
#####################################################################################################






