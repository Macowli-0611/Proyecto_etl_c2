"""Apache Airflow DAG: Pipeline Automation, API Integration & Data Validation.

Orchestrates the domestic violence ETL pipeline following Airflow 3.X TaskFlow API:
  - Branch 1: extract_primary -> validate_primary_raw
  - Branch 2: extract_api -> validate_api_raw
  - Convergence: transform_and_integrate -> validate_prepared -> load_dimensional_dw

Task Interfaces:Compact references (file paths & metadata manifests) exchanged via XCom.
Bulk datasets are NEVER moved through XCom; they are persisted in data/raw and data/processed.

Selective Retry Policies:
  - Network / API extraction tasks: retries=3, retry_delay=10s (transient network faults).
  - Validation gates: retries=0 (deterministic data quality violations fail fast).
  - DW load: retries=1, retry_delay=5s (transient database connections).
"""

from datetime import datetime, timedelta
import json
import os
import sys

# Add project root to sys.path so modules in src can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Airflow 3.X TaskFlow authoring interface
try:
    from airflow.sdk import dag, task
except ImportError:
    from airflow.decorators import dag, task

from src.extract_primary import extract_primary_data
from src.extract_api import extract_api_data
from src.validate_gx import validate_primary_raw, validate_api_raw, validate_prepared_data, ValidationError
from src.transform_and_integrate import transform_and_integrate_all
from src.dimensional_model import build_star_schema
from src.load_dw import load_dimensional_warehouse


default_args = {
    "owner": "DataEngineeringTeam_G01",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "execution_timeout": timedelta(minutes=15)
}


@dag(
    dag_id="etl_violencia_intrafamiliar_segunda_entrega",
    default_args=default_args,
    description="Automated ETL Pipeline: Domestic Violence + MinJusticia Comisarías de Familia API",
    schedule=None,  # Triggered on-demand or external event
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["etl", "dijin", "comisarias", "great-expectations", "postgres-dw", "sdg-5", "sdg-16"]
)
def domestic_violence_pipeline():

    # -------------------------------------------------------------------------
    # Branch 1: Primary Source (Policía Nacional - DIJIN)
    # -------------------------------------------------------------------------
    @task(
        task_id="extract_primary",
        retries=2,
        retry_delay=timedelta(seconds=10),
        doc_md="Acquires raw primary dataset, verifies SHA-256 and records manifest."
    )
    def task_extract_primary() -> dict:
        """Extracts primary source and returns compact metadata manifest."""
        _, manifest = extract_primary_data()
        return {
            "source": "primary",
            "local_filepath": manifest["local_filepath"],
            "row_count": manifest["row_count"],
            "sha256": manifest["sha256"],
            "victims_raw": manifest["total_victims_raw"]
        }

    @task(
        task_id="validate_primary_raw",
        retries=0,  # Deterministic quality gate: Fail immediately if Critical rule is violated
        doc_md="Gate 1: Great Expectations automated validation of raw primary batch."
    )
    def task_validate_primary_raw(primary_meta: dict) -> dict:
        """Evaluates raw primary data against Suite Primary Raw."""
        from src.extract_primary import extract_primary_data
        df_raw, _ = extract_primary_data(filepath=primary_meta["local_filepath"])
        passed, audit = validate_primary_raw(df_raw)
        return {
            "gate": "validate_primary_raw",
            "passed": passed,
            "critical_failure": audit["critical_failure"],
            "total_records": audit["total_records"]
        }

    # -------------------------------------------------------------------------
    # Branch 2: API Source (Comisarías de Familia - MinJusticia)
    # -------------------------------------------------------------------------
    @task(
        task_id="extract_api",
        retries=3,  # Transient network/SODA API retries with backoff
        retry_delay=timedelta(seconds=10),
        doc_md="Programmatically extracts Comisarías de Familia via SODA REST API with pagination."
    )
    def task_extract_api() -> dict:
        """Extracts API source and returns compact metadata manifest."""
        _, manifest = extract_api_data()
        return {
            "source": "api",
            "local_filepath": manifest["local_filepath"],
            "row_count": manifest["row_count"],
            "sha256": manifest["sha256"],
            "distinct_municipalities": manifest["distinct_municipalities_raw"]
        }

    @task(
        task_id="validate_api_raw",
        retries=0,  # Deterministic quality gate: Fail immediately if Critical rule is violated
        doc_md="Gate 2: Great Expectations automated validation of raw API batch."
    )
    def task_validate_api_raw(api_meta: dict) -> dict:
        """Evaluates raw API data against Suite API Raw."""
        from src.extract_api import extract_api_data
        df_api, _ = extract_api_data(force_refresh=False)
        passed, audit = validate_api_raw(df_api)
        return {
            "gate": "validate_api_raw",
            "passed": passed,
            "critical_failure": audit["critical_failure"],
            "total_records": audit["total_records"]
        }

    # -------------------------------------------------------------------------
    # Convergence: Transformation, Harmonisation & Integration
    # -------------------------------------------------------------------------
    @task(
        task_id="transform_and_clean_and_integrate",
        retries=0,
        doc_md="Executes integration contract, cleans demographics, rolls up geography and builds star schema."
    )
    def task_transform_and_integrate(primary_val_meta: dict, api_val_meta: dict) -> dict:
        """Transforms and integrates both validated branches."""
        if not primary_val_meta.get("passed") or not api_val_meta.get("passed"):
            raise ValidationError("Cannot proceed with transformation: One or both raw validation gates failed.")

        from src.extract_primary import extract_primary_data
        from src.extract_api import extract_api_data

        df_p, manifest_p = extract_primary_data()
        df_a, manifest_a = extract_api_data()

        trans_res = transform_and_integrate_all(df_p, df_a)
        tables = build_star_schema(
            trans_res["df_primary_clean"],
            trans_res["df_geo_integrated"],
            trans_res["df_comisarias_dir"]
        )

        # Persist prepared datasets in data/processed (Parquet/CSV) for decoupled loading & audit
        proc_dir = os.path.join(PROJECT_ROOT, "data", "processed")
        os.makedirs(proc_dir, exist_ok=True)
        persisted_paths = {}
        for name, df in tables.items():
            path = os.path.join(proc_dir, f"{name}.parquet")
            df.to_parquet(path, index=False)
            persisted_paths[name] = path

        return {
            "persisted_paths": persisted_paths,
            "expected_victims": manifest_p["total_victims_raw"],
            "expected_records": manifest_p["row_count"],
            "total_fact_rows": len(tables["fact_violencia_intrafamiliar"]),
            "total_municipalities": len(tables["dim_geografia"])
        }

    # -------------------------------------------------------------------------
    # Gate 3: Prepared Data Quality Validation
    # -------------------------------------------------------------------------
    @task(
        task_id="validate_prepared",
        retries=0,  # Deterministic quality gate: Halt before touching DW if invariants fail
        doc_md="Gate 3: Great Expectations validation of grain uniqueness, referential integrity and reconciliation."
    )
    def task_validate_prepared(prepared_meta: dict) -> dict:
        """Validates prepared datasets prior to database loading."""
        import pandas as pd
        tables = {
            name: pd.read_parquet(path)
            for name, path in prepared_meta["persisted_paths"].items()
        }
        expected_totals = {
            "victims": prepared_meta["expected_victims"],
            "records": prepared_meta["expected_records"]
        }
        passed, audit = validate_prepared_data(tables, expected_totals)
        return {
            "gate": "validate_prepared",
            "passed": passed,
            "critical_failure": audit["critical_failure"],
            "prepared_meta": prepared_meta
        }

    # -------------------------------------------------------------------------
    # Dimensional Data Warehouse Load
    # -------------------------------------------------------------------------
    @task(
        task_id="load_dimensional_dw",
        retries=1,
        retry_delay=timedelta(seconds=5),
        doc_md="Executes DDL and bulk COPY into PostgreSQL DW with post-load automated reconciliation."
    )
    def task_load_dw(prep_val_meta: dict) -> dict:
        """Loads accepted data into PostgreSQL and runs final verification queries."""
        if not prep_val_meta.get("passed"):
            raise ValidationError("Prepared data validation failed! Aborting DW load to protect data warehouse.")

        import pandas as pd
        prep_meta = prep_val_meta["prepared_meta"]
        tables = {
            name: pd.read_parquet(path)
            for name, path in prep_meta["persisted_paths"].items()
        }
        expected_totals = {
            "victims": prep_meta["expected_victims"],
            "records": prep_meta["expected_records"]
        }

        reconciliation_report = load_dimensional_warehouse(tables, expected_totals)
        return reconciliation_report

    # Define DAG Task Dependencies
    primary_meta = task_extract_primary()
    primary_val = task_validate_primary_raw(primary_meta)

    api_meta = task_extract_api()
    api_val = task_validate_api_raw(api_meta)

    # Both raw branches must validate before transformation begins
    prepared_meta = task_transform_and_integrate(primary_val, api_val)

    # Prepared validation gate must pass before DW load
    prep_val = task_validate_prepared(prepared_meta)

    # Load into PostgreSQL
    dw_report = task_load_dw(prep_val)


# Instantiate the DAG
dag_instance = domestic_violence_pipeline()
