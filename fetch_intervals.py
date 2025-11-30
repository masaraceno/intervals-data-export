#!/usr/bin/env python3
import argparse
import os
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

# Carica .env se presente
load_dotenv()

BASE_URL = os.getenv("INTERVALS_BASE_URL", "https://intervals.icu/api/v1")
API_KEY = os.getenv("INTERVALS_API_KEY")
ATHLETE_ID = os.getenv("INTERVALS_ATHLETE_ID", "0")  # 0 = atleta legato all'API key


def _check_config():
    if not API_KEY:
        raise RuntimeError(
            "INTERVALS_API_KEY non impostata. "
            "Crea un file .env (copiando .env.example) e inserisci la tua API key."
        )


def fetch_csv(endpoint: str, oldest: str, newest: str, out_path: Path):
    """
    Scarica un CSV dall'API di Intervals.icu e lo salva su disco.

    endpoint: es. 'activities.csv' o 'wellness.csv'
    oldest/newest: 'YYYY-MM-DD'
    """
    _check_config()

    url = f"{BASE_URL}/athlete/{ATHLETE_ID}/{endpoint}"
    params = {
        "oldest": oldest,
        "newest": newest,
    }

    # Basic auth: username = 'API_KEY', password = api key
    auth = ("API_KEY", API_KEY)

    print(f"[INFO] Richiedo {endpoint} da {oldest} a {newest} …")
    resp = requests.get(url, params=params, auth=auth)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Errore {resp.status_code} chiamando {url}\n"
            f"Risposta: {resp.text}"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(resp.content)
    print(f"[OK] Salvato {endpoint} in: {out_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scarica activities.csv e wellness.csv da Intervals.icu per un intervallo di date."
    )
    parser.add_argument(
        "--start",
        required=True,
        help="Data iniziale (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end",
        required=True,
        help="Data finale (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--out-dir",
        default="data",
        help="Cartella di output (default: data)",
    )
    return parser.parse_args()


def validate_date(date_str: str) -> str:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        raise SystemExit(f"Data non valida '{date_str}', usare formato YYYY-MM-DD") from e
    return date_str


def main():
    args = parse_args()
    start = validate_date(args.start)
    end = validate_date(args.end)
    out_dir = Path(args.out_dir)

    # File di output
    activities_path = out_dir / f"activities_{start}_to_{end}.csv"
    wellness_path = out_dir / f"wellness_{start}_to_{end}.csv"

    # Scarica Activities e Wellness
    fetch_csv("activities.csv", start, end, activities_path)
    fetch_csv("wellness.csv", start, end, wellness_path)

    print("\nFatto! Ora puoi caricare questi file in ChatGPT per l’analisi.")


if __name__ == "__main__":
    main()
