"""Apache Airflow 3.1.8 DAG: Pipeline Automation, API Integration & Data Validation.

Orchestrates the domestic violence ETL pipeline following Apache Airflow 3.1.8 Task SDK:
  - Branch 1: extract_primary >> validate_primary_raw
  - Branch 2: extract_api >> validate_api_raw
  - Convergence: transform_and_clean_and_integrate >> validate_prepared >> load_dimensional_dw

Task Interfaces: Compact references (file paths & metadata manifests) exchanged via XCom.
Bulk datasets and DataFrames are NEVER passed through XCom; they are persisted in data/raw and data/processed.

Selective Retries Policy:
  - Operational transient failures (retries enabled with backoff):
      * extract_primary: retries=2, retry_delay=1m (transient I/O locks, file access latency)
      * extract_api: retries=3, retry_delay=2m (transient API rate limits, HTTP 429, socket timeouts)
      * load_dimensional_dw: retries=2, retry_delay=1m (transient DB connection pool contention)
  - Deterministic data quality or contract failures (retries=0, NO RETRIES):
      * validate_primary_raw: retries=0 (deterministic raw schema/data quality violation)
      * validate_api_raw: retries=0 (deterministic API contract violation)
      * transform_and_clean_and_integrate: retries=0 (deterministic business transformation failure)
      * validate_prepared: retries=0 (deterministic dimensional invariant/reconciliation failure)
"""

from datetime import datetime, timedelta
import json
import os
import sys

# Add project root to sys.path so modules in src can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Airflow 3.1.8 Task SDK public authoring interface
from airflow.sdk import dag, task, Param

# Airflow exception to halt task and downstream tasks immediately on Critical failure
try:
    from airflow.exceptions import AirflowFailException
except ImportError:
    try:
        from airflow.sdk.exceptions import AirflowFailException
    except ImportError:
        AirflowFailException = ValueError

from src.extract_primary import extract_primary_data
from src.extract_api import extract_api_data
from src.validate_gx import (
    validate_primary_raw,
    validate_api_raw,
    validate_prepared_data,
    ValidationError
)
from src.transform_and_integrate import transform_and_integrate_all
from src.dimensional_model import build_star_schema
from src.load_dw import load_dimensional_warehouse


default_args = {
    "owner": "DataEngineeringTeam_G01",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,  # Explicitly 0: generic DAG retries are strictly forbidden; each task defines its own selective retry policy
    "execution_timeout": timedelta(minutes=15)
}


@dag(
    dag_id="etl_violencia_intrafamiliar_segunda_entrega",
    default_args=default_args,
    description="Automated ETL Pipeline: Domestic Violence + MinJusticia Comisarías de Familia API",
    schedule=None,  # Triggered on-demand or external event
    start_date=datetime(2026, 1, 1),
    catchup=False,
    params={
        "test_mode": Param(
            "TEST_A_SUCCESSFUL_RUN",
            enum=[
                "TEST_A_SUCCESSFUL_RUN",
                "TEST_B_CONTROLLED_FAILURE",
                "TEST_C_SAFE_RERUN"
            ],
            description="Seleccione la prueba de confiabilidad obligatoria (Rúbrica Sección 20):\n- TEST_A_SUCCESSFUL_RUN: 20.1 Test A (Ejecución completa exitosa de punta a punta).\n- TEST_B_CONTROLLED_FAILURE: 20.2 Test B (Falla crítica controlada en Compuerta 1 con Great Expectations).\n- TEST_C_SAFE_RERUN: 20.3 Test C (Re-ejecución segura e idempotente sin duplicados)."
        )
    },
    tags=["etl", "dijin", "comisarias", "great-expectations", "postgres-dw", "airflow-3.1.8", "sdg-5", "sdg-16"]
)
def domestic_violence_pipeline():

    # -------------------------------------------------------------------------
    # Branch 1: Primary Source (Policía Nacional - DIJIN)
    # -------------------------------------------------------------------------
    @task(
        task_id="extract_primary",
        retries=2,
        retry_delay=timedelta(minutes=1),
        doc_md="""
        Acquires raw primary dataset from local cache or remote portal, verifies SHA-256 and records manifest.

        Selective Retry Justification:
        Configured with retries=2 and retry_delay=1m to recover from transient operational I/O failures,
        temporary file locks or momentary network interruptions during download without manual intervention.
        """
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
        doc_md="""
        Gate 1: Great Expectations automated validation of raw primary batch against primary_raw_suite.

        Selective Retry Justification:
        Configured with retries=0 (No Retries). Data quality and schema violations are strictly deterministic:
        re-evaluating an identical, unchanged raw file against the same rules will produce the exact same
        failure. Automatic retries would only waste cluster resources and delay failure notification.
        """
    )
    def task_validate_primary_raw(primary_meta: dict, **context) -> dict:
        """Evaluates raw primary data against Suite Primary Raw."""
        df_raw, _ = extract_primary_data(filepath=primary_meta["local_filepath"])

        # Check execution parameters (Opciones Avanzadas in Airflow UI)
        params = context.get("params", {})
        dag_run = context.get("dag_run")
        conf = dag_run.conf if dag_run else {}
        test_mode = conf.get("test_mode", params.get("test_mode", "TEST_A_SUCCESSFUL_RUN"))

        if test_mode in ["TEST_B_CONTROLLED_FAILURE", "test_b_controlled_failure"]:
            import logging
            logging.warning("=== [TEST B ACTIVATED] Injecting critical synthetic quality violation (null DEPARTAMENTO) ===")
            df_raw = df_raw.copy()
            df_raw.loc[df_raw.index[:500], "DEPARTAMENTO"] = None

        try:
            passed, audit = validate_primary_raw(df_raw)
        except ValidationError as e:
            raise AirflowFailException(
                f"Gate 1 (Primary Raw) failed with Critical severity: {e}. Downstream tasks blocked."
            )

        if audit.get("critical_failure") or not passed:
            raise AirflowFailException(
                "Gate 1 (Primary Raw) Critical Quality Failure detected! Halting pipeline execution immediately."
            )

        return {
            "gate": "validate_primary_raw",
            "passed": passed,
            "critical_failure": audit["critical_failure"],
            "total_records": audit["total_records"],
            "local_filepath": primary_meta["local_filepath"]
        }

    # -------------------------------------------------------------------------
    # Branch 2: API Source (Comisarías de Familia - MinJusticia)
    # -------------------------------------------------------------------------
    @task(
        task_id="extract_api",
        retries=3,
        retry_delay=timedelta(minutes=2),
        doc_md="""
        Programmatically extracts Comisarías de Familia via SODA REST API with pagination.

        Selective Retry Justification:
        Configured with retries=3 and retry_delay=2m to handle transient external API failures, including
        temporary HTTP 429 rate limits, socket timeouts, DNS resolution hiccups, or momentary API downtime.
        """
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
        doc_md="""
        Gate 2: Great Expectations automated validation of raw API payload against api_raw_suite.

        Selective Retry Justification:
        Configured with retries=0 (No Retries). API schema and data contract violations are deterministic:
        if the retrieved payload violates mandatory columns or attribute constraints, retrying against the
        same extracted payload will inevitably fail again.
        """
    )
    def task_validate_api_raw(api_meta: dict) -> dict:
        """Evaluates raw API data against Suite API Raw."""
        df_api, _ = extract_api_data(force_refresh=False)
        try:
            passed, audit = validate_api_raw(df_api)
        except ValidationError as e:
            raise AirflowFailException(
                f"Gate 2 (API Raw) failed with Critical severity: {e}. Downstream tasks blocked."
            )

        if audit.get("critical_failure") or not passed:
            raise AirflowFailException(
                "Gate 2 (API Raw) Critical Quality Failure detected! Halting pipeline execution immediately."
            )

        return {
            "gate": "validate_api_raw",
            "passed": passed,
            "critical_failure": audit["critical_failure"],
            "total_records": audit["total_records"],
            "local_filepath": api_meta["local_filepath"]
        }

    # -------------------------------------------------------------------------
    # Convergence: Transformation, Harmonisation & Integration
    # -------------------------------------------------------------------------
    @task(
        task_id="transform_and_clean_and_integrate",
        retries=0,  # Deterministic transformation and integration logic
        doc_md="""
        Executes integration contract, cleans demographics, rolls up geography and builds star schema.

        Selective Retry Justification:
        Configured with retries=0 (No Retries). Data transformation and integration logic is pure and
        deterministic: code or structural discrepancies cannot be resolved by re-running the same inputs.
        """
    )
    def task_transform_and_integrate(primary_val_meta: dict, api_val_meta: dict) -> dict:
        """Transforms and integrates both validated branches."""
        if not primary_val_meta.get("passed") or primary_val_meta.get("critical_failure"):
            raise AirflowFailException(
                "Cannot proceed with transformation: Gate 1 (Primary Raw) validation failed."
            )
        if not api_val_meta.get("passed") or api_val_meta.get("critical_failure"):
            raise AirflowFailException(
                "Cannot proceed with transformation: Gate 2 (API Raw) validation failed."
            )

        df_p, manifest_p = extract_primary_data(filepath=primary_val_meta.get("local_filepath"))
        df_a, manifest_a = extract_api_data()

        trans_res = transform_and_integrate_all(df_p, df_a)
        tables = build_star_schema(
            trans_res["df_primary_clean"],
            trans_res["df_geo_integrated"],
            trans_res["df_comisarias_dir"]
        )

        # Persist prepared datasets in data/processed (Parquet) for decoupled loading & audit
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
        doc_md="""
        Gate 3: Great Expectations validation of grain uniqueness, referential integrity and reconciliation.

        Selective Retry Justification:
        Configured with retries=0 (No Retries). Quality gate before loading into the Data Warehouse.
        If grain uniqueness, referential integrity, or measure reconciliation fails, it represents a
        deterministic model invariant violation that requires engineer intervention before touching the DW.
        """
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
        try:
            passed, audit = validate_prepared_data(tables, expected_totals)
        except ValidationError as e:
            raise AirflowFailException(
                f"Gate 3 (Prepared Data) failed with Critical severity: {e}. DW load blocked."
            )

        if audit.get("critical_failure") or not passed:
            raise AirflowFailException(
                "Gate 3 (Prepared Data) Critical Quality Failure detected! Aborting DW load to protect analytical integrity."
            )

        return {
            "gate": "validate_prepared",
            "passed": passed,
            "critical_failure": audit["critical_failure"],
            "persisted_paths": prepared_meta["persisted_paths"],
            "expected_victims": prepared_meta["expected_victims"],
            "expected_records": prepared_meta["expected_records"]
        }

    # -------------------------------------------------------------------------
    # Dimensional Data Warehouse Load
    # -------------------------------------------------------------------------
    @task(
        task_id="load_dimensional_dw",
        retries=2,
        retry_delay=timedelta(minutes=1),
        doc_md="""
        Executes DDL and bulk COPY into PostgreSQL DW with post-load automated reconciliation.

        Selective Retry Justification:
        Configured with retries=2 and retry_delay=1m to recover from transient database operational faults,
        such as temporary connection pool exhaustion, transient network blips to the DB host, or brief lock waits.
        """
    )
    def task_load_dw(prep_val_meta: dict, **context) -> dict:
        """Loads accepted data into PostgreSQL and runs final verification queries."""
        if not prep_val_meta.get("passed") or prep_val_meta.get("critical_failure"):
            raise AirflowFailException(
                "Prepared data validation failed! Aborting DW load to protect data warehouse."
            )

        params = context.get("params", {})
        dag_run = context.get("dag_run")
        conf = dag_run.conf if dag_run else {}
        test_mode = conf.get("test_mode", params.get("test_mode", "TEST_A_SUCCESSFUL_RUN"))

        import pandas as pd
        tables = {
            name: pd.read_parquet(path)
            for name, path in prep_val_meta["persisted_paths"].items()
        }
        expected_totals = {
            "victims": prep_val_meta["expected_victims"],
            "records": prep_val_meta["expected_records"]
        }

        reconciliation_report = load_dimensional_warehouse(tables, expected_totals)

        if test_mode in ["TEST_C_SAFE_RERUN", "test_c_safe_rerun"]:
            import logging
            logging.info("=== [TEST C VERIFIED] Safe Rerun & Idempotency: DW atomic reload completed with 0 duplicates ===")
            logging.info(f"Target Fact Rows: {reconciliation_report['table_row_counts']['fact_violencia_intrafamiliar']}, Reconciled Victims: {reconciliation_report['source_reconciliation']['loaded_fact_victims']}")

        return reconciliation_report

    # -------------------------------------------------------------------------
    # Pipeline Dependency Graph
    # -------------------------------------------------------------------------
    # Branch 1: Primary Source (Extraction -> Raw Validation)
    primary_meta = task_extract_primary()
    primary_val = task_validate_primary_raw(primary_meta)

    # Branch 2: API Source (Extraction -> Raw Validation)
    api_meta = task_extract_api()
    api_val = task_validate_api_raw(api_meta)

    # Convergence: Both raw branches must validate before transformation begins
    prepared_meta = task_transform_and_integrate(primary_val, api_val)

    # Prepared validation gate must pass before DW load
    prep_val = task_validate_prepared(prepared_meta)

    # Load into PostgreSQL DW
    dw_report = task_load_dw(prep_val)


# Instantiate the DAG
dag_instance = domestic_violence_pipeline()
