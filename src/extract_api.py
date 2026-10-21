"""API Source Extraction Module: Comisarías de Familia (Ministerio de Justicia / datos.gov.co).

Programmatically extracts the Comisarías de Familia dataset via SODA REST API,
applies pagination, includes retry logic with exponential backoff for network resilience,
persists raw response for reproducibility, and computes provenance manifest.
"""

import hashlib
import json
import logging
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ExtractAPI")

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://www.datos.gov.co/resource/7tuu-upb2.json"
)
API_APP_TOKEN = os.getenv("API_APP_TOKEN", "")
API_TIMEOUT = int(os.getenv("API_TIMEOUT_SECONDS", "30"))
API_PAGE_LIMIT = int(os.getenv("API_PAGE_LIMIT", "2000"))

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
API_RAW_JSON_PATH = os.path.join(RAW_DIR, "api_comisarias_raw.json")
MANIFEST_PATH = os.path.join(RAW_DIR, "api_source_manifest.json")


def fetch_api_page_with_retry(
    url: str,
    params: Dict[str, str],
    max_retries: int = 3,
    backoff_factor: float = 1.5
) -> List[Dict]:
    """Fetches a page of data from the SODA REST API with retry on transient failures."""
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}" if query_string else url

    headers = {
        "User-Agent": "ETL-Pipeline-MinJusticia-Comisarias/2.0",
        "Accept": "application/json"
    }
    if API_APP_TOKEN and API_APP_TOKEN != "your_app_token_here_optional":
        headers["X-App-Token"] = API_APP_TOKEN

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(full_url, headers=headers)
            with urllib.request.urlopen(req, timeout=API_TIMEOUT) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return data
                else:
                    raise urllib.error.HTTPError(
                        full_url, response.status, f"HTTP Error {response.status}", response.headers, None
                    )
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            logger.warning(
                "Attempt %d/%d failed when querying API (%s). Error: %s",
                attempt, max_retries, full_url, e
            )
            if attempt == max_retries:
                logger.error("Exceeded maximum retries for API endpoint.")
                raise e
            sleep_time = backoff_factor ** attempt
            logger.info("Sleeping %.1f seconds before retry...", sleep_time)
            time.sleep(sleep_time)

    return []


def extract_api_data(
    filepath: str = None,
    offline_mode: bool = False,
    force_refresh: bool = True
) -> Tuple[pd.DataFrame, Dict]:
    """Programmatically extracts all records from the Comisarías de Familia SODA API.

    Uses pagination to guarantee complete acquisition regardless of API page limits.
    Persists the raw JSON payload and generates a cryptographic provenance manifest.
    If external network or API fails, gracefully falls back to local cache if present.

    Args:
        filepath: Optional path to an already extracted JSON file (for downstream tasks).
        offline_mode: If True, skips network call and loads from local cache.
        force_refresh: If True (default), always attempts live API call first.

    Returns:
        Tuple[pd.DataFrame, Dict]: Raw API dataframe and manifest dictionary.
    """
    os.makedirs(RAW_DIR, exist_ok=True)
    target_path = filepath or API_RAW_JSON_PATH
    all_records: List[Dict] = []
    fallback_used = False

    # Scenario 1: Downstream task requested a specific filepath
    if filepath and os.path.exists(filepath):
        logger.info("Loading specified API raw payload from %s...", filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            all_records = json.load(f)
        target_path = filepath

    # Scenario 2: Offline mode requested
    elif offline_mode and os.path.exists(API_RAW_JSON_PATH):
        logger.info("Offline mode requested: loading cached API payload from %s...", API_RAW_JSON_PATH)
        with open(API_RAW_JSON_PATH, "r", encoding="utf-8") as f:
            all_records = json.load(f)
        fallback_used = True

    # Scenario 3: Operational workflow - Live Programmatic Extraction via SODA REST API
    else:
        logger.info("Initiating programmatic extraction from SODA API: %s", API_BASE_URL)
        offset = 0
        limit = API_PAGE_LIMIT
        try:
            while True:
                params = {
                    "$limit": str(limit),
                    "$offset": str(offset),
                    "$order": ":id"
                }
                logger.info("Fetching API batch: offset=%d, limit=%d...", offset, limit)
                page_records = fetch_api_page_with_retry(API_BASE_URL, params)
                if not page_records:
                    break

                all_records.extend(page_records)
                logger.info("Retrieved %d records in current batch. Total: %d", len(page_records), len(all_records))

                if len(page_records) < limit:
                    break
                offset += limit

            logger.info("API extraction complete. Total records retrieved: %d", len(all_records))

            # Persist raw response for audit, inspection and offline reproducibility
            with open(API_RAW_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(all_records, f, indent=2, ensure_ascii=False)
            logger.info("Persisted raw API response to %s", API_RAW_JSON_PATH)

        except Exception as e:
            if os.path.exists(API_RAW_JSON_PATH):
                logger.warning(
                    "Live API query failed (%s). Falling back to local cache %s to guarantee operational continuity.",
                    e, API_RAW_JSON_PATH
                )
                with open(API_RAW_JSON_PATH, "r", encoding="utf-8") as f:
                    all_records = json.load(f)
                fallback_used = True
            else:
                logger.error("API query failed and no local cache is available!")
                raise e

    # Read into pandas dataframe as text strings
    df_raw = pd.DataFrame(all_records).astype(str)

    # Compute hash of raw file
    hasher = hashlib.sha256()
    with open(target_path, "rb") as f:
        while chunk := f.read(8192 * 1024):
            hasher.update(chunk)
    sha256_hash = hasher.hexdigest()

    manifest = {
        "source_name": "Caracterización de las comisarías de familia en el territorio nacional",
        "provider": "Ministerio de Justicia y del Derecho / Presidencia de la República",
        "api_endpoint": API_BASE_URL,
        "extraction_timestamp": datetime.now().isoformat(),
        "local_filepath": target_path,
        "sha256": sha256_hash,
        "row_count": len(df_raw),
        "columns": list(df_raw.columns),
        "distinct_municipalities_raw": int(df_raw["c_digo_dane_municipio"].nunique()) if "c_digo_dane_municipio" in df_raw.columns else 0,
        "fallback_to_cache": fallback_used
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info(
        "API manifest written: %d records, %d distinct municipalities, SHA-256: %s... (fallback=%s)",
        len(df_raw), manifest["distinct_municipalities_raw"], sha256_hash[:16], fallback_used
    )

    return df_raw, manifest


if __name__ == "__main__":
    df, manifest = extract_api_data()
    print("API Manifest Summary:")
    print(json.dumps(manifest, indent=2))
