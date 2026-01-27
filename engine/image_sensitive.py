from ultralytics import YOLO
from logging import Logger

# Carica modello leggero (veloce e sufficiente)
model = YOLO("yolov8n.pt")

# Classi da considerare "sensibili"
SENSITIVE_CLASSES = {
    "person",
    "car",
    "motorcycle",
    "bus",
    "truck"
}

def is_image_sensitive(image_path, conf_threshold=0.15, logger: Logger = None):
    try:
        results = model(image_path, conf=conf_threshold)
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = model.names[cls_id]

                if cls_name in SENSITIVE_CLASSES:
                    if cls_name == "person":
                        return True, cls_name  # scarta subito
                    else:
                        x1, y1, x2, y2 = box.xyxy[0]
                        conf = box.conf[0]
                        w, h = x2 - x1, y2 - y1
                        return (True, cls_name) if w > 400 and h > 380 else (False, None)  # scarta subito se maggiore di 400 w e 380 h
    except Exception as e:
        if logger:
            logger.warning(f"Errore durante l'elaborazione dell'immagine {image_path}: {str(e)}")
        return False, None
    return False, None

