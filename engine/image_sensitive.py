from ultralytics import YOLO
from logging import Logger
import re
import numpy as np

# Carica modello leggero per rilevamento oggetti generici
model = YOLO("yolov8n.pt")

# Classi da considerare "sensibili"
SENSITIVE_CLASSES = {
    "person",
    "car",
    "motorcycle",
    "bus",
    "truck"
}

# Pattern targa generico: copre IT (AB123CD), EU e altri formati
_PLATE_PATTERN = re.compile(
    r'\b(?:[A-Z]{1,3}[\s\-]?\d{2,4}[\s\-]?[A-Z]{0,3}|\d{2,4}[\s\-]?[A-Z]{2,4})\b',
    re.IGNORECASE
)

# Modello dedicato al rilevamento targhe (lazy-loaded da HuggingFace)
_plate_detector = None

def _get_plate_detector():
    """Carica il modello YOLOv8 dedicato al rilevamento targhe (una sola volta)."""
    global _plate_detector
    if _plate_detector is None:
        _plate_detector = YOLO("keremberke/yolov8n-license-plate-detection")
    return _plate_detector

# Reader OCR inizializzato una sola volta (lazy) — usato come fallback
_ocr_reader = None

def _get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        import easyocr
        _ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    return _ocr_reader

def _has_plate_in_crop(image_path, x1, y1, x2, y2, conf_plate=0.25):
    """
    Primo livello: usa il plate detector YOLOv8 dedicato sul crop del veicolo.
    Ritorna True se rileva almeno una targa con confidenza >= conf_plate.
    """
    try:
        from PIL import Image
        img = Image.open(image_path)
        # Allarga leggermente il crop per non tagliare targhe sul bordo
        W, H = img.size
        pad_x = int((x2 - x1) * 0.1)
        pad_y = int((y2 - y1) * 0.1)
        crop = img.crop((
            max(0, int(x1) - pad_x),
            max(0, int(y1) - pad_y),
            min(W, int(x2) + pad_x),
            min(H, int(y2) + pad_y),
        ))
        detector = _get_plate_detector()
        results = detector(crop, conf=conf_plate, verbose=False)
        for r in results:
            if len(r.boxes) > 0:
                return True
        return False
    except Exception:
        return False

def _is_plate_readable_ocr(image_path, x1, y1, x2, y2):
    """
    Secondo livello (fallback): OCR sul crop del veicolo.
    Ritorna True se trova testo che corrisponde a un pattern targa.
    Soglia di confidenza abbassata a 0.35 per maggiore sensibilità.
    """
    try:
        from PIL import Image
        img = Image.open(image_path)
        crop = img.crop((int(x1), int(y1), int(x2), int(y2)))
        arr = np.array(crop)
        reader = _get_ocr_reader()
        results = reader.readtext(arr, detail=1)
        for (_, text, prob) in results:
            clean = re.sub(r'\s+', '', text).upper()
            if prob >= 0.35 and _PLATE_PATTERN.search(clean):
                return True
        return False
    except Exception:
        return False

def is_image_sensitive(image_path, conf_threshold=0.15, logger: Logger = None):
    try:
        results = model(image_path, conf=conf_threshold, verbose=False)
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = model.names[cls_id]

                if cls_name in SENSITIVE_CLASSES:
                    if cls_name == "person":
                        return True, cls_name  # persona → scarta subito
                    if cls_name == "car":
                        return True, cls_name  # veicolo → scarta subito
                    if cls_name == "bicycle":
                        return True, cls_name  # bicicletta → scarta subito
                    if cls_name == "motorbike":
                        return True, cls_name  # motociclo → scarta subito

                    # # Veicolo: controlla targa con plate detector (livello 1)
                    # x1, y1, x2, y2 = box.xyxy[0]
                    # if _has_plate_in_crop(image_path, x1, y1, x2, y2):
                    #     return True, cls_name  # targa rilevata dal detector

                    # # Fallback OCR (livello 2) se il detector non trova nulla
                    # if _is_plate_readable_ocr(image_path, x1, y1, x2, y2):
                    #     return True, cls_name  # targa trovata via OCR

    except Exception as e:
        if logger:
            logger.warning(f"Errore durante l'elaborazione dell'immagine {image_path}: {str(e)}")
        return False, None
    return False, None

