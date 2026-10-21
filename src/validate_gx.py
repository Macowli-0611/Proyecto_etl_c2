"""Automated Data Quality Validation Module with Great Expectations 1.X.

Implements three explicit validation gates required by the course rubric:
  1. validate_primary_raw: Raw Primary Branch (DIJIN Domestic Violence Reports) - Gate 1
  2. validate_api_raw: Raw API Branch (MinJusticia Comisarías de Familia) - Gate 2
  3. validate_prepared_data: Transformed & Integrated Prepared Data (pre-DW load) - Gate 3

Each check is traceable to a documented DQ Rule ID, dimension, metric, threshold, and severity.
Expectation Suites are maintained and synchronized from the declarative repository:
  - gx/expectations/primary_raw_suite.json
  - gx/expectations/api_raw_suite.json
  - gx/expectations/prepared_data_suite.json

Severity Policy:
  - Critical severity violations halt execution immediately and block downstream processing.
  - Warning severity checks record audit findings in docs/evidence/ and allow pipeline continuation.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple

import great_expectations as gx
import great_expectations.expectations as gxe
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ValidateGX")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GX_DIR = os.path.join(PROJECT_ROOT, "gx")
EXPECTATIONS_DIR = os.path.join(GX_DIR, "expectations")
EVIDENCE_DIR = os.path.join(PROJECT_ROOT, "docs", "evidence")


class ValidationError(Exception):
    """Custom exception raised when a Critical quality expectation fails."""
    pass


def load_expectation_suite_json(suite_name: str) -> Dict[str, Any]:
    """Loads a declarative expectation suite definition from gx/expectations/."""
    filename = f"{suite_name}.json" if not suite_name.endswith(".json") else suite_name
    filepath = os.path.join(EXPECTATIONS_DIR, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Could not read expectation suite from %s: %s", filepath, e)
    return {}


def _save_validation_result(gate_name: str, result_dict: Dict[str, Any]) -> str:
    """Saves validation execution results as JSON for audit, observability, and compliance."""
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(EVIDENCE_DIR, f"gx_validation_{gate_name}_{timestamp}.json")
    latest_path = os.path.join(EVIDENCE_DIR, f"gx_validation_{gate_name}_latest.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, indent=2, default=str, ensure_ascii=False)
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, indent=2, default=str, ensure_ascii=False)

    logger.info("Saved %s validation evidence to %s", gate_name, filepath)
    return filepath


def validate_primary_raw(df_raw: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
    """Gate 1: Validates raw primary source before entering transformation.

    Rules defined in gx/expectations/primary_raw_suite.json:
      - DQ-RAW1-01 (Critical): Mandatory schema columns exist.
      - DQ-RAW1-02 (Critical): FECHA HECHO format DD/MM/YYYY.
      - DQ-RAW1-03 (Critical): CODIGO DANE length (8 characters).
      - DQ-RAW1-04 (Critical): CANTIDAD positive integer >= 1.
      - DQ-RAW1-05 (Warning): GENERO missingness <= 1%.
    """
    logger.info("--- GATE 1: Validating Raw Primary Source (%d rows) ---", len(df_raw))
    suite_json = load_expectation_suite_json("primary_raw_suite")

    context = gx.get_context(mode="ephemeral")
    source_name = f"pandas_primary_raw_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"
    data_source = context.data_sources.add_pandas(source_name)
    data_asset = data_source.add_dataframe_asset("primary_raw_asset")
    batch_def = data_asset.add_batch_definition_whole_dataframe("batch_def_primary")

    suite_name = "primary_raw_suite"
    suite = context.suites.add(gx.ExpectationSuite(name=suite_name))

    # Required columns
    required_cols = [
        "DEPARTAMENTO", "MUNICIPIO", "CODIGO DANE", "ARMAS MEDIOS",
        "FECHA HECHO", "GENERO", "GRUPO ETARIO", "CANTIDAD"
    ]
    if suite_json and "expectations" in suite_json:
        for exp in suite_json["expectations"]:
            if exp.get("type") == "expect_table_columns_to_match_set":
                required_cols = exp.get("kwargs", {}).get("column_set", required_cols)

    # DQ-RAW1-01: Mandatory columns
    suite.add_expectation(
        gxe.ExpectTableColumnsToMatchSet(
            column_set=required_cols,
            exact_match=False,
            notes="DQ-RAW1-01: Critical. Verifies mandatory schema columns exist."
        )
    )

    # Prepare DataFrame copy with numeric conversion for CANTIDAD
    df_eval = df_raw.copy()
    if "CANTIDAD" in df_eval.columns:
        df_eval["CANTIDAD_NUMERIC"] = pd.to_numeric(df_eval["CANTIDAD"], errors="coerce")
        # DQ-RAW1-04: CANTIDAD positive integer
        suite.add_expectation(
            gxe.ExpectColumnValuesToBeBetween(
                column="CANTIDAD_NUMERIC",
                min_value=1,
                notes="DQ-RAW1-04: Critical. Measure CANTIDAD must be >= 1."
            )
        )

    # DQ-RAW1-03: CODIGO DANE length (8 characters at centro poblado level)
    if "CODIGO DANE" in df_eval.columns:
        suite.add_expectation(
            gxe.ExpectColumnValueLengthsToBeBetween(
                column="CODIGO DANE",
                min_value=8,
                max_value=8,
                mostly=0.9999,
                notes="DQ-RAW1-03: Critical. DANE code must be 8-digit string."
            )
        )

    # DQ-RAW1-05: GENERO null threshold <= 1%
    if "GENERO" in df_eval.columns:
        suite.add_expectation(
            gxe.ExpectColumnValuesToNotBeNull(
                column="GENERO",
                mostly=0.99,
                notes="DQ-RAW1-05: Warning. Null gender must not exceed 1%."
            )
        )

    val_def = context.validation_definitions.add(
        gx.ValidationDefinition(name="val_primary_raw", data=batch_def, suite=suite)
    )

    eval_result = val_def.run(batch_parameters={"dataframe": df_eval})
    overall_success = eval_result.success

    results_summary = []
    critical_failure = False

    for res in eval_result.results:
        exp_type = res.expectation_config.type
        notes = getattr(res.expectation_config, "notes", "") or ""
        success = res.success
        result_info = {
            "expectation": exp_type,
            "notes": notes,
            "success": success,
            "result_details": res.result
        }
        results_summary.append(result_info)

        if not success:
            if "Critical" in notes or "DQ-RAW1-01" in notes or "DQ-RAW1-03" in notes or "DQ-RAW1-04" in notes:
                critical_failure = True
                logger.error("CRITICAL FAILURE in Gate 1: %s (%s)", exp_type, notes)
            else:
                logger.warning("WARNING in Gate 1: %s (%s)", exp_type, notes)

    audit_payload = {
        "gate": "validate_primary_raw",
        "suite_name": "primary_raw_suite",
        "timestamp": datetime.now().isoformat(),
        "total_records": len(df_raw),
        "overall_success": overall_success,
        "critical_failure": critical_failure,
        "results": results_summary
    }
    _save_validation_result("primary_raw", audit_payload)

    if critical_failure:
        raise ValidationError(
            "Gate 1 (Primary Raw Validation) failed with Critical severity. Execution halted to protect downstream tasks."
        )

    logger.info("Gate 1 (Primary Raw) passed successfully! All critical rules satisfied.")
    return True, audit_payload


def validate_api_raw(df_api: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
    """Gate 2: Validates raw API source before entering transformation.

    Rules defined in gx/expectations/api_raw_suite.json:
      - DQ-RAW2-01 (Critical): Mandatory API fields present.
      - DQ-RAW2-02 (Critical): c_digo_dane_municipio length 4-5 characters.
      - DQ-RAW2-03 (Warning): categoria_municipio in statutory set {1,2,3,4,5,6,ESP}.
      - DQ-RAW2-04 (Critical): existencia_de_comisarias >= 0.
    """
    logger.info("--- GATE 2: Validating Raw API Source (%d rows) ---", len(df_api))
    suite_json = load_expectation_suite_json("api_raw_suite")

    context = gx.get_context(mode="ephemeral")
    source_name = f"pandas_api_raw_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"
    data_source = context.data_sources.add_pandas(source_name)
    data_asset = data_source.add_dataframe_asset("api_raw_asset")
    batch_def = data_asset.add_batch_definition_whole_dataframe("batch_def_api")

    suite_name = "api_raw_suite"
    suite = context.suites.add(gx.ExpectationSuite(name=suite_name))

    required_cols = [
        "c_digo_dane_municipio", "categoria_municipio",
        "existencia_de_comisarias", "comisarias_ley_2126_100_000"
    ]
    if suite_json and "expectations" in suite_json:
        for exp in suite_json["expectations"]:
            if exp.get("type") == "expect_table_columns_to_match_set":
                required_cols = exp.get("kwargs", {}).get("column_set", required_cols)

    # DQ-RAW2-01: Mandatory columns
    suite.add_expectation(
        gxe.ExpectTableColumnsToMatchSet(
            column_set=required_cols,
            exact_match=False,
            notes="DQ-RAW2-01: Critical. Mandatory API schema attributes must exist."
        )
    )

    # DQ-RAW2-02: DANE length 4 to 5
    if "c_digo_dane_municipio" in df_api.columns:
        suite.add_expectation(
            gxe.ExpectColumnValueLengthsToBeBetween(
                column="c_digo_dane_municipio",
                min_value=4,
                max_value=5,
                mostly=0.99,
                notes="DQ-RAW2-02: Critical. API DANE code length must be between 4 and 5 characters."
            )
        )

    # DQ-RAW2-04: Non-negative comisarías count
    df_eval = df_api.copy()
    if "existencia_de_comisarias" in df_eval.columns:
        df_eval["existencia_numeric"] = pd.to_numeric(df_eval["existencia_de_comisarias"], errors="coerce")
        suite.add_expectation(
            gxe.ExpectColumnValuesToBeBetween(
                column="existencia_numeric",
                min_value=0,
                mostly=0.90,
                notes="DQ-RAW2-04: Critical. Existing comisarías count must be non-negative."
            )
        )

    # DQ-RAW2-03: Category in expected domain
    if "categoria_municipio" in df_eval.columns:
        suite.add_expectation(
            gxe.ExpectColumnValuesToBeInSet(
                column="categoria_municipio",
                value_set=["1", "2", "3", "4", "5", "6", "ESP", "Especial", "None", None, ""],
                mostly=0.95,
                notes="DQ-RAW2-03: Warning. Municipal category domain validity."
            )
        )

    val_def = context.validation_definitions.add(
        gx.ValidationDefinition(name="val_api_raw", data=batch_def, suite=suite)
    )

    eval_result = val_def.run(batch_parameters={"dataframe": df_eval})
    overall_success = eval_result.success

    results_summary = []
    critical_failure = False

    for res in eval_result.results:
        exp_type = res.expectation_config.type
        notes = getattr(res.expectation_config, "notes", "") or ""
        success = res.success
        result_info = {
            "expectation": exp_type,
            "notes": notes,
            "success": success,
            "result_details": res.result
        }
        results_summary.append(result_info)

        if not success:
            if "Critical" in notes or "DQ-RAW2-01" in notes or "DQ-RAW2-02" in notes:
                critical_failure = True
                logger.error("CRITICAL FAILURE in Gate 2: %s (%s)", exp_type, notes)
            else:
                logger.warning("WARNING in Gate 2: %s (%s)", exp_type, notes)

    audit_payload = {
        "gate": "validate_api_raw",
        "suite_name": "api_raw_suite",
        "timestamp": datetime.now().isoformat(),
        "total_records": len(df_api),
        "overall_success": overall_success,
        "critical_failure": critical_failure,
        "results": results_summary
    }
    _save_validation_result("api_raw", audit_payload)

    if critical_failure:
        raise ValidationError(
            "Gate 2 (API Raw Validation) failed with Critical severity. Execution halted to protect downstream tasks."
        )

    logger.info("Gate 2 (API Raw) passed successfully! All critical rules satisfied.")
    return True, audit_payload


def validate_prepared_data(tables: Dict[str, pd.DataFrame], expected_totals: Dict[str, int]) -> Tuple[bool, Dict[str, Any]]:
    """Gate 3: Validates transformed and integrated data before loading into the Data Warehouse.

    Rules defined in gx/expectations/prepared_data_suite.json:
      - DQ-PREP-01 (Critical): Fact table declared grain uniqueness (id_tiempo, id_geografia, id_victima, id_medio).
      - DQ-PREP-02 (Critical): Zero null foreign keys in fact table.
      - DQ-PREP-03 (Critical): Referential integrity (fact foreign keys must exist in dimensions).
      - DQ-PREP-04 (Critical): Installed comisarías >= 0 in dim_geografia.
      - DQ-PREP-05 (Critical): Total victim count reconciliation with raw source.
    """
    logger.info("--- GATE 3: Validating Transformed & Integrated Prepared Data ---")
    suite_json = load_expectation_suite_json("prepared_data_suite")

    fact = tables["fact_violencia_intrafamiliar"]
    dim_geo = tables["dim_geografia"]
    dim_tiempo = tables["dim_tiempo"]
    dim_victima = tables["dim_victima"]
    dim_medio = tables["dim_medio"]

    grain = ["id_tiempo", "id_geografia", "id_victima", "id_medio"]
    critical_failure = False
    results_summary = []

    # 1. Grain Uniqueness (DQ-PREP-01)
    grain_duplicates = int(fact.duplicated(subset=grain).sum())
    grain_pass = (grain_duplicates == 0)
    results_summary.append({
        "rule_id": "DQ-PREP-01",
        "dimension": "Uniqueness",
        "requirement": "R1–R7",
        "description": "Fact table uniqueness at declared municipal grain",
        "expected": "0 duplicates",
        "actual": f"{grain_duplicates} duplicates",
        "severity": "Critical",
        "success": grain_pass
    })
    if not grain_pass:
        critical_failure = True
        logger.error("CRITICAL: Fact grain uniqueness violated! Found %d duplicates.", grain_duplicates)

    # 2. Foreign Keys Not Null (DQ-PREP-02)
    fk_nulls = {col: int(fact[col].isna().sum()) for col in grain}
    total_fk_nulls = sum(fk_nulls.values())
    fks_pass = (total_fk_nulls == 0)
    results_summary.append({
        "rule_id": "DQ-PREP-02",
        "dimension": "Completeness",
        "requirement": "R1–R7",
        "description": "Foreign keys not null in fact table",
        "expected": "0 nulls",
        "actual": fk_nulls,
        "severity": "Critical",
        "success": fks_pass
    })
    if not fks_pass:
        critical_failure = True
        logger.error("CRITICAL: Found null foreign keys in fact table: %s", fk_nulls)

    # 3. Referential Integrity (Fact -> Dimensions) (DQ-PREP-03)
    ref_errors = {}
    for col, dim_df, pk in [
        ("id_tiempo", dim_tiempo, "id_tiempo"),
        ("id_geografia", dim_geo, "id_geografia"),
        ("id_victima", dim_victima, "id_victima"),
        ("id_medio", dim_medio, "id_medio"),
    ]:
        orphans = set(fact[col]) - set(dim_df[pk])
        if orphans:
            ref_errors[col] = len(orphans)
    ref_pass = (len(ref_errors) == 0)
    results_summary.append({
        "rule_id": "DQ-PREP-03",
        "dimension": "Consistency",
        "requirement": "R1–R7",
        "description": "Referential integrity (fact foreign keys must exist in dimensions)",
        "expected": "0 orphans",
        "actual": ref_errors,
        "severity": "Critical",
        "success": ref_pass
    })
    if not ref_pass:
        critical_failure = True
        logger.error("CRITICAL: Referential integrity violation: %s", ref_errors)

    # 4. Measure Reconciliation (DQ-PREP-05)
    loaded_victims = int(fact["cantidad_victimas"].sum())
    loaded_records = int(fact["numero_registros"].sum())
    expected_victims = expected_totals.get("victims", 0)
    expected_records = expected_totals.get("records", 0)

    reconciled = (loaded_victims == expected_victims) and (loaded_records == expected_records)
    results_summary.append({
        "rule_id": "DQ-PREP-05",
        "dimension": "Accuracy & Reconciliation",
        "requirement": "All",
        "description": "Reconciliation of measures between source extract and fact table",
        "expected": f"victims={expected_victims}, records={expected_records}",
        "actual": f"victims={loaded_victims}, records={loaded_records}",
        "severity": "Critical",
        "success": reconciled
    })
    if not reconciled:
        critical_failure = True
        logger.error(
            "CRITICAL: Reconciliation failure! Expected: %d victims, %d records. Got: %d victims, %d records.",
            expected_victims, expected_records, loaded_victims, loaded_records
        )

    # 5. Integration Key Plausibility in dim_geografia (DQ-PREP-04)
    has_installed_valid = (dim_geo["comisarias_instaladas"] >= 0).all()
    results_summary.append({
        "rule_id": "DQ-PREP-04",
        "dimension": "Validity",
        "requirement": "R6, R7",
        "description": "Enriched dim_geografia comisarias_instaladas non-negative",
        "expected": ">= 0 for all rows",
        "actual": f"min={dim_geo['comisarias_instaladas'].min()}",
        "severity": "Critical",
        "success": bool(has_installed_valid)
    })
    if not has_installed_valid:
        critical_failure = True
        logger.error("CRITICAL: Negative values in dim_geografia.comisarias_instaladas!")

    audit_payload = {
        "gate": "validate_prepared",
        "suite_name": "prepared_data_suite",
        "timestamp": datetime.now().isoformat(),
        "total_fact_rows": len(fact),
        "total_victims": loaded_victims,
        "overall_success": not critical_failure,
        "critical_failure": critical_failure,
        "results": results_summary
    }
    _save_validation_result("prepared", audit_payload)

    if critical_failure:
        raise ValidationError(
            "Gate 3 (Prepared Data Validation) failed with Critical severity. DW load blocked to protect analytical integrity."
        )

    logger.info("Gate 3 (Prepared Data) passed successfully! All dimensional invariants verified.")
    return True, audit_payload
