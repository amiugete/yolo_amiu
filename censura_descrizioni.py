import argparse
import csv
import re
import sys
from logging import Logger, basicConfig, getLogger
from pathlib import Path

import spacy
from spacy.matcher import Matcher
from config.commons import get_config_values_env_mig

# Carica modello italiano
nlp = spacy.load("it_core_news_sm")


def censura(valore: str) -> str:
    return "*" * len(valore)


def anonimizza_testo(testo: str) -> str:
    doc = nlp(testo)
    sostituzioni = []

    # ==========================
    # PERSONE / LUOGHI / AZIENDE
    # ==========================
    for ent in doc.ents:
        if ent.label_ in (
            "PER",   # Persona
            "LOC",   # Luogo
            "GPE",   # Città/Stato
            "ORG"    # Organizzazione
        ):
            sostituzioni.append((ent.start_char, ent.end_char))

    # ==========================
    # INDIRIZZI
    # ==========================
    matcher = Matcher(nlp.vocab)
    matcher.add(
        "INDIRIZZO",
        [[
            {
                "LOWER": {
                    "IN": [
                        "via",
                        "viale",
                        "piazza",
                        "corso",
                        "largo",
                        "vicolo"
                    ]
                }
            },
            {"IS_ALPHA": True, "OP": "+"},
            {"IS_DIGIT": True, "OP": "?"}
        ]]
    )

    matches = matcher(doc)
    for _, start, end in matches:
        span = doc[start:end]
        sostituzioni.append((span.start_char, span.end_char))

    # ==========================
    # NOMI IN MAIUSCOLO E NOMI DOPO "di"
    # ==========================
    for m in re.finditer(
        r"\b(?:[A-ZÀ-Ý]{2,})(?:\s+[A-ZÀ-Ý]{2,})+\b",
        testo
    ):
        sostituzioni.append((m.start(), m.end()))

    for m in re.finditer(
        r"\bdi\s+([A-ZÀ-Ý][a-zà-ÿ]+(?:\s+[A-ZÀ-Ý][a-zà-ÿ]+){0,3})\b",
        testo,
        flags=re.IGNORECASE
    ):
        start = m.start(1)
        end = m.end(1)
        sostituzioni.append((start, end))

    # ==========================
    # EMAIL
    # ==========================
    for m in re.finditer(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        testo
    ):
        sostituzioni.append((m.start(), m.end()))

    # ==========================
    # TELEFONI
    # ==========================
    for m in re.finditer(
        r"(?:\+39\s?)?(?:\d[\s\-]?){9,12}",
        testo
    ):
        sostituzioni.append((m.start(), m.end()))

    # ==========================
    # RIMUOVE DUPLICATI
    # ==========================
    sostituzioni = list(set(sostituzioni))

    # ==========================
    # ORDINA AL CONTRARIO
    # ==========================
    sostituzioni.sort(key=lambda x: x[0], reverse=True)

    risultato = testo

    # ==========================
    # APPLICA CENSURA
    # ==========================
    for start, end in sostituzioni:
        originale = risultato[start:end]
        risultato = risultato[:start] + censura(originale) + risultato[end:]

    return risultato


def censura_descrizioni(csv_path: Path, output_path: Path | None = None, logger: Logger | None = None) -> Path:
    if logger is None:
        logger = getLogger(__name__)

    if not csv_path.exists():
        raise FileNotFoundError(f"File CSV non trovato: {csv_path}")

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames or ["id_richiesta", "descrizione_richiesta", "nome_file"]
        rows = []

        for row in reader:
            descrizione = row.get("descrizione_richiesta", "")
            if descrizione:
                row["descrizione_richiesta"] = anonimizza_testo(descrizione)
            rows.append(row)

    output_path = output_path or csv_path.parent / f"{csv_path.stem}_censurato{csv_path.suffix}"
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"File CSV censurato scritto in: {output_path}")
    return output_path


def find_default_csv(start_folder: Path) -> Path | None:
    _, _, _, _, shared_images_path = get_config_values_env_mig()
    if shared_images_path:
        candidate = Path(shared_images_path) / "dati_immagini" / "dati_immagini.csv"
        if candidate.exists():
            return candidate

    candidate = start_folder / "images" / "dati_immagini" / "dati_immagini.csv"
    if candidate.exists():
        return candidate
    candidate = start_folder / "dati_immagini" / "dati_immagini.csv"
    if candidate.exists():
        return candidate
    return None


def main() -> int:
    basicConfig(level="INFO", format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(
        description="Censura le descrizioni del file CSV generato da _append_image_metadata_csv."
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        type=Path,
        help="Percorso del file CSV da leggere."
    )
    parser.add_argument(
        "--output",
        dest="output_path",
        type=Path,
        help="Percorso del file CSV di output censurato."
    )

    args = parser.parse_args()
    csv_path = args.csv_path or find_default_csv(Path.cwd())
    
    print(f"Utilizzo file CSV: {csv_path}")

    if csv_path is None:
        print("Errore: impossibile trovare il file CSV. Specifica il percorso con --csv.")
        return 1

    try:
        censura_descrizioni(csv_path, args.output_path)
    except Exception as exc:
        print(f"Errore durante l'elaborazione del CSV: {exc}")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
