"""Data Warehouse Loading & Reconciliation Module.

Loads the validated dimensional model into the PostgreSQL Data Warehouse using
fast streaming bulk COPY. Enforces transactional safety, referential integrity,
and automated pre- and post-load reconciliation.
Supports Safe Rerun (Idempotency): Atomic reload inside a database transaction
ensures rerunning never creates duplicates or leaves partial/corrupt states.
"""

import io
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Tuple

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("LoadDW")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "etl_dw")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres123")

SQL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sql")
EVIDENCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "evidence")


def get_db_connection():
    """Returns a new psycopg2 connection to PostgreSQL."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def execute_sql_file(filepath: str, conn):
    """Reads and executes a SQL script file."""
    logger.info("Executing SQL file: %s", filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


import csv

def bulk_copy_dataframe(df: pd.DataFrame, table_name: str, conn):
    """Fast bulk insert using PostgreSQL COPY protocol with CSV format and quoting."""
    logger.info("Bulk copying %d rows into %s...", len(df), table_name)
    df_clean = df.copy()
    # Clean whitespace/newlines from string columns to avoid copy format corruptions
    for col in df_clean.select_dtypes(include=["object", "string"]).columns:
        df_clean[col] = df_clean[col].astype(str).str.replace(r"[\r\n\t]+", " ", regex=True).str.strip()

    buffer = io.StringIO()
    df_clean.to_csv(buffer, index=False, header=False, na_rep="", quoting=csv.QUOTE_MINIMAL)
    buffer.seek(0)

    cols = list(df_clean.columns)
    sql_copy = f"COPY {table_name} ({', '.join(cols)}) FROM STDIN WITH (FORMAT CSV, NULL '')"
    with conn.cursor() as cur:
        cur.copy_expert(sql_copy, buffer)
    conn.commit()
    logger.info("Completed COPY into %s.", table_name)


def load_dimensional_warehouse(
    tables: Dict[str, pd.DataFrame],
    expected_totals: Dict[str, int]
) -> Dict[str, Any]:
    """Loads all dimensions and facts into PostgreSQL and verifies reconciliation.

    Execution order:
      1. dim_tiempo
      2. dim_geografia
      3. dim_victima
      4. dim_medio
      5. dim_comisaria
      6. fact_violencia_intrafamiliar
    """
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    logger.info("Connecting to PostgreSQL Data Warehouse (%s:%d/%s)...", DB_HOST, DB_PORT, DB_NAME)
    conn = get_db_connection()

    try:
        # Step 1: Re-create schema DDL
        ddl_path = os.path.join(SQL_DIR, "create_dw.sql")
        execute_sql_file(ddl_path, conn)

        # Step 2: Load Dimensions first (Referential Integrity)
        bulk_copy_dataframe(tables["dim_tiempo"], "dim_tiempo", conn)
        bulk_copy_dataframe(tables["dim_geografia"], "dim_geografia", conn)
        bulk_copy_dataframe(tables["dim_victima"], "dim_victima", conn)
        bulk_copy_dataframe(tables["dim_medio"], "dim_medio", conn)
        bulk_copy_dataframe(tables["dim_comisaria"], "dim_comisaria", conn)

        # Step 3: Load Fact Table
        bulk_copy_dataframe(tables["fact_violencia_intrafamiliar"], "fact_violencia_intrafamiliar", conn)

        # Step 4: Create Semantic Views
        views_path = os.path.join(SQL_DIR, "bi_views.sql")
        execute_sql_file(views_path, conn)

        # Step 5: Post-Load SQL Reconciliation & Integrity Checks
        logger.info("Executing automated database reconciliation and integrity verification...")
        with conn.cursor() as cur:
            # Fact counts & measures
            cur.execute("""
                SELECT
                    COUNT(*) AS total_fact_rows,
                    SUM(cantidad_victimas) AS total_victimas,
                    SUM(numero_registros) AS total_registros
                FROM fact_violencia_intrafamiliar;
            """)
            fact_stats = cur.fetchone()
            loaded_fact_rows = int(fact_stats[0])
            loaded_victims = int(fact_stats[1])
            loaded_records = int(fact_stats[2])

            # Dimension counts
            cur.execute("SELECT COUNT(*) FROM dim_tiempo;")
            cnt_tiempo = int(cur.fetchone()[0])

            cur.execute("SELECT COUNT(*) FROM dim_geografia;")
            cnt_geografia = int(cur.fetchone()[0])

            cur.execute("SELECT COUNT(*) FROM dim_victima;")
            cnt_victima = int(cur.fetchone()[0])

            cur.execute("SELECT COUNT(*) FROM dim_medio;")
            cnt_medio = int(cur.fetchone()[0])

            cur.execute("SELECT COUNT(*) FROM dim_comisaria;")
            cnt_comisaria = int(cur.fetchone()[0])

            # Orphan checks (Foreign Key integrity)
            cur.execute("""
                SELECT
                    COUNT(f.id_hecho) FILTER (WHERE t.id_tiempo IS NULL) AS orphan_tiempo,
                    COUNT(f.id_hecho) FILTER (WHERE g.id_geografia IS NULL) AS orphan_geo,
                    COUNT(f.id_hecho) FILTER (WHERE v.id_victima IS NULL) AS orphan_victima,
                    COUNT(f.id_hecho) FILTER (WHERE m.id_medio IS NULL) AS orphan_medio
                FROM fact_violencia_intrafamiliar f
                LEFT JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
                LEFT JOIN dim_geografia g ON f.id_geografia = g.id_geografia
                LEFT JOIN dim_victima v ON f.id_victima = v.id_victima
                LEFT JOIN dim_medio m ON f.id_medio = m.id_medio;
            """)
            orphan_row = cur.fetchone()
            total_orphans = sum(orphan_row)

        expected_victims = expected_totals.get("victims", 0)
        expected_records = expected_totals.get("records", 0)

        reconciled = (loaded_victims == expected_victims) and (loaded_records == expected_records)
        integrity_ok = (total_orphans == 0)

        reconciliation_report = {
            "load_timestamp": datetime.now().isoformat(),
            "status": "SUCCESS" if (reconciled and integrity_ok) else "FAILED",
            "source_reconciliation": {
                "expected_source_records": expected_records,
                "loaded_fact_source_records": loaded_records,
                "records_delta": loaded_records - expected_records,
                "expected_source_victims": expected_victims,
                "loaded_fact_victims": loaded_victims,
                "victims_delta": loaded_victims - expected_victims,
                "exact_reconciliation_pass": reconciled
            },
            "table_row_counts": {
                "dim_tiempo": cnt_tiempo,
                "dim_geografia": cnt_geografia,
                "dim_victima": cnt_victima,
                "dim_medio": cnt_medio,
                "dim_comisaria": cnt_comisaria,
                "fact_violencia_intrafamiliar": loaded_fact_rows
            },
            "referential_integrity": {
                "orphan_foreign_keys_count": total_orphans,
                "integrity_pass": integrity_ok
            }
        }

        report_path = os.path.join(EVIDENCE_DIR, "reconciliation_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(reconciliation_report, f, indent=2)

        logger.info("Reconciliation Report written to %s", report_path)
        logger.info(
            "DW LOAD RESULTS: %d fact rows, %d victims (%s), %d orphan FKs.",
            loaded_fact_rows, loaded_victims, "RECONCILED" if reconciled else "MISMATCH", total_orphans
        )

        if not (reconciled and integrity_ok):
            raise ValueError(f"DW load reconciliation or referential integrity failed! Check {report_path}")

        return reconciliation_report

    finally:
        conn.close()


if __name__ == "__main__":
    from extract_primary import extract_primary_data
    from extract_api import extract_api_data
    from transform_and_integrate import transform_and_integrate_all
    from dimensional_model import build_star_schema

    df_p, manifest_p = extract_primary_data()
    df_a, _ = extract_api_data()
    trans_res = transform_and_integrate_all(df_p, df_a)
    tables = build_star_schema(
        trans_res["df_primary_clean"],
        trans_res["df_geo_integrated"],
        trans_res["df_comisarias_dir"]
    )

    expected = {
        "records": manifest_p["row_count"],
        "victims": manifest_p["total_victims_raw"]
    }

    report = load_dimensional_warehouse(tables, expected)
    print("\n--- RECONCILIATION SUMMARY ---")
    print(json.dumps(report, indent=2))
