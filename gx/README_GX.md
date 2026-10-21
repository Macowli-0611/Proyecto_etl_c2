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
| **DQ-RAW1-03** | Gate 1 (Raw Primary) | `CODIGO DANE` | Format & Length | `expect_column_value_lengths_to_be_between` | Longitud = 8 en 100% de filas | **Critical** | R2, R5, R6, R7 |
| **DQ-RAW1-04** | Gate 1 (Raw Primary) | `CANTIDAD` | Validity & Range | `expect_column_values_to_be_between` | Valor entero >= 1 para 100% | **Critical** | R1–R7 |
| **DQ-RAW1-05** | Gate 1 (Raw Primary) | `GENERO` | Completeness | `expect_column_values_to_not_be_null` | Nulos <= 1.0% | **Warning** | R3 |
| **DQ-RAW2-01** | Gate 2 (Raw API) | Esquema SODA | Completeness | `expect_table_columns_to_match_set` | Atributos faltantes = 0 | **Critical** | R6, R7 |
| **DQ-RAW2-02** | Gate 2 (Raw API) | `c_digo_dane_municipio` | Validity | `expect_column_value_lengths_to_be_between` | Longitud 4 a 5 caracteres (100%) | **Critical** | R6, R7 |
| **DQ-RAW2-03** | Gate 2 (Raw API) | `categoria_municipio` | Domain Validity | `expect_column_values_to_be_in_set` | Valores legales Ley 617 (1-6, ESP) (<= 2% fuera) | **Warning** | R7 |
| **DQ-RAW2-04** | Gate 2 (Raw API) | `existencia_de_comisarias` | Validity & Range | `expect_column_values_to_be_between` | Conteo comisarias >= 0 (100% de no nulos) | **Critical** | R6, R7 |
| **DQ-RAW2-05** | Gate 2 (Raw API) | `existencia_de_comisarias` | Completeness | `expect_column_values_to_not_be_null` | Nulos <= 10.0% (imputables a 1 comisaría física) | **Warning** | R6 |
| **DQ-PREP-01** | Gate 3 (Prepared) | Grano de la Fact | Uniqueness | `expect_compound_columns_to_be_unique` | Duplicados en grano = 0 | **Critical** | R1–R7 |
| **DQ-PREP-02** | Gate 3 (Prepared) | Foreign Keys Fact | Completeness | `expect_column_values_to_not_be_null` | Claves foráneas nulas = 0 | **Critical** | R1–R7 |
| **DQ-PREP-03** | Gate 3 (Prepared) | Integridad Referencial | Consistency | `expect_column_values_to_be_in_set` | Huérfanos Fact -> Dimensiones = 0 | **Critical** | R1–R7 |
| **DQ-PREP-04** | Gate 3 (Prepared) | `comisarias_instaladas` | Validity & Range | `expect_column_values_to_be_between` | Valores >= 0 en dim_geografia | **Critical** | R6, R7 |
| **DQ-PREP-05** | Gate 3 (Prepared) | Víctimas y Registros | Accuracy & Reconciliation | `expect_column_sum_to_be_between` | Delta víctimas = 0, Delta registros = 0 | **Critical** | Todos |
| **DQ-PREP-06** | Gate 3 (Prepared) | Cobertura Integración | Integration Coverage | `expect_column_values_to_not_be_in_set` | Municipios emparejados con API >= 98% | **Warning** | R6, R7 |

---

## 3. Justificación Analítica y Operativa de Umbrales (Sección 8.1)

| ID Regla | Umbral Material | Justificación Analítica, Contractual u Operativa |
| :---: | :--- | :--- |
| **DQ-RAW1-01** | Faltantes = 0 | Contractual: Las 8 columnas representan el esquema canónico del dataset vuyt-mqpw de la DIJIN. La ausencia de una sola columna imposibilita poblar su dimensión. |
| **DQ-RAW1-02** | Válidos = 100% | Analítica: Registros con fecha ilegible no pueden mapearse a `dim_tiempo`, violando el principio de reconciliación exacta (cero pérdida de hechos). |
| **DQ-RAW1-03** | Longitud 8 = 100% | Contractual (DIVIPOLA): Códigos de centro poblado a 8 dígitos (`DDMMMPPP`). Truncar los 5 primeros permite mapeo 1:1 a municipio. Códigos de otra longitud romperían la clave de integración. |
| **DQ-RAW1-04** | Valor >= 1 (100%) | Lógica de Negocio: La medida `CANTIDAD` representa personas agredidas en un denuncio policial; valores menores o nulos carecen de sentido físico. |
| **DQ-RAW1-05** | Nulos <= 1.0% | Tolerancia Analítica: El 0.48% histórico de valores nulos se imputa como `NO REPORTADO`. Un desvío superior a 1% sesgaría el indicador R3 (% mujeres 77.3%). |
| **DQ-RAW2-01** | Faltantes = 0 | Contractual: Los 4 atributos del endpoint SODA 7tuu-upb2 son indispensables para el join municipal y el cómputo de la brecha Ley 2126. |
| **DQ-RAW2-02** | Longitud 4-5 = 100%| Contractual (DIVIPOLA): En la API de MinJusticia, los códigos de 4 dígitos perdieron el cero inicial (p. ej. `5088` -> `05088`). Se normalizan con `zfill(5)`. Longitudes distintas representan llaves corruptas. |
| **DQ-RAW2-03** | Fuera de set <= 2%| Marco Legal (Ley 617 de 2000): Las categorías válidas son 1 a 6 y Especial (`ESP`). Errores tipográficos menores se imputan sin alterar la priorización nacional. |
| **DQ-RAW2-04** | Conteo >= 0 (100%) | Rango de Negocio: No existen comisarías negativas. Un número negativo invalidaría el denominador de R6. |
| **DQ-RAW2-05** | Nulos <= 10.0% | Operativa: Si la columna es nula pero el registro existe en el directorio, se imputa 1 comisaría sede. Un valor nulo mayor al 10% exigiría validación manual con MinJusticia. |
| **DQ-PREP-01** | Duplicados = 0 | Grano Dimensional: Unicidad estricta en `(id_tiempo, id_geografia, id_victima, id_medio)`. Todo duplicado inflaría artificialmente las víctimas. |
| **DQ-PREP-02** | Claves nulas = 0 | Integridad Relacional: En el modelo estrella de Kimball, una foreign key nula en la fact table rompe la navegabilidad de drill-down. |
| **DQ-PREP-03** | Huérfanos = 0 | Integridad Referencial: Garantiza que el 100% de las llaves en la fact existan previamente en sus respectivas dimensiones antes del comando COPY. |
| **DQ-PREP-04** | Conteo >= 0 (100%) | Validez Derivada: La columna calculada en `dim_geografia` debe mantenerse no-negativa para alimentar los dashboards de BI. |
| **DQ-PREP-05** | Delta = 0 (100%) | Reconciliación Exacta: El sistema no descarta registros en la limpieza; por ende, `SUM(fact.cantidad_victimas)` debe coincidir al centésimo con el extracto crudo (1,501,809). |
| **DQ-PREP-06** | Cobertura >= 98%| Techo Estructural: Colombia cuenta con 18 áreas no municipalizadas (corregimientos departamentales en Amazonía) sin comisarías por ley. Un cruce inferior a 98% evidenciaría desalineación de catálogos DIVIPOLA. |

---

## 4. Política de Ejecución y Severidad (Severity Enforcement)

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

## 5. Sincronización entre `gx/expectations/` y `src/validate_gx.py`

El módulo `src/validate_gx.py` carga de forma directa y sincroniza las suites desde los archivos JSON alojados en `gx/expectations/`. Cada regla evaluada extrae su metadato (`rule_id`, `severity`, `requirement`, `description`), garantizando coherencia absoluta entre las suites declarativas y la evidencia de ejecución guardada en `docs/evidence/`.
