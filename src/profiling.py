"""Data Profiling Module for Primary and API Sources.

Evaluates schemas, completeness, uniqueness, candidate keys, categorical domains,
numerical ranges, temporal coverage, and cross-source integration matching.
CRITICAL: Profiling only OBSERVES and produces evidence. It does NOT modify data.
"""

import json
import logging
import os
from typing import Any, Dict

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("Profiling")

EVIDENCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "evidence")


def profile_primary_source(df_raw: pd.DataFrame) -> Dict[str, Any]:
    """Profiles the raw primary dataset from Policía Nacional (DIJIN)."""
    logger.info("Profiling Primary Source (%d rows)...", len(df_raw))

    # Basic stats
    total_rows = len(df_raw)
    null_counts = {col: int(df_raw[col].isna().sum()) for col in df_raw.columns}
    null_percentages = {col: round(cnt / total_rows * 100, 3) for col, cnt in null_counts.items()}

    # Measure stats
    cantidad_numeric = pd.to_numeric(df_raw["CANTIDAD"], errors="coerce")
    invalid_measure_cnt = int(cantidad_numeric.isna().sum())
    total_victims = int(cantidad_numeric.fillna(0).sum())
    min_victims = float(cantidad_numeric.min())
    max_victims = float(cantidad_numeric.max())
    mean_victims = round(float(cantidad_numeric.mean()), 2)

    # Key and Geography profiling
    dane_col = df_raw["CODIGO DANE"].astype(str)
    distinct_dane_8 = int(dane_col.nunique())
    muni_code_5 = dane_col.str[:5]
    distinct_muni_5 = int(muni_code_5.nunique())
    dane_len_distribution = dane_col.str.len().value_counts().to_dict()

    # Temporal profiling
    dates = pd.to_datetime(df_raw["FECHA HECHO"], format="%d/%m/%Y", errors="coerce")
    unparseable_dates = int(dates.isna().sum())
    min_date = str(dates.min().date()) if unparseable_dates == 0 else "N/A"
    max_date = str(dates.max().date()) if unparseable_dates == 0 else "N/A"
    distinct_dates = int(dates.nunique())

    # Categorical distributions
    genero_dist = df_raw["GENERO"].value_counts(dropna=False).to_dict()
    grupo_etario_dist = df_raw["GRUPO ETARIO"].value_counts(dropna=False).to_dict()
    armas_dist = df_raw["ARMAS MEDIOS"].value_counts(dropna=False).to_dict()

    evidence = {
        "dataset_name": "Reporte Delito Violencia Intrafamiliar - Policía Nacional",
        "total_records": total_rows,
        "null_counts": null_counts,
        "null_percentages": null_percentages,
        "measure_profiling": {
            "attribute": "CANTIDAD",
            "total_victims": total_victims,
            "min": min_victims,
            "max": max_victims,
            "mean": mean_victims,
            "invalid_measure_count": invalid_measure_cnt
        },
        "geographic_profiling": {
            "distinct_8_digit_dane": distinct_dane_8,
            "distinct_5_digit_municipalities": distinct_muni_5,
            "dane_length_distribution": {str(k): int(v) for k, v in dane_len_distribution.items()},
            "malformed_dane_rows": int(df_raw[dane_col.str.startswith("00000") | dane_col.str.startswith("52000")].shape[0])
        },
        "temporal_profiling": {
            "unparseable_dates": unparseable_dates,
            "min_date": min_date,
            "max_date": max_date,
            "distinct_calendar_days": distinct_dates
        },
        "categorical_domains": {
            "genero": {str(k): int(v) for k, v in genero_dist.items()},
            "grupo_etario": {str(k): int(v) for k, v in grupo_etario_dist.items()},
            "armas_medios_top": {str(k): int(v) for k, v in list(armas_dist.items())[:10]}
        }
    }
    return evidence


def profile_api_source(df_api: pd.DataFrame) -> Dict[str, Any]:
    """Profiles the raw Comisarías de Familia API dataset from datos.gov.co."""
    logger.info("Profiling API Source (%d rows)...", len(df_api))

    total_rows = len(df_api)
    null_counts = {col: int(df_api[col].isna().sum()) for col in df_api.columns}
    null_percentages = {col: round(cnt / total_rows * 100, 3) for col, cnt in null_counts.items()}

    # Municipal key profiling
    dane_raw = df_api["c_digo_dane_municipio"].astype(str).str.strip()
    raw_lengths = dane_raw.str.len().value_counts().to_dict()
    distinct_raw_muni = int(dane_raw.nunique())

    # Padding to 5 digits for candidate key evaluation
    dane_5 = dane_raw.str.zfill(5)
    distinct_dane_5 = int(dane_5.nunique())

    # Municipal categories (Ley 617 de 2000)
    cat_dist = df_api["categoria_municipio"].value_counts(dropna=False).to_dict()

    # Comisarias Ley 2126 / 100.000 (Required comisarías)
    req_numeric = pd.to_numeric(df_api["comisarias_ley_2126_100_000"], errors="coerce")
    req_nulls = int(req_numeric.isna().sum())
    req_dist = df_api["comisarias_ley_2126_100_000"].value_counts(dropna=False).to_dict()

    # Existencia comisarías (Installed comisarías)
    inst_numeric = pd.to_numeric(df_api["existencia_de_comisarias"], errors="coerce")
    inst_nulls = int(inst_numeric.isna().sum())
    inst_dist = df_api["existencia_de_comisarias"].value_counts(dropna=False).to_dict()

    evidence = {
        "dataset_name": "Caracterización de las comisarías de familia en el territorio nacional (API)",
        "total_records": total_rows,
        "null_counts": null_counts,
        "null_percentages": null_percentages,
        "dane_key_profiling": {
            "distinct_raw_codes": distinct_raw_muni,
            "distinct_padded_5_digit_codes": distinct_dane_5,
            "raw_length_distribution": {str(k): int(v) for k, v in raw_lengths.items()},
            "rows_requiring_zero_padding": int((dane_raw.str.len() == 4).sum())
        },
        "categoria_municipio_distribution": {str(k): int(v) for k, v in cat_dist.items()},
        "comisarias_ley_2126_requeridas": {
            "null_or_invalid_count": req_nulls,
            "distribution": {str(k): int(v) for k, v in req_dist.items()}
        },
        "existencia_comisarias_instaladas": {
            "null_or_invalid_count": inst_nulls,
            "distribution": {str(k): int(v) for k, v in inst_dist.items()}
        }
    }
    return evidence


def profile_cross_source_integration(df_primary: pd.DataFrame, df_api: pd.DataFrame) -> Dict[str, Any]:
    """Profiles the integration key and match coverage between both sources."""
    logger.info("Profiling Cross-Source Integration...")

    primary_muni = set(df_primary["CODIGO DANE"].astype(str).str[:5])
    api_muni = set(df_api["c_digo_dane_municipio"].astype(str).str.strip().str.zfill(5))

    matched = primary_muni.intersection(api_muni)
    primary_only = primary_muni - api_muni
    api_only = api_muni - primary_muni

    coverage_pct = round(len(matched) / len(primary_muni) * 100, 2)

    evidence = {
        "integration_key": "codigo_dane_municipio (5-digit DANE code)",
        "primary_distinct_municipalities": len(primary_muni),
        "api_distinct_municipalities": len(api_muni),
        "matched_municipalities_count": len(matched),
        "primary_coverage_percentage": coverage_pct,
        "unmatched_primary_count": len(primary_only),
        "unmatched_primary_samples": sorted(list(primary_only)),
        "unmatched_api_count": len(api_only),
        "unmatched_api_samples": sorted(list(api_only)),
        "integration_risk_assessment": (
            "Primary codes not in API correspond to non-municipalized areas (corregimientos departamentales "
            "in Amazonas, Vaupés, Guainía) and 6 malformed source rows (00000, 52000). Handled via left join "
            "with explicit default institution metrics without dropping any primary victim."
        )
    }
    return evidence


def run_full_profiling(df_primary: pd.DataFrame, df_api: pd.DataFrame) -> Dict[str, Any]:
    """Executes profiling on both sources and cross-source matching, exporting evidence."""
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

    report = {
        "profiling_metadata": {
            "execution_date": pd.Timestamp.now().isoformat(),
            "status": "COMPLETED"
        },
        "primary_source": profile_primary_source(df_primary),
        "api_source": profile_api_source(df_api),
        "cross_source_integration": profile_cross_source_integration(df_primary, df_api)
    }

    evidence_json_path = os.path.join(EVIDENCE_DIR, "profiling_evidence.json")
    with open(evidence_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info("Profiling report saved to %s", evidence_json_path)
    return report


if __name__ == "__main__":
    from extract_primary import extract_primary_data
    from extract_api import extract_api_data

    df_p, _ = extract_primary_data()
    df_a, _ = extract_api_data()
    report = run_full_profiling(df_p, df_a)

    print("\n=== PROFILING SUMMARY ===")
    print("Primary rows:", report["primary_source"]["total_records"])
    print("API rows:", report["api_source"]["total_records"])
    print("Match rate:", report["cross_source_integration"]["primary_coverage_percentage"], "%")
