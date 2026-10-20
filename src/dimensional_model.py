"""Refined Dimensional Model Module.

Constructs the refined Star Schema:
  - dim_tiempo: Dense daily calendar with completeness flags (R1).
  - dim_geografia: Enriched with municipal category, installed comisarías, legal requirement, and gap (R2, R6, R7).
  - dim_victima: Gender and age cohorts with child vulnerability flag (R3, R5).
  - dim_medio: Means of aggression, categories, and lethality flag (R4, R5).
  - dim_comisaria: Outrigger directory of physical comisarías for operational/geospatial analytics.
  - fact_violencia_intrafamiliar: Transaction fact table strictly enforced at the declared municipal grain.
"""

import logging
from typing import Dict
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("DimensionalModel")

MONTH_NAMES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}
DAY_NAMES = {
    0: "Lunes", 1: "Martes", 2: "Miercoles", 3: "Jueves",
    4: "Viernes", 5: "Sabado", 6: "Domingo",
}


def build_time_dimension(fechas: pd.Series) -> pd.DataFrame:
    """Builds dense daily calendar dimension; es_periodo_completo flags fully covered years."""
    logger.info("Building Time Dimension (dim_tiempo)...")
    observed = pd.to_datetime(pd.Series(fechas).dropna().unique())
    calendar = pd.date_range(observed.min(), observed.max(), freq="D")

    max_date = observed.max()
    last_full_year = max_date.year - 1 if (max_date.month, max_date.day) != (12, 31) else max_date.year

    df = pd.DataFrame({"fecha": calendar})
    df.insert(0, "id_tiempo", range(1, len(df) + 1))
    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["nombre_mes"] = df["mes"].map(MONTH_NAMES)
    df["trimestre"] = df["fecha"].dt.quarter
    df["semestre"] = (df["mes"] > 6).astype(int) + 1
    df["dia_semana"] = df["fecha"].dt.weekday + 1
    df["nombre_dia"] = df["fecha"].dt.weekday.map(DAY_NAMES)
    df["es_fin_semana"] = df["fecha"].dt.weekday >= 5
    df["es_periodo_completo"] = df["anio"] <= last_full_year
    df["fecha"] = df["fecha"].dt.date

    logger.info(
        "dim_tiempo generated: %d calendar days (%s to %s). Last complete year: %d.",
        len(df), df["fecha"].iat[0], df["fecha"].iat[-1], last_full_year
    )
    return df


def build_geographic_dimension(df_geo_integrated: pd.DataFrame) -> pd.DataFrame:
    """Builds the enriched geographic dimension with institutional capacity metrics."""
    logger.info("Building Enriched Geographic Dimension (dim_geografia)...")
    cols = [
        "codigo_dane_municipio", "municipio", "codigo_dane_departamento", "departamento",
        "es_capital", "categoria_municipio", "comisarias_instaladas", "comisarias_requeridas_ley",
        "brecha_comisarias", "tiene_comisaria"
    ]
    df_geo = (
        df_geo_integrated[cols]
        .drop_duplicates(subset=["codigo_dane_municipio"])
        .sort_values(["departamento", "municipio"])
        .reset_index(drop=True)
    )

    df_geo.insert(0, "id_geografia", range(1, len(df_geo) + 1))
    logger.info("dim_geografia generated: %d municipalities.", len(df_geo))
    return df_geo


def build_victim_dimension(df_clean: pd.DataFrame) -> pd.DataFrame:
    """Builds victim demographic dimension with child vulnerability flag."""
    logger.info("Building Victim Demographic Dimension (dim_victima)...")
    df_victima = (
        df_clean[["genero", "grupo_etario"]]
        .drop_duplicates()
        .sort_values(["genero", "grupo_etario"])
        .reset_index(drop=True)
    )

    label = {"FEMENINO": "MUJER", "MASCULINO": "HOMBRE"}
    df_victima["perfil_demografico"] = [
        f"{label[g]} {a}" if g in label else f"NO REPORTADO ({a})"
        for g, a in zip(df_victima["genero"], df_victima["grupo_etario"])
    ]
    df_victima["es_menor_de_edad"] = df_victima["grupo_etario"].isin(["MENORES", "ADOLESCENTES"])

    df_victima.insert(0, "id_victima", range(1, len(df_victima) + 1))
    logger.info("dim_victima generated: %d demographic cohorts.", len(df_victima))
    return df_victima


def build_weapon_dimension(df_clean: pd.DataFrame) -> pd.DataFrame:
    """Builds weapon and means of aggression dimension with lethality flag."""
    logger.info("Building Weapon Dimension (dim_medio)...")
    df_medio = (
        df_clean[["medio_agresion", "categoria_mecanismo"]]
        .drop_duplicates()
        .sort_values(["categoria_mecanismo", "medio_agresion"])
        .reset_index(drop=True)
    )
    df_medio["es_arma_letal"] = df_medio["categoria_mecanismo"].isin(["ARMAS BLANCAS", "ARMAS DE FUEGO"])
    df_medio.insert(0, "id_medio", range(1, len(df_medio) + 1))
    logger.info("dim_medio generated: %d means of aggression.", len(df_medio))
    return df_medio


def build_comisaria_dimension(df_comisarias_dir: pd.DataFrame) -> pd.DataFrame:
    """Builds physical directory dimension for individual Comisarías de Familia."""
    logger.info("Building Comisaría Directory Dimension (dim_comisaria)...")
    cols = [
        "codigo_dane_municipio", "nombre_comisaria", "direccion",
        "telefono", "horario_atencion", "categoria_municipio"
    ]
    df_com = (
        df_comisarias_dir[cols]
        .drop_duplicates()
        .sort_values(["codigo_dane_municipio", "nombre_comisaria"])
        .reset_index(drop=True)
    )
    df_com.insert(0, "id_comisaria", range(1, len(df_com) + 1))
    logger.info("dim_comisaria generated: %d physical entries.", len(df_com))
    return df_com


def build_star_schema(
    df_primary_clean: pd.DataFrame,
    df_geo_integrated: pd.DataFrame,
    df_comisarias_dir: pd.DataFrame
) -> Dict[str, pd.DataFrame]:
    """Builds all dimensions, maps surrogate foreign keys, and aggregates facts to the declared municipal grain."""
    logger.info("Building Refined Star Schema from %d prepared records...", len(df_primary_clean))

    dim_tiempo = build_time_dimension(df_primary_clean["fecha"])
    dim_geografia = build_geographic_dimension(df_geo_integrated)
    dim_victima = build_victim_dimension(df_primary_clean)
    dim_medio = build_weapon_dimension(df_primary_clean)
    dim_comisaria = build_comisaria_dimension(df_comisarias_dir)

    logger.info("Mapping surrogate foreign keys onto fact records...")
    df = df_primary_clean.copy()
    df = df.merge(dim_tiempo[["id_tiempo", "fecha"]], on="fecha", how="left")
    df = df.merge(
        dim_geografia[["id_geografia", "codigo_dane_municipio"]],
        on="codigo_dane_municipio", how="left"
    )
    df = df.merge(
        dim_victima[["id_victima", "genero", "grupo_etario"]],
        on=["genero", "grupo_etario"], how="left"
    )
    df = df.merge(
        dim_medio[["id_medio", "medio_agresion", "categoria_mecanismo"]],
        on=["medio_agresion", "categoria_mecanismo"], how="left"
    )

    # Check for missing foreign keys
    grain = ["id_tiempo", "id_geografia", "id_victima", "id_medio"]
    for fk in grain:
        n_missing = int(df[fk].isna().sum())
        if n_missing:
            raise ValueError(f"{n_missing} records could not be mapped to surrogate key {fk}.")

    # Aggregate strictly to the declared municipal grain
    logger.info("Aggregating fact table to declared grain %s...", tuple(grain))
    fact = (
        df.groupby(grain, as_index=False)
        .agg(
            cantidad_victimas=("cantidad_victimas", "sum"),
            numero_registros=("cantidad_victimas", "size")
        )
        .sort_values(grain)
        .reset_index(drop=True)
    )

    fact.insert(0, "id_hecho", range(1, len(fact) + 1))
    fact["fecha_carga"] = pd.Timestamp.now().replace(microsecond=0)
    fact = fact[["id_hecho"] + grain + ["cantidad_victimas", "numero_registros", "fecha_carga"]]

    logger.info(
        "Fact table constructed: %d rows (declared grain), %d victims, %d source records collapsed.",
        len(fact), int(fact["cantidad_victimas"].sum()), len(df) - len(fact)
    )

    return {
        "dim_tiempo": dim_tiempo,
        "dim_geografia": dim_geografia,
        "dim_victima": dim_victima,
        "dim_medio": dim_medio,
        "dim_comisaria": dim_comisaria,
        "fact_violencia_intrafamiliar": fact
    }


if __name__ == "__main__":
    from extract_primary import extract_primary_data
    from extract_api import extract_api_data
    from transform_and_integrate import transform_and_integrate_all

    df_p, _ = extract_primary_data()
    df_a, _ = extract_api_data()
    trans_res = transform_and_integrate_all(df_p, df_a)

    tables = build_star_schema(
        trans_res["df_primary_clean"],
        trans_res["df_geo_integrated"],
        trans_res["df_comisarias_dir"]
    )

    print("\n--- MODEL SUMMARY ---")
    for name, tbl in tables.items():
        print(f"Table: {name:32} | Rows: {len(tbl):,}")
