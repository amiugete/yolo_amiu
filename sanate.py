#Script di supporto per il processo di migrazione immagini, esegue operazioni simili a main.py ma con log dedicati e senza aggiornamento flag lettura immagini, utile per migrare immagini in caso di errori o per processare immagini non processate in precedenza e le salva sulla cartella condivisa

############################# Configura il logging ##################################
import csv
import logging
from datetime import datetime
from pathlib import Path
from config.database.database import reset_flg_archiviata_not_in_ids
from config.commons import get_config_values_env_mig


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


def extract_request_id_from_file_name(nome_file: str) -> str:
    """Estrae l'id_richiesta dal nome file '15651367_1.jpg' o '15651367_2'."""
    if not nome_file:
        return ""
    base_name = Path(nome_file).stem
    return base_name.split("_")[0] if "_" in base_name else base_name


def read_request_ids_from_csv(csv_path: Path) -> set[str]:
    ids = set()
    if not csv_path.exists():
        logger.error(f"CSV non trovato: {csv_path}")
        return ids

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            id_richiesta = str(row.get("id_richiesta", "") or "").strip()
            if "_" in id_richiesta:
                id_richiesta = id_richiesta.split("_")[0]

            if not id_richiesta:
                id_richiesta = extract_request_id_from_file_name(str(row.get("nome_file", "")).strip())

            if id_richiesta:
                ids.add(id_richiesta)

    return ids


def reset_flg_archiviata_from_csv(csv_path: Path) -> None:
    """Legge il CSV e resetta FLG_ARCHIVIATA a 0 per tutte le richieste non presenti nel CSV."""
    request_ids = read_request_ids_from_csv(csv_path)
    if not csv_path.exists():
        logger.error(f"CSV non trovato: {csv_path}")
        return

    success = reset_flg_archiviata_not_in_ids(sorted(request_ids))
    if success:
        logger.info(
            f"Reset FLG_ARCHIVIATA=0 per tutte le richieste non presenti nel CSV. Esclusi: {sorted(request_ids)}"
        )
    else:
        logger.error("Errore durante il reset FLG_ARCHIVIATA per le richieste non presenti nel CSV")


LIMIT, USER, PWD, BASE_API_URL_AUTH, SHARED_IMAGES_PATH = get_config_values_env_mig()

def main():
    csv_path = Path(SHARED_IMAGES_PATH) / "dati_immagini" / "dati_immagini.csv"
    reset_flg_archiviata_from_csv(csv_path)


if __name__ == "__main__":
    main()