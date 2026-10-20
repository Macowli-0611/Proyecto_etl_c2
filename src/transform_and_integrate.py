"""Transformation and API Integration Module.

Implements the Integration Contract between the Policía Nacional domestic violence reports
and the Ministerio de Justicia Comisarías de Familia API source.
Applies data cleaning, harmonization, derived attributes, and reconciles coverage.
CRITICAL: Applies known engineering rules without silently modifying data to force validations.
"""

import logging
from typing import Dict, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("TransformAndIntegrate")

# Blade weapon harmonization dictionary (Finding 5 from Delivery 1)
BLADE_WEAPONS = {
    "ARMA BLANCA / CORTOPUNZANTE": "ARMA BLANCA",
    "CORTOPUNZANTES": "ARMA BLANCA",
    "CORTANTES": "ARMA BLANCA",
    "PUNZANTES": "ARMA BLANCA",
}

# Mechanism category classification
MECHANISM_CATEGORIES = {
    "ARMA BLANCA": "ARMAS BLANCAS",
    "ARMA DE FUEGO": "ARMAS DE FUEGO",
    "CONTUNDENTES": "CONTUNDENTES",
    "SIN EMPLEO DE ARMAS": "SIN EMPLEO DE ARMAS",
    "NO REPORTADO": "NO REPORTADO",
    "ESCOPOLAMINA": "QUIMICOS / SUSTANCIAS",
    "SUSTANCIAS TOXICAS": "QUIMICOS / SUSTANCIAS",
    "JERINGA": "OTROS",
    "ALMOHADA": "OTROS",
    "CUERDA": "OTROS",
    "BOLSA PLASTICA": "OTROS",
    "PAQUETE BOMBA": "ARTEFACTOS EXPLOSIVOS",
    "ARTEFACTO EXPLOSIVO/INCENDIARIO": "ARTEFACTOS EXPLOSIVOS",
}


def prepare_primary_data(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Prepares and cleans the primary domestic violence dataset.

    - Normalizes DANE code to 5-digit municipal grain.
    - Strips (CT) from municipality names and derives boolean es_capital.
    - Establishes canonical names per DANE code.
    - Harmonizes weapon descriptions and derives mechanism categories and lethality flag.
    - Imputes explicit NO REPORTADO for missing demographics (0 victims dropped).
    - Strictly parses dates.
    """
    logger.info("Preparing primary dataset (%d raw records)...", len(df_raw))
    df = df_raw.copy()

    # 1. Dates
    df["fecha"] = pd.to_datetime(df["FECHA HECHO"], format="%d/%m/%Y", errors="raise").dt.date

    # 2. Geography Rollup to 5 digits (DDMMM)
    dane_str = df["CODIGO DANE"].astype(str).str.strip().str.zfill(8)
    df["codigo_dane_municipio"] = dane_str.str[:5]
    df["codigo_dane_departamento"] = dane_str.str[:2]

    # Resolve known malformed codes from Delivery 1: 00000 -> Medellin, 52000 -> Narino No Especificado
    mask_00000 = df["codigo_dane_municipio"] == "00000"
    if mask_00000.any():
        df.loc[mask_00000, "codigo_dane_municipio"] = "05001"
        df.loc[mask_00000, "codigo_dane_departamento"] = "05"

    mask_52000 = df["codigo_dane_municipio"] == "52000"
    if mask_52000.any():
        df.loc[mask_52000, "codigo_dane_municipio"] = "52999"
        df.loc[mask_52000, "codigo_dane_departamento"] = "52"

    # Department and Municipality cleaning
    df["departamento"] = df["DEPARTAMENTO"].astype(str).str.strip().str.upper()
    muni_raw = df["MUNICIPIO"].astype(str).str.strip()
    df["es_capital"] = muni_raw.str.contains(r"\(CT\)", case=False, regex=True)
    df["municipio"] = muni_raw.str.replace(r"\s*\(CT\)", "", regex=True).str.strip().str.upper()

    # Canonical municipal name per code (modal name)
    valid_mask = df["codigo_dane_municipio"].str.len() == 5
    cat = df.loc[valid_mask, ["codigo_dane_municipio", "municipio"]].dropna()
    canonical_names = (
        cat.groupby("codigo_dane_municipio")["municipio"]
        .agg(lambda s: s.value_counts().index[0] if len(s) > 0 else "NO ESPECIFICADO")
        .to_dict()
    )
    df["municipio"] = df["codigo_dane_municipio"].map(canonical_names).fillna("NO ESPECIFICADO")

    # 3. Means of Aggression Harmonization
    armas_raw = df["ARMAS MEDIOS"].astype(str).str.strip().str.upper()
    df["medio_agresion"] = armas_raw.replace(BLADE_WEAPONS)
    df["categoria_mecanismo"] = df["medio_agresion"].map(
        lambda m: MECHANISM_CATEGORIES.get(m, "OTROS")
    )
    df["es_arma_letal"] = df["categoria_mecanismo"].isin(["ARMAS BLANCAS", "ARMAS DE FUEGO"])

    # 4. Demographic Cohorts
    df["genero"] = df["GENERO"].fillna("NO REPORTADO").astype(str).str.strip().str.upper()
    df["genero"] = df["genero"].replace({"-": "NO REPORTADO", "": "NO REPORTADO", "NAN": "NO REPORTADO"})

    df["grupo_etario"] = df["GRUPO ETARIO"].fillna("NO REPORTADO").astype(str).str.strip().str.upper()
    df["grupo_etario"] = df["grupo_etario"].replace({"-": "NO REPORTADO", "": "NO REPORTADO", "NAN": "NO REPORTADO"})

    # 5. Measure
    df["cantidad_victimas"] = pd.to_numeric(df["CANTIDAD"], errors="raise").astype(int)

    logger.info(
        "Primary dataset prepared: %d records, %d victims.",
        len(df), int(df["cantidad_victimas"].sum())
    )
    return df


def prepare_api_data(df_api: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Prepares and cleans the Comisarías de Familia API source.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]:
          1. df_api_muni: Municipal rollup with institutional capacity & legal gap metrics.
          2. df_comisarias_dir: Directory of physical comisarías for outrigger dimension.
    """
    logger.info("Preparing API dataset (%d raw records)...", len(df_api))
    df = df_api.copy()

    # Normalize DANE municipal code to 5 digits
    df["codigo_dane_municipio"] = (
        df["c_digo_dane_municipio"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )

    # Standardize municipal category (Ley 617 de 2000)
    cat_clean = df["categoria_municipio"].fillna("NO REPORTADA").astype(str).str.strip().str.upper()
    cat_clean = cat_clean.replace({"ESP": "ESPECIAL", "NAN": "NO REPORTADA", "": "NO REPORTADA", "NONE": "NO REPORTADA"})
    df["categoria_municipio_clean"] = cat_clean

    # Clean numeric indicators
    df["comisarias_ley_req"] = pd.to_numeric(
        df["comisarias_ley_2126_100_000"], errors="coerce"
    ).fillna(1).astype(int)

    df["comisarias_existentes"] = pd.to_numeric(
        df["existencia_de_comisarias"], errors="coerce"
    ).fillna(1).astype(int)

    # Physical directory dataframe
    dir_cols = {
        "codigo_dane_municipio": "codigo_dane_municipio",
        "nombre_comisaria": "nombre_comisaria",
        "direcci_n_comisara": "direccion",
        "telefono_de_contacto": "telefono",
        "horario_de_atenci_n": "horario_atencion",
        "categoria_municipio_clean": "categoria_municipio",
        "longitud_de_ubicaci_n_de": "longitud_raw",
        "latitud_de_ubicaci_n_de_la": "latitud_raw"
    }
    df_dir = df[[c for c in dir_cols.keys() if c in df.columns]].copy()
    df_dir.rename(columns=dir_cols, inplace=True)
    df_dir["nombre_comisaria"] = df_dir["nombre_comisaria"].fillna("COMISARÍA DE FAMILIA MUNICIPAL").str.strip().str.upper()
    df_dir["direccion"] = df_dir["direccion"].fillna("SEDE ALCALDÍA / PRINCIPAL").str.strip()
    df_dir["telefono"] = df_dir["telefono"].fillna("NO REPORTADO").str.strip()
    df_dir["horario_atencion"] = df_dir["horario_atencion"].fillna("LUNES A VIERNES EN HORARIO LABORAL").str.strip()

    # Municipal Rollup
    # In each municipality:
    #   - comisarias_instaladas = count of comisarías registered, or max reported count
    #   - comisarias_requeridas_ley = statutory target under Ley 2126 (1 per 100k inhabitants)
    #   - brecha_comisarias = max(0, comisarias_requeridas_ley - comisarias_instaladas)
    #   - tiene_comisaria = True if installed > 0
    muni_grouped = df.groupby("codigo_dane_municipio").agg(
        comisarias_registradas=("nombre_comisaria", "count"),
        comisarias_existentes_max=("comisarias_existentes", "max"),
        comisarias_ley_req_max=("comisarias_ley_req", "max"),
        categoria_municipio=("categoria_municipio_clean", lambda s: s.mode().iat[0] if not s.empty else "NO REPORTADA")
    ).reset_index()

    # Effective installed is the maximum of the counted directory entries and reported existence
    muni_grouped["comisarias_instaladas"] = muni_grouped[
        ["comisarias_registradas", "comisarias_existentes_max"]
    ].max(axis=1)

    muni_grouped["comisarias_requeridas_ley"] = muni_grouped["comisarias_ley_req_max"]
    muni_grouped["brecha_comisarias"] = np.maximum(
        0, muni_grouped["comisarias_requeridas_ley"] - muni_grouped["comisarias_instaladas"]
    )
    muni_grouped["tiene_comisaria"] = muni_grouped["comisarias_instaladas"] > 0

    df_api_muni = muni_grouped[[
        "codigo_dane_municipio", "categoria_municipio",
        "comisarias_instaladas", "comisarias_requeridas_ley",
        "brecha_comisarias", "tiene_comisaria"
    ]]

    logger.info(
        "API dataset prepared: %d physical directory entries, %d municipalities rolled up.",
        len(df_dir), len(df_api_muni)
    )
    return df_api_muni, df_dir


def integrate_geography(
    df_primary_clean: pd.DataFrame,
    df_api_muni: pd.DataFrame,
    df_comisarias_dir: pd.DataFrame
) -> pd.DataFrame:
    """Implements the Geographic Integration Contract.

    Performs an outer integration so that:
      1. 100% of primary municipalities with reported violence are preserved.
      2. Valid Colombian municipalities present in the institutional API directory
         (e.g., Carmen del Darién 27150, Barrancominas 94343) are included in dim_geografia
         to guarantee complete referential integrity with dim_comisaria.
      3. Unmatched areas receive consistent statutory defaults.
    """
    logger.info("Executing Geographic Integration Contract...")

    # Unique primary geography
    geo_cols = ["codigo_dane_municipio", "municipio", "codigo_dane_departamento", "departamento", "es_capital"]
    df_primary_geo = df_primary_clean[geo_cols].drop_duplicates().reset_index(drop=True)

    # Full outer merge with API municipal capacity metrics
    df_geo_integrated = df_primary_geo.merge(
        df_api_muni,
        on="codigo_dane_municipio",
        how="outer"
    )

    # For API-only municipalities, recover department and municipality names from the API directory
    api_only_mask = df_geo_integrated["municipio"].isna()
    if api_only_mask.any():
        logger.info(
            "Found %d API municipalities with 0 primary police reports. Recovering names for dim_geografia...",
            api_only_mask.sum()
        )
        api_names = df_comisarias_dir.groupby("codigo_dane_municipio").first().reset_index()
        for idx in df_geo_integrated[api_only_mask].index:
            code = df_geo_integrated.loc[idx, "codigo_dane_municipio"]
            dept_code = str(code)[:2]
            match = api_names[api_names["codigo_dane_municipio"] == code]
            if not match.empty:
                muni_name = match.iloc[0].get("nombre_comisaria", "MUNICIPIO")
                # Clean comisaria prefix if needed
                muni_name = muni_name.replace("COMISARÍA DE FAMILIA", "").replace("COMISARÍA", "").strip() or "MUNICIPIO"
            else:
                muni_name = "MUNICIPIO"

            df_geo_integrated.loc[idx, "codigo_dane_departamento"] = dept_code
            df_geo_integrated.loc[idx, "municipio"] = muni_name
            df_geo_integrated.loc[idx, "departamento"] = "COLOMBIA"
            df_geo_integrated.loc[idx, "es_capital"] = False

    # Impute defaults for unmatched primary municipalities (e.g. non-municipalized areas)
    df_geo_integrated["categoria_municipio"] = df_geo_integrated["categoria_municipio"].fillna("ÁREA NO MUNICIPALIZADA")
    df_geo_integrated["comisarias_instaladas"] = df_geo_integrated["comisarias_instaladas"].fillna(0).astype(int)
    df_geo_integrated["comisarias_requeridas_ley"] = df_geo_integrated["comisarias_requeridas_ley"].fillna(1).astype(int)
    df_geo_integrated["brecha_comisarias"] = df_geo_integrated["brecha_comisarias"].fillna(1).astype(int)
    df_geo_integrated["tiene_comisaria"] = df_geo_integrated["tiene_comisaria"].fillna(False).astype(bool)
    df_geo_integrated["es_capital"] = df_geo_integrated["es_capital"].fillna(False).astype(bool)

    # Harmonize department names for the 2 API-only codes
    dept_map = {
        "27": "CHOCÓ",
        "94": "GUAINÍA"
    }
    for code_pfx, dname in dept_map.items():
        mask_d = (df_geo_integrated["codigo_dane_departamento"] == code_pfx) & (df_geo_integrated["departamento"] == "COLOMBIA")
        df_geo_integrated.loc[mask_d, "departamento"] = dname

    name_fixes = {
        "27150": "CARMEN DEL DARIÉN",
        "94343": "BARRANCOMINAS"
    }
    for mcode, mname in name_fixes.items():
        mask_m = df_geo_integrated["codigo_dane_municipio"] == mcode
        df_geo_integrated.loc[mask_m, "municipio"] = mname

    logger.info(
        "Geographic integration completed: %d municipalities in dim_geografia with institutional indicators.",
        len(df_geo_integrated)
    )
    return df_geo_integrated


def transform_and_integrate_all(
    df_primary_raw: pd.DataFrame,
    df_api_raw: pd.DataFrame
) -> Dict[str, pd.DataFrame]:
    """Orchestrates end-to-end transformation, harmonisation and integration for both sources."""
    logger.info("Executing comprehensive transformation and integration...")

    df_primary_clean = prepare_primary_data(df_primary_raw)
    df_api_muni, df_comisarias_dir = prepare_api_data(df_api_raw)
    df_geo_integrated = integrate_geography(df_primary_clean, df_api_muni, df_comisarias_dir)

    return {
        "df_primary_clean": df_primary_clean,
        "df_geo_integrated": df_geo_integrated,
        "df_comisarias_dir": df_comisarias_dir
    }


if __name__ == "__main__":
    from extract_primary import extract_primary_data
    from extract_api import extract_api_data

    df_p, _ = extract_primary_data()
    df_a, _ = extract_api_data()
    res = transform_and_integrate_all(df_p, df_a)

    print("\n--- TRANSFORMATION SUMMARY ---")
    print("Clean primary rows:", len(res["df_primary_clean"]))
    print("Clean victims:", res["df_primary_clean"]["cantidad_victimas"].sum())
    print("Enriched municipalities:", len(res["df_geo_integrated"]))
    print("Comisarías directory entries:", len(res["df_comisarias_dir"]))
