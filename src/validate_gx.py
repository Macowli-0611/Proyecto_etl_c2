"""Automated Data Quality Validation Module with Great Expectations 1.X.

Implements the three explicit validation gates required by the Second Delivery:
  1. validate_primary_raw   - Gate 1: raw primary branch (Policía Nacional - DIJIN)
  2. validate_api_raw       - Gate 2: raw API branch (MinJusticia - Comisarías de Familia)
  3. validate_prepared_data - Gate 3: transformed & integrated star schema (pre-DW load)

Design
------
* Single source of truth: the declarative Expectation Suites in ``gx/expectations/*.json``.
  Every expectation in a suite carries ``meta.rule_id``, ``meta.severity``, ``meta.requirement``,
  ``meta.metric`` and ``meta.threshold_justification``. This module builds the GX suite *from*
  those files, so documentation, configuration and execution cannot drift apart.
* Controlled execution: for each data object an ephemeral GX context registers a pandas
  Data Source -> Data Asset -> Batch Definition, links it to the suite through a
  Validation Definition and runs it through a Checkpoint (see ``gx/checkpoints``).
* Severity policy (pipeline response, decided here and NOT by GX):
    - Critical -> raise ``ValidationError`` (Airflow task FAILED, downstream UPSTREAM_FAILED).
    - Warning  -> recorded in the evidence file and logs; the batch continues.
* Evidence: every run writes ``docs/evidence/gx_validation_<gate>_<timestamp>.json`` and a
  ``*_latest.json`` pointer with rule-level outcomes and unexpected counts/examples.
* Profiling/cleaning separation: validation never modifies the batch. Type casts needed only
  for evaluation (e.g. ``CANTIDAD_NUMERIC``) are added to a copy and documented in the suite meta.
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

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

MAX_EXAMPLES = 10  # unexpected examples kept per rule in the evidence file


class ValidationError(Exception):
    """Raised when at least one Critical expectation fails (pipeline must stop)."""


# ---------------------------------------------------------------------------
# Suite loading and expectation construction
# ---------------------------------------------------------------------------
def load_expectation_suite_json(suite_name: str) -> Dict[str, Any]:
    """Loads a declarative expectation suite definition from gx/expectations/."""
    filename = suite_name if suite_name.endswith(".json") else f"{suite_name}.json"
    filepath = os.path.join(EXPECTATIONS_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Expectation suite not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _expectation_class(exp_type: str):
    """Maps a snake_case GX expectation type to its class (e.g. expect_x_y -> ExpectXY)."""
    class_name = "".join(part.capitalize() for part in exp_type.split("_"))
    exp_cls = getattr(gxe, class_name, None)
    if exp_cls is None:
        raise ValueError(f"Unknown Great Expectations expectation type: {exp_type}")
    return exp_cls


def _resolve_kwargs(kwargs: Dict[str, Any], runtime_params: Dict[str, Any]) -> Dict[str, Any]:
    """Replaces "$placeholder" values with runtime parameters (dimension key sets, totals)."""
    resolved = {}
    for key, value in kwargs.items():
        if isinstance(value, str) and value.startswith("$"):
            if value not in runtime_params:
                raise KeyError(f"Missing runtime parameter {value} for expectation kwarg '{key}'")
            resolved[key] = runtime_params[value]
        else:
            resolved[key] = value
    return resolved


def _describe_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Compact kwargs for evidence (large runtime value sets are summarized)."""
    out = {}
    for key, value in kwargs.items():
        if isinstance(value, (list, set, tuple)) and len(value) > 20:
            out[key] = f"<{len(value)} values>"
        else:
            out[key] = value
    return out


def _compact_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Keeps the interpretable part of a GX result (counts, percentages, examples)."""
    keep = [
        "observed_value", "element_count", "missing_count", "missing_percent",
        "unexpected_count", "unexpected_percent", "unexpected_percent_nonmissing",
        "partial_unexpected_list", "details",
    ]
    compact = {k: result[k] for k in keep if k in result}
    if isinstance(compact.get("partial_unexpected_list"), list):
        compact["partial_unexpected_list"] = compact["partial_unexpected_list"][:MAX_EXAMPLES]
    if isinstance(compact.get("observed_value"), (list, set)) and len(compact["observed_value"]) > 30:
        compact["observed_value"] = f"<{len(compact['observed_value'])} values>"
    return compact


# ---------------------------------------------------------------------------
# Generic controlled execution of one suite (or one table slice of a suite)
# ---------------------------------------------------------------------------
def _run_suite_on_dataframe(
    df: pd.DataFrame,
    suite_json: Dict[str, Any],
    gate: str,
    data_object: str,
    expectations: List[Dict[str, Any]],
    runtime_params: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Builds a GX suite from JSON expectations and runs it through a Checkpoint.

    Column-level expectations whose column is absent are reported as NOT_EVALUATED; the
    schema expectation (expect_table_columns_to_match_set) already fails in that case.
    """
    runtime_params = runtime_params or {}
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
    safe_obj = re.sub(r"[^A-Za-z0-9_]", "_", data_object)

    context = gx.get_context(mode="ephemeral")
    data_source = context.data_sources.add_pandas(f"pandas_{gate}_{safe_obj}_{stamp}")
    data_asset = data_source.add_dataframe_asset(f"{safe_obj}_asset")
    batch_def = data_asset.add_batch_definition_whole_dataframe(f"batch_{safe_obj}")

    suite = context.suites.add(gx.ExpectationSuite(name=f"{suite_json['name']}__{safe_obj}"))

    outcomes: List[Dict[str, Any]] = []
    registered: List[Dict[str, Any]] = []
    for exp in expectations:
        meta = exp.get("meta", {})
        kwargs = _resolve_kwargs(exp.get("kwargs", {}), runtime_params)
        column = kwargs.get("column")
        if column is not None and column not in df.columns:
            outcomes.append({
                "rule_id": meta.get("rule_id"),
                "severity": meta.get("severity"),
                "expectation": exp["type"],
                "kwargs": _describe_kwargs(kwargs),
                "data_object": data_object,
                "success": None,
                "status": "NOT_EVALUATED_COLUMN_MISSING",
            })
            continue
        exp_cls = _expectation_class(exp["type"])
        notes = f"{meta.get('rule_id')}: {meta.get('severity')}. {meta.get('metric', '')}"
        gx_exp = exp_cls(**kwargs, notes=notes, meta={"rule_id": meta.get("rule_id"), "severity": meta.get("severity")})
        suite.add_expectation(gx_exp)
        registered.append({"exp": exp, "kwargs": kwargs})

    if registered:
        val_def = context.validation_definitions.add(
            gx.ValidationDefinition(name=f"val_{safe_obj}", data=batch_def, suite=suite)
        )
        checkpoint = context.checkpoints.add(
            gx.Checkpoint(name=f"checkpoint_{safe_obj}", validation_definitions=[val_def], actions=[])
        )
        checkpoint_result = checkpoint.run(batch_parameters={"dataframe": df})
        suite_result = next(iter(checkpoint_result.run_results.values()))

        for res in suite_result.results:
            cfg = res.expectation_config
            res_meta = cfg.meta or {}
            source = next(
                (r for r in registered
                 if r["exp"]["meta"].get("rule_id") == res_meta.get("rule_id")
                 and r["exp"]["type"] == cfg.type
                 and r["kwargs"].get("column") == cfg.kwargs.get("column")),
                None,
            )
            src_meta = source["exp"]["meta"] if source else res_meta
            outcomes.append({
                "rule_id": src_meta.get("rule_id"),
                "severity": src_meta.get("severity"),
                "dimension": src_meta.get("dimension"),
                "requirement": src_meta.get("requirement"),
                "metric": src_meta.get("metric"),
                "expectation": cfg.type,
                "kwargs": _describe_kwargs(source["kwargs"] if source else dict(cfg.kwargs)),
                "data_object": data_object,
                "success": bool(res.success),
                "status": "PASSED" if res.success else "FAILED",
                "result": _compact_result(res.result or {}),
                "exception": (res.exception_info or {}).get("exception_message")
                if isinstance(res.exception_info, dict) and res.exception_info.get("raised_exception") else None,
            })
    return outcomes


def _apply_severity_policy(gate: str, outcomes: List[Dict[str, Any]]) -> Tuple[bool, bool, List[str], List[str]]:
    """Translates rule outcomes into the pipeline response.

    Returns (overall_success, critical_failure, failed_critical_rules, failed_warning_rules).
    A NOT_EVALUATED Critical rule counts as a Critical failure (the contract could not be checked).
    """
    failed_critical, failed_warning = [], []
    for o in outcomes:
        if o["success"] is True:
            continue
        if o["severity"] == "Critical":
            failed_critical.append(o["rule_id"])
            logger.error("[%s] CRITICAL rule failed: %s (%s on %s) -> %s",
                         gate, o["rule_id"], o["expectation"], o.get("kwargs", {}).get("column", o["data_object"]),
                         o.get("result", {}).get("unexpected_count", o["status"]))
        else:
            failed_warning.append(o["rule_id"])
            logger.warning("[%s] WARNING rule failed: %s (%s) -> %s. Batch continues per policy.",
                           gate, o["rule_id"], o["expectation"],
                           o.get("result", {}).get("unexpected_percent", o["status"]))
    critical_failure = bool(failed_critical)
    overall_success = not failed_critical and not failed_warning
    return overall_success, critical_failure, sorted(set(failed_critical)), sorted(set(failed_warning))


def _save_validation_result(gate_name: str, result_dict: Dict[str, Any]) -> str:
    """Saves validation execution results as JSON for audit and observability."""
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(EVIDENCE_DIR, f"gx_validation_{gate_name}_{timestamp}.json")
    latest_path = os.path.join(EVIDENCE_DIR, f"gx_validation_{gate_name}_latest.json")
    for path in (filepath, latest_path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2, default=str, ensure_ascii=False)
    logger.info("Saved %s validation evidence to %s", gate_name, filepath)
    return filepath


def _finalize_gate(
    gate: str,
    evidence_name: str,
    suite_json: Dict[str, Any],
    outcomes: List[Dict[str, Any]],
    extra: Dict[str, Any],
    batch_id: Optional[str],
) -> Tuple[bool, Dict[str, Any]]:
    overall_success, critical_failure, failed_critical, failed_warning = _apply_severity_policy(gate, outcomes)
    if critical_failure:
        pipeline_action = "STOP: Critical rule violated; downstream tasks must not run."
    elif failed_warning:
        pipeline_action = "CONTINUE_WITH_WARNING: Warning rules recorded; batch accepted per policy."
    else:
        pipeline_action = "CONTINUE: all rules passed."

    audit_payload = {
        "gate": gate,
        "suite_name": suite_json["name"],
        "suite_file": f"gx/expectations/{suite_json['name']}.json",
        "batch_id": batch_id,
        "timestamp": datetime.now().isoformat(),
        **extra,
        "rules_evaluated": len(outcomes),
        "overall_success": overall_success,
        "critical_failure": critical_failure,
        "failed_critical_rules": failed_critical,
        "failed_warning_rules": failed_warning,
        "pipeline_action": pipeline_action,
        "results": outcomes,
    }
    audit_payload["evidence_file"] = _save_validation_result(evidence_name, audit_payload)

    if critical_failure:
        raise ValidationError(
            f"{gate} failed with Critical severity (rules: {', '.join(failed_critical)}). "
            f"Execution halted to protect downstream tasks. Evidence: {audit_payload['evidence_file']}"
        )
    logger.info("%s passed (%s).", gate, pipeline_action)
    return True, audit_payload


# ---------------------------------------------------------------------------
# Gate 1 - Primary raw
# ---------------------------------------------------------------------------
def validate_primary_raw(df_raw: pd.DataFrame, batch_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
    """Gate 1: validates the raw primary batch against gx/expectations/primary_raw_suite.json."""
    logger.info("--- GATE 1: Validating Raw Primary Source (%d rows) ---", len(df_raw))
    suite_json = load_expectation_suite_json("primary_raw_suite")

    df_eval = df_raw.copy()
    if "CANTIDAD" in df_eval.columns:
        df_eval["CANTIDAD_NUMERIC"] = pd.to_numeric(df_eval["CANTIDAD"], errors="coerce")

    outcomes = _run_suite_on_dataframe(
        df_eval, suite_json, "validate_primary_raw", "raw_primary_batch", suite_json["expectations"]
    )
    return _finalize_gate(
        "validate_primary_raw", "primary_raw", suite_json, outcomes,
        {"total_records": len(df_raw)}, batch_id,
    )


# ---------------------------------------------------------------------------
# Gate 2 - API raw
# ---------------------------------------------------------------------------
def validate_api_raw(df_api: pd.DataFrame, batch_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
    """Gate 2: validates the normalized raw API payload against gx/expectations/api_raw_suite.json."""
    logger.info("--- GATE 2: Validating Raw API Source (%d rows) ---", len(df_api))
    suite_json = load_expectation_suite_json("api_raw_suite")

    df_eval = df_api.copy()
    if "existencia_de_comisarias" in df_eval.columns:
        df_eval["existencia_numeric"] = pd.to_numeric(df_eval["existencia_de_comisarias"], errors="coerce")

    outcomes = _run_suite_on_dataframe(
        df_eval, suite_json, "validate_api_raw", "raw_api_batch", suite_json["expectations"]
    )
    return _finalize_gate(
        "validate_api_raw", "api_raw", suite_json, outcomes,
        {"total_records": len(df_api)}, batch_id,
    )


# ---------------------------------------------------------------------------
# Gate 3 - Prepared data
# ---------------------------------------------------------------------------
def validate_prepared_data(
    tables: Dict[str, pd.DataFrame],
    expected_totals: Dict[str, int],
    batch_id: Optional[str] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """Gate 3: validates prepared star-schema tables against gx/expectations/prepared_data_suite.json.

    Each table referenced by ``meta.table`` is validated as its own GX batch. Referential integrity
    and reconciliation thresholds are runtime parameters resolved from the prepared dimensions and
    from the accepted raw batch totals.
    """
    logger.info("--- GATE 3: Validating Transformed & Integrated Prepared Data ---")
    suite_json = load_expectation_suite_json("prepared_data_suite")

    runtime_params = {
        "$dim_tiempo.id_tiempo": tables["dim_tiempo"]["id_tiempo"].dropna().unique().tolist(),
        "$dim_geografia.id_geografia": tables["dim_geografia"]["id_geografia"].dropna().unique().tolist(),
        "$dim_victima.id_victima": tables["dim_victima"]["id_victima"].dropna().unique().tolist(),
        "$dim_medio.id_medio": tables["dim_medio"]["id_medio"].dropna().unique().tolist(),
        "$expected_victims": int(expected_totals.get("victims", 0)),
        "$expected_records": int(expected_totals.get("records", 0)),
    }

    by_table: Dict[str, List[Dict[str, Any]]] = {}
    for exp in suite_json["expectations"]:
        by_table.setdefault(exp["meta"]["table"], []).append(exp)

    outcomes: List[Dict[str, Any]] = []
    for table_name, exps in by_table.items():
        if table_name not in tables:
            raise KeyError(f"Prepared table '{table_name}' required by the suite was not produced.")
        outcomes.extend(_run_suite_on_dataframe(
            tables[table_name], suite_json, "validate_prepared", table_name, exps, runtime_params
        ))

    fact = tables["fact_violencia_intrafamiliar"]
    extra = {
        "total_fact_rows": len(fact),
        "total_victims": int(fact["cantidad_victimas"].sum()),
        "total_records": int(fact["numero_registros"].sum()),
        "expected_victims": runtime_params["$expected_victims"],
        "expected_records": runtime_params["$expected_records"],
        "dim_geografia_rows": len(tables["dim_geografia"]),
    }
    return _finalize_gate("validate_prepared", "prepared", suite_json, outcomes, extra, batch_id)
