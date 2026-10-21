# Arquitectura y Manifiesto de Calidad de Datos - Great Expectations (`gx/`)

Este directorio contiene la infraestructura declarativa de validación de calidad de datos con **Great Expectations 1.X** para el proyecto de integración de Violencia Intrafamiliar (Policía Nacional - DIJIN) y Comisarías de Familia (Ministerio de Justicia).

---

## 1. Estructura del Directorio `gx/`

```text
gx/
├── gx_config.yaml                  # Configuración y manifiesto global de compuertas y reglas
├── README_GX.md                    # Documentación técnica y matriz de trazabilidad (este archivo)
├── expectations/                   # Expectation Suites formales en formato JSON
│   ├── primary_raw_suite.json      # Compuerta 1: Validación cruda de fuente primaria (DIJIN)
│   ├── api_raw_suite.json          # Compuerta 2: Validación cruda de API (MinJusticia)
│   └── prepared_data_suite.json    # Compuerta 3: Validación dimensional y de reconciliación
├── checkpoints/                    # Definiciones de Checkpoints reutilizables
│   ├── checkpoint_primary_raw.json
│   ├── checkpoint_api_raw.json
│   └── checkpoint_prepared_data.json
└── validation_definitions/         # Mapeos de Batch Definition a Expectation Suite
    ├── val_primary_raw.json
    ├── val_api_raw.json
    └── val_prepared_data.json
```

---

## 2. Matriz de Trazabilidad de Reglas de Calidad (Traceability Matrix)

Todas las expectativas definidas en los archivos JSON de `gx/expectations/` y ejecutadas mediante `src/validate_gx.py` mantienen trazabilidad estricta hacia las dimensiones de calidad, severidad y requerimientos analíticos del proyecto:

| ID Regla | Compuerta / Capa | Atributo / Objetivo | Dimensión | Expectation Type | Métrica / Umbral | Severidad | Requerimiento |
| :---: | :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| **DQ-RAW1-01** | Gate 1 (Raw Primary) | Columnas requeridas | Completeness | `expect_table_columns_to_match_set` | Columnas faltantes = 0 | **Critical** | R1–R5 |
| **DQ-RAW1-02** | Gate 1 (Raw Primary) | `FECHA HECHO` | Validity & Format | `expect_column_values_to_match_regex` | Formato DD/MM/YYYY = 100% | **Critical** | R1 |
| **DQ-RAW1-03** | Gate 1 (Raw Primary) | `CODIGO DANE` | Format & Length | `expect_column_value_lengths_to_be_between` | Longitud = 8 en >= 99.99% | **Critical** | R2, R5 |
| **DQ-RAW1-04** | Gate 1 (Raw Primary) | `CANTIDAD` | Validity & Range | `expect_column_values_to_be_between` | Valor entero >= 1 para 100% | **Critical** | R1–R5 |
| **DQ-RAW1-05** | Gate 1 (Raw Primary) | `GENERO` | Completeness | `expect_column_values_to_not_be_null` | Nulos <= 1.0% | **Warning** | R3 |
| **DQ-RAW2-01** | Gate 2 (Raw API) | Esquema SODA | Completeness | `expect_table_columns_to_match_set` | Atributos faltantes = 0 | **Critical** | R6, R7 |
| **DQ-RAW2-02** | Gate 2 (Raw API) | `c_digo_dane_municipio` | Validity | `expect_column_value_lengths_to_be_between` | Longitud 4 a 5 caracteres (>= 99%) | **Critical** | R6, R7 |
| **DQ-RAW2-03** | Gate 2 (Raw API) | `categoria_municipio` | Domain Validity | `expect_column_values_to_be_in_set` | Valores legales (1-6, ESP) (<= 2% fuera) | **Warning** | R7 |
| **DQ-RAW2-04** | Gate 2 (Raw API) | `existencia_de_comisarias` | Validity & Range | `expect_column_values_to_be_between` | Conteo comisarias >= 0 (>= 90%) | **Critical** | R6, R7 |
| **DQ-PREP-01** | Gate 3 (Prepared) | Grano de la Fact | Uniqueness | `expect_compound_columns_to_be_unique` | Duplicados en grano = 0 | **Critical** | R1–R7 |
| **DQ-PREP-02** | Gate 3 (Prepared) | Foreign Keys Fact | Completeness | `expect_column_values_to_not_be_null` | Claves foráneas nulas = 0 | **Critical** | R1–R7 |
| **DQ-PREP-03** | Gate 3 (Prepared) | Integridad Referencial | Consistency | `expect_table_foreign_keys_to_exist_in_dimensions` | Huérfanos Fact -> Dimensiones = 0 | **Critical** | R1–R7 |
| **DQ-PREP-04** | Gate 3 (Prepared) | `comisarias_instaladas` | Validity & Range | `expect_column_values_to_be_between` | Valores >= 0 en dim_geografia | **Critical** | R6, R7 |
| **DQ-PREP-05** | Gate 3 (Prepared) | Víctimas y Registros | Accuracy & Reconciliation | `expect_table_reconciliation_totals_to_match` | Delta víctimas = 0, Delta filas = 0 | **Critical** | Todos |

---

## 3. Política de Ejecución y Severidad (Severity Enforcement)

1. **Severidad Crítica (`Critical`):**
   - Viola un invariante estructural, de contrato o de integridad referencial.
   - En `src/validate_gx.py` dispara `ValidationError`.
   - En Airflow 3.1.8 (`dags/etl_violencia_intrafamiliar_dag.py`) dispara `AirflowFailException`, marcando la tarea como `FAILED` con `retries=0` e interrumpiendo de inmediato la ejecución de tareas aguas abajo (las cuales pasan a `UPSTREAM_FAILED`).
   - Evita la contaminación de la capa analítica y del Data Warehouse PostgreSQL.

2. **Severidad Advertencia (`Warning`):**
   - Identifica desvíos tolerables o atributos opcionales (p. ej. completitud de género no reportado <= 1% o categorías municipales no estándar).
   - Registra el hallazgo en el log de auditoría (`docs/evidence/gx_validation_*_latest.json`) con conteos e índices de filas inesperadas.
   - Permite que el pipeline continúe con la fase de imputación/limpieza controlada.

---

## 4. Sincronización entre `gx/expectations/` y `src/validate_gx.py`

El módulo `src/validate_gx.py` carga de forma directa y sincroniza las suites desde los archivos JSON alojados en `gx/expectations/`. Cada regla evaluada extrae su metadato (`rule_id`, `severity`, `requirement`, `description`), garantizando coherencia absoluta entre las suites declarativas y la evidencia de ejecución guardada en `docs/evidence/`.
