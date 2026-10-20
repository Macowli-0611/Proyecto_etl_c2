"""Primary Source Extraction Module: Policía Nacional Domestic Violence Dataset.

Acquires the raw primary dataset, verifies provenance, computes SHA-256 hash,
records manifest metadata, and provides raw data without applying cleaning or business rules.
"""

import hashlib
import json
import logging
import os
import urllib.request
from datetime import datetime
from typing import Dict, Tuple

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ExtractPrimary")

PRIMARY_URL = os.getenv(
    "PRIMARY_DATA_URL",
    "https://www.datos.gov.co/api/views/vuyt-mqpw/rows.csv?accessType=DOWNLOAD"
)
RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
MANIFEST_PATH = os.path.join(RAW_DIR, "primary_source_manifest.json")
DEFAULT_CSV_PATH = os.path.join(
    RAW_DIR, "Reporte_Delito_Violencia_Intrafamiliar_Policía_Nacional_20260902.csv"
)


def compute_sha256(filepath: str) -> str:
    """Calculates SHA-256 hash of a file in chunks."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_primary_data(filepath: str = None) -> Tuple[pd.DataFrame, Dict]:
    """Acquires the raw primary dataset from local cache or downloads from datos.gov.co.

    Returns:
        Tuple[pd.DataFrame, Dict]: Raw dataframe and provenance metadata manifest.
    """
    os.makedirs(RAW_DIR, exist_ok=True)
    target_path = filepath or DEFAULT_CSV_PATH

    if not os.path.exists(target_path):
        logger.info("Primary raw CSV not found locally. Downloading from %s...", PRIMARY_URL)
        req = urllib.request.Request(
            PRIMARY_URL,
            headers={"User-Agent": "ETL-Pipeline-DIJIN/2.0"}
        )
        with urllib.request.urlopen(req) as response, open(target_path, "wb") as out_file:
            while chunk := response.read(8192 * 1024):
                out_file.write(chunk)
        logger.info("Download completed successfully: %s", target_path)
    else:
        logger.info("Loading cached primary raw CSV from %s...", target_path)

    # Read all columns as string to prevent loss of leading zeros in DANE codes
    logger.info("Reading raw CSV into memory (dtype=str)...")
    df_raw = pd.read_csv(target_path, dtype=str)

    sha256_hash = compute_sha256(target_path)
    file_size = os.path.getsize(target_path)
    row_count = len(df_raw)

    total_victims = int(pd.to_numeric(df_raw["CANTIDAD"], errors="coerce").fillna(0).sum())
    min_date = df_raw["FECHA HECHO"].min()
    max_date = df_raw["FECHA HECHO"].max()

    manifest = {
        "source_name": "Reporte Delito Violencia Intrafamiliar - Policía Nacional (DIJIN)",
        "source_url": PRIMARY_URL,
        "extraction_timestamp": datetime.now().isoformat(),
        "local_filepath": target_path,
        "sha256": sha256_hash,
        "file_size_bytes": file_size,
        "row_count": row_count,
        "total_victims_raw": total_victims,
        "date_range": {"min": str(min_date), "max": str(max_date)},
        "columns": list(df_raw.columns)
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info(
        "Primary extract ready: %d records, %d victims, SHA-256: %s...",
        row_count, total_victims, sha256_hash[:16]
    )
    return df_raw, manifest


if __name__ == "__main__":
    df, manifest = extract_primary_data()
    print("Manifest:", json.dumps(manifest, indent=2))
