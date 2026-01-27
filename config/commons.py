# database.py
import os
from dotenv import load_dotenv
from pathlib import Path


# Carica le variabili dal file .env
load_dotenv()


def get_config_values_env():
    """
    Recupera i valori di configurazione dal file .env
    """
     # Recupera i valori dalle variabili d'ambiente
    LIMIT = os.getenv("LIMIT_ROWS")
    USER = os.getenv("USER_AUTH_API")
    PWD = os.getenv("USER_AUTH_PWD")
    BASE_API_URL_AUTH = os.getenv("BASE_API_URL_AUTH")
    IMAGES_STORE_PATH = os.getenv("IMAGES_STORE_PATH")
    OK_PATH = IMAGES_STORE_PATH + "/ok"
    KO_PATH = IMAGES_STORE_PATH + "/ko"

    return LIMIT, USER, PWD, BASE_API_URL_AUTH, IMAGES_STORE_PATH, OK_PATH, KO_PATH



def config_folder(store_path,ok_folder,ko_folder):
    """Crea le cartelle per il salvataggio delle immagini se non esistono"""
    images_folder = Path(store_path)
    images_folder.mkdir(parents=True, exist_ok=True)
    ok_folder = Path(images_folder / "ok")
    ko_folder = Path(images_folder / "ko")
    ok_folder.mkdir(exist_ok=True)
    ko_folder.mkdir(exist_ok=True)

