import argparse
import csv
import shutil
from pathlib import Path
from config.commons import get_config_values_env_mig


def remove_duplicate_csv_rows(csv_path: Path, key_column: str = "nome_file", backup: bool = True) -> tuple[int, int]:
    """Remove righe duplicate da un CSV usando la colonna specificata come chiave."""
    csv_path = csv_path.expanduser().resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file non trovato: {csv_path}")

    with csv_path.open("r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise ValueError(f"CSV vuoto o intestazione non valida: {csv_path}")
        if key_column not in fieldnames:
            raise ValueError(
                f"Colonna '{key_column}' non trovata nelle intestazioni: {fieldnames}"
            )

        rows = list(reader)

    seen_keys = set()
    unique_rows = []
    duplicate_count = 0

    for row in rows:
        key_value = (row.get(key_column) or "").strip()
        if key_value in seen_keys:
            duplicate_count += 1
            continue
        seen_keys.add(key_value)
        unique_rows.append(row)

    if duplicate_count == 0:
        return len(rows), 0

    if backup:
        backup_path = csv_path.with_suffix(csv_path.suffix + ".bak")
        shutil.copy2(csv_path, backup_path)

    with csv_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_rows)

    return len(rows), duplicate_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rimuove righe duplicate da un file CSV basate sulla colonna 'nome_file'."
    )
    parser.add_argument(
        "csv_file",
        nargs="?",
        type=Path,
        help="Percorso del file CSV da processare. Se omesso verrà usato SHARED_IMAGES_PATH/dati_immagini/dati_immagini.csv.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Non creare un file di backup prima di riscrivere il CSV.",
    )
    parser.add_argument(
        "--column",
        default="nome_file",
        help="Nome della colonna da usare per individuare i duplicati (default: nome_file).",
    )
    return parser.parse_args()


def get_default_csv_path() -> Path:
    _, _, _, _, shared_images_path = get_config_values_env_mig()
    if not shared_images_path:
        raise EnvironmentError("Variabile SHARED_IMAGES_PATH non impostata nel file .env")
    return Path(shared_images_path) / "dati_immagini" / "dati_immagini.csv"


def main() -> None:
    args = parse_args()
    csv_path = args.csv_file if args.csv_file is not None else get_default_csv_path()

    try:
        total_rows, removed = remove_duplicate_csv_rows(
            csv_path,
            key_column=args.column,
            backup=not args.no_backup,
        )
    except Exception as error:
        raise SystemExit(f"Errore: {error}")

    if removed == 0:
        print(f"Nessuna riga duplicata trovata in {csv_path}.")
    else:
        print(
            f"Eliminati {removed} duplicati da {csv_path}. "
            f"Righe totali lette: {total_rows}."
        )
        if not args.no_backup:
            backup_path = csv_path.with_suffix(csv_path.suffix + ".bak")
            print(f"Backup creato in: {backup_path}")


if __name__ == "__main__":
    main()
