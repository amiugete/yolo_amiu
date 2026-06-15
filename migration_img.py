#Script di supporto per il processo di migrazione immagini, esegue operazioni simili a main.py ma con log dedicati e senza aggiornamento flag lettura immagini, utile per migrare immagini in caso di errori o per processare immagini non processate in precedenza e le salva sulla cartella condivisa

############################# Configura il logging ##################################
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from config.database.database import execute_query
from engine.write_image_business import writeImageOnFolderImages_update_csv
from repository.segnalazioni_immagini_repo import get_segnalazioni_immagini, get_segnalazioni_immagini_da_archiviare, update_flg_archiviata_segnalazioni_immagini
from config.commons import  get_config_values_env_mig
from models.models import SegnalazioneImmagine
from rest.client import get_auth_session


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


LIMIT, USER, PWD, BASE_API_URL_AUTH, SHARED_IMAGES_PATH = get_config_values_env_mig()

def main():
    logger.info("Inizio processo di migrazione immagini")
    # Strappo il token di autenticazione per le chiamate API
    session_with_token = get_auth_session(USER, PWD, BASE_API_URL_AUTH)

    #Esegue query per prendere le immagini da archiviare
    sql = get_segnalazioni_immagini_da_archiviare()
    resultSet = execute_query(sql, {"limit": LIMIT})
    segnalazioniImmagini = [SegnalazioneImmagine(**row) for row in resultSet.mappings()]
    logger.info("Esecuzione query per recuperare immagini da archiviare")

    if segnalazioniImmagini is not None and len(segnalazioniImmagini) > 0:
        # Raggruppa le immagini per id_richiesta per gestire più immagini per richiesta
        grouped = defaultdict(list)
        for seg in segnalazioniImmagini:
            grouped[seg.id_richiesta].append(seg)

        for id_richiesta, gruppo in grouped.items():
            for idx, segnalazione in enumerate(gruppo, start=1):
                success = writeImageOnFolderImages_update_csv(session_with_token, segnalazione, Path(SHARED_IMAGES_PATH), logger, idx)
                if  success:
                    sql_update = update_flg_archiviata_segnalazioni_immagini()
                    execute_query(sql_update, {"id_richiesta": id_richiesta, "url": segnalazione.url})
    else:
        logger.info("Nessuna immagine da archiviare")






if __name__ == "__main__":
    main()