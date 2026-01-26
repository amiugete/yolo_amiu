from ultralytics import YOLO

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

def is_image_sensitive(image_path, conf_threshold=0.4):
    results = model(image_path, conf=conf_threshold)

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]

            if cls_name in SENSITIVE_CLASSES:
                return True, cls_name  # scarta subito

    return False, None

