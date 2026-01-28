# database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import oracledb
import logging
from typing import List

# Carica le variabili dal file .env
load_dotenv()

# Recupera i valori dalle variabili d'ambiente
path_client = os.getenv("ORACLE_CLIENT_PATH")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# Inizializza il client Oracle
oracledb.init_oracle_client(lib_dir=path_client)
################# Strnga di connessione base dati Oracle ##########################
DATABASE_URL = f"oracle+oracledb://{user}:{password}@{host}:{port}/{db_name}"
engine = create_engine(DATABASE_URL)
logger = logging.getLogger(__name__)



#################### Funzione di esecuzione query ################################################
def execute_query(sql, params=None):
   try: 
        with engine.connect() as connection:
            result = connection.execute(text(sql), params or {})
            connection.commit() # Necessario per INSERT/UPDATE
            return result
   except Exception as e:
        logger.error(f"Errore SQL o di connessione: {str(e)}")
        return result
   
 #################### Funzione di esecuzione query multiple in transazione ########################
def execute_transaction_immagini(list_ids: List[int]) -> bool:
    """
    Riceve una lista di id_richiesta delle immagini per poi andare in update aggiornando il flg_lettura a 1
    """
    params = [{"id_val": id_val} for id_val in list_ids]
    try:
        with engine.begin() as connection:
            connection.execute(text("INSERT INTO STRADE.temp_id_richiesta (id) VALUES (:id_val)"), params)
            connection.execute(text("""UPDATE STRADE.SEGNALAZIONI_IMMAGINI
                                       SET FLG_LETTURA = 1
                                       WHERE ID_RICHIESTA IN 
                                      (SELECT id FROM STRADE.temp_id_richiesta)
                                    """))
        return True
    except Exception as e:
        logger.error(f"Transazione fallita: {e}")
        return False

