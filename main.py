from image_sensitive import is_image_sensitive
from pathlib import Path
import logging
from datetime import datetime

# Configura il logging
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

images_folder = Path("images")
images_folder.mkdir(exist_ok=True)

# Estensioni immagine supportate
image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}

# Prendi tutti i file immagine dalla cartella
image_files = [f for f in images_folder.iterdir() if f.suffix.lower() in image_extensions]

if not image_files:
    logger.warning(f"Nessuna immagine trovata nella cartella '{images_folder}'")
else:
    logger.info(f"Trovate {len(image_files)} immagini da processare")
    
    for image_path in image_files:
        sensitive, reason = is_image_sensitive(str(image_path))
        
        if sensitive:
            logger.warning(f"{image_path.name} - SCARTATA (rilevato: {reason})")
        else:
            logger.info(f"{image_path.name} - OK")
    
    logger.info("Processamento completato")