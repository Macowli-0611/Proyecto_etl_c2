# ETL Project — Pipeline Automation, API Integration and Data Validation
## Second Delivery: From Data Engineering Baseline to an Operational Analytical System

**Academic Program:** Data Engineering and Artificial Intelligence  
**Faculty:** Engineering and Basic Sciences  
**Course:** ETL (G01) — Academic Period 2026-2  
**SDG Alignment:** SDG 5 (*Target 5.2 — Eliminate violence against women and girls*) and SDG 16 (*Target 16.1 — Reduce all forms of violence*)  
**Deliverable:** Independent Second Delivery GitHub Repository with complete orchestration, automated validation, and technical evidence.

---

## 1. Problem and Analytical Objective

### 1.1 Context and Problem Formulation
Domestic violence represents one of the most critical structural challenges in Colombia. In the First Delivery, analysis of police crime reports (Policía Nacional - DIJIN) revealed that registered victims grew from 23,171 in 2010 to 138,803 in 2025. However, crime reports alone measure only **reported volume**, which functions as a moving proxy heavily influenced by institutional presence and local reporting infrastructure rather than true underlying incidence.

The Second Delivery tackles this fundamental analytical limitation by integrating a second data source: the **National Directory and Characterization of Comisarías de Familia** (Ministerio de Justicia y del Derecho), extracted programmatically via SODA REST API. This integration bridges the gap between crime occurrence and institutional protection capacity, answering:

> *¿Cuál es la sobrecarga operativa real que enfrentan las Comisarías de Familia en Colombia frente al volumen de violencia intrafamiliar reportado, y dónde existe un déficit legal de infraestructura (Ley 2126 de 2021) que coincide críticamente con ataques letales contra menores de edad y mujeres?*

### 1.2 Engineering Objective
Evolve the Phase 1 analytical baseline into an automated, observable, and resilient data engineering system by:
1. Programmatically acquiring and profiling both primary and REST API sources.
2. Automating quality gates using **Great Expectations 1.X** for raw branches and prepared layers.
3. Formulating and answering integrated analytical requirements **R6** and **R7**.
4. Refining the dimensional Data Warehouse schema in **PostgreSQL 16**.
5. Orchestrating the end-to-end workflow with **Apache Airflow 3.X** using the TaskFlow API (`@dag`, `@task`).
6. Enforcing and proving reliability across **Test A (Successful Run)**, **Test B (Controlled Critical Failure)**, and **Test C (Safe Rerun & Idempotency)**.

---

## 2. First Delivery Baseline and Repository Link

* **Baseline Repository (Delivery 1):** [https://github.com/michaelmaccardona-lgtm/Proyecto_etl_c1](https://github.com/michaelmaccardona-lgtm/Proyecto_etl_c1)
* **Local Reference Folder:** `Proyecto_etl_C1/` (kept intact as historical evidence, with documentation consolidated in `docs_proyecto_1/`).
* **Línea Base Dimensional:** PostgreSQL star schema with 4 dimensions (`dim_tiempo`, `dim_geografia`, `dim_victima`, `dim_medio`) and transaction fact table `fact_violencia_intrafamiliar` (701,714 fact rows representing 1,501,809 victims).
* **Documented Limitation in Delivery 1:** Absence of institutional capacity and statutory population thresholds. The model measured volume, but could not identify institutional overload or legal deficits.

---

## 3. Status and Changes for Requirements R1–R5

| Requirement | Status | Change Introduced | Justification | Second Delivery Analytical Output |
| :---: | :---: | :---: | :---: | :---: |
| **R1** | **Maintained** | None (Preserved `es_periodo_completo`). | Multi-year YoY growth requires dense calendar; partial year 2026 is excluded from rate calculations. | Annual victim series (2010–2026), YoY growth rates, and quantification of the 2020 lockdown plateau (+1.93%). |
| **R2** | **Maintained** | Geography dimension enriched with institutional indicators. | National ranking and capital city concentration remain foundational to understand territorial burden. | Department/municipality rankings; verifies 63.99% concentration in departmental capitals. |
| **R3** | **Maintained** | Preserved explicit demographic cohorts and child flag. | Gender and life stage disparities underpin SDG 5.2. | Disaggregation confirming 77.33% female victims (1,161,392) and 93,986 children/adolescents. |
| **R4** | **Maintained** | Harmonized blade weapons and mechanism categories. | Lethality filtering is required to isolate lethal weapon violence. | Weapon category distribution, lethality flag, and victims-per-report ratio (2.59 for unarmed violence). |
| **R5** | **Refined** | Municipal minor lethal-weapon victims feed directly into R7 prioritisation. | Connecting lethal attacks on minors with institutional deficits provides actionable intervention targets. | Ranking of municipalities with lethal weapon attacks against minors, serving as the severity numerator for R7. |

---

## 4. New Integrated Analytical Requirements R6 and R7

| ID | Analytical Requirement | Primary-Source Data Required | API Data Required | Integration Strategy / Key | Expected KPI or Measure | Required Level of Detail |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **R6** | **Institutional Workload & Saturation per Comisaría de Familia** | `cantidad_victimas`, `numero_registros`, `codigo_dane_municipio` | `existencia_de_comisarias`, `categoria_municipio` | Equi-join on 5-digit DANE code (`codigo_dane_municipio`) | `tasa_carga_victimas_por_comisaria` = `SUM(victimas) / comisarias_instaladas`. Classification: Crítica (>2k), Alta (1k–2k), Moderada (<1k). | Municipality grain (`dim_geografia`), annual rollup. |
| **R7** | **Statutory Institutional Deficit (Ley 2126) vs Severe Child & Gender Vulnerability** | `cantidad_victimas` filtered by `es_menor_de_edad AND es_arma_letal` (R5) and `genero = 'FEMENINO'` (R3) | `comisarias_ley_2126_100_000`, `existencia_de_comisarias`, `categoria_municipio` | Multi-attribute join on `codigo_dane_municipio` with conditional prioritization logic | `brecha_comisarias` = `max(0, requeridas - instaladas)` and `indice_prioridad_intervencion` (Prioridad 1 Urgente, Prioridad 2 Alta). | Municipality and Municipal Category (Ley 617). |

---

## 5. Primary Source and API Source

### 5.1 Primary Source
* **Dataset:** Reporte Delito Violencia Intrafamiliar — Policía Nacional (DIJIN)
* **Platform:** Portal de Datos Abiertos del Estado Colombiano (`datos.gov.co`)
* **Endpoint:** `https://www.datos.gov.co/api/views/vuyt-mqpw/rows.csv?accessType=DOWNLOAD`
* **Format & Volume:** CSV, UTF-8, 65.6 MB, 704,551 records, 1,501,809 victims, 8 native attributes.
* **Extraction:** Programmatic acquisition with SHA-256 validation pinned in `data/raw/primary_source_manifest.json`.

### 5.2 API Source: Suitability and Technical Documentation (Table 4.1)

| Item | Required Documentation |
| :--- | :--- |
| **Provider and purpose** | Ministerio de Justicia y del Derecho / Presidencia de la República. Caracterización geográfica, administrativa y de infraestructura física de las Comisarías de Familia en todo el territorio nacional. |
| **Analytical value** | Complementa el reporte de delitos de la Policía Nacional con la oferta institucional instalada y la capacidad de respuesta legal (Ley 2126 de 2021), permitiendo responder R6 y R7. |
| **Endpoint and parameters** | Endpoint: `https://www.datos.gov.co/resource/7tuu-upb2.json`. Parámetros: `$limit=2000`, `$offset`, `$order=:id`. Alcance: cobertura nacional completa (1.249 registros). |
| **Response** | Formato JSON REST API. 15 atributos que caracterizan departamento, municipio, código DANE, categoría municipal, existencia de comisarías, exigencia legal de comisarías y datos de contacto. |
| **Authentication** | Endpoint público con autenticación opcional por cabecera `X-App-Token` (gestionada mediante `API_APP_TOKEN` en `.env` sin exponer credenciales). |
| **Operational behavior** | Paginación por offset/limit, timeouts configurables (30s), reintentos con retroceso exponencial ante errores HTTP 429/503 y registro del timestamp de extracción en `data/raw/api_source_manifest.json`. |
| **Reproducibility** | El evaluador puede ejecutar `python3 -c "from src.extract_api import extract_api_data; extract_api_data(force_refresh=True)"` o consultar el payload estático versionado en `data/raw/api_comisarias_raw.json` verificado con SHA-256. |

---

## 6. Analytical Value Contributed by the API

1. **Revealing Hidden Institutional Overload (R6):**
   In absolute terms, Bogotá registers the most victims (433,697) across 39 comisarías (11,120 víctimas/comisaría). However, the API reveals that intermediate cities suffer an even more extreme collapse in operational capacity:
   * **Cúcuta:** 20,389 víctimas registradas con **1 sola comisaría instalada** (20,389 víctimas/comisaría).
   * **Popayán:** 17,070 víctimas con **1 sola comisaría** (17,070 víctimas/comisaría).
   * **Bello:** 16,984 víctimas con **1 sola comisaría** (16,984 víctimas/comisaría).
   * **Floridablanca:** 10,192 víctimas con **1 sola comisaría** (10,192 víctimas/comisaría).

2. **Targeting Legal Deficit to Protect Minors and Women (R7):**
   * Under **Ley 2126 de 2021**, municipalities must have at least 1 Comisaría de Familia per 100,000 inhabitants.
   * **Cúcuta** has a statutory deficit of **8 comisarías** (requires 9, has 1) and registers **51 minors attacked with lethal weapons** (Rank 1 Urgency).
   * **Soacha** has a deficit of **6 comisarías** (requires 9, has 3) and 27 minors attacked with lethal weapons.
   * **Montería** has a deficit of **5 comisarías** (requires 6, has 1) and 41 minors attacked with lethal weapons.
   * Across Colombia, **114 comisarías de familia faltan por construir** para cumplir la ley, concentrándose el 58% del déficit en municipios de Categoría 1 y Categoría Especial.

---

## 7. System Architecture

```text
  [Primary Source]                          [API Source]
Policía Nacional DIJIN                MinJusticia Comisarías
  (704,551 records)                      (1,249 records)
          │                                      │
          ▼                                      ▼
   extract_primary                         extract_api
          │                                      │
          ▼                                      ▼
[validate_primary_raw]                  [validate_api_raw]
Great Expectations Gate 1              Great Expectations Gate 2
 (DQ-RAW1-01 to 05)                     (DQ-RAW2-01 to 04)
          │                                      │
          └──────────────────┬───────────────────┘
                             │
                             ▼
              [transform_and_clean_and_integrate]
              - DANE 5-Digit Rollup (DDMMM)
              - Weapon Harmonisation & Lethality
              - Demographic Imputation
              - Geographic Integration Contract
              - Fact Grain Aggregation (701,714 rows)
                             │
                             ▼
                    [validate_prepared]
                 Great Expectations Gate 3
               - Declared Grain Uniqueness
               - Referential Integrity (0 Orphans)
               - Exact Measure Reconciliation
                             │
                             ▼
                    [load_dimensional_dw]
                 PostgreSQL 16 Data Warehouse
               - Fast Bulk COPY Protocol
               - Foreign Key & Check Constraints
               - Semantic Views (vw_bi_hechos_completos)
                             │
                             ▼
                 [BI Analytical Dashboard]
                 Connected to PostgreSQL DW
                 Interactive R1–R7 Visualisations
```

![Architecture Diagram](docs/architecture.png)

---

## 8. Data Profiling Findings

Full profiling evidence generated automatically in [`docs/evidence/profiling_evidence.json`](docs/evidence/profiling_evidence.json) and executed in [`notebooks/profiling_and_validation.ipynb`](notebooks/profiling_and_validation.ipynb).

| Dataset or Attribute | Profiling Evidence | Potential Quality Risk | Related Requirement | Mitigation in Pipeline |
| :--- | :--- | :--- | :---: | :--- |
| **Primary:** `CODIGO DANE` | 2,397 distinct 8-digit codes reaching *centro poblado* level. | Records split across sub-municipal keys; grain dilution. | R2, R5, R6, R7 | Truncated to 5 digits (`DDMMM`); collapses 2,837 rows to municipal grain. |
| **Primary:** `CANTIDAD` | Range 1–198; 0 non-positive; 0 nulls; mean 2.13. Total: 1,501,809. | Outliers could distort averages if not treated as additive sums. | R1, R4, R6 | Reconciled at pre-load, post-transform, and post-load gates. |
| **API:** `c_digo_dane_municipio` | Text codes with length 4 (e.g. `5088`) and 5 (e.g. `11001`). 114 codes missing leading zero. | Leading zeros lost if read as integer; equi-join fails. | R6, R7 | Formatted strictly with `.str.strip().str.zfill(5)`. |
| **API:** `categoria_municipio` | Categorías 1–6, `ESP`, plus 17 null values. | Unhandled null categories in dimension drill-downs. | R7 | Standardized `ESP` → `ESPECIAL`, imputed `NO REPORTADA`. |
| **Cross-Source:** `codigo_dane_municipio` | 1,100 municipalities match (98.92% coverage). 12 primary codes and 2 API codes unmatched. | Unmatched records could drop victims or break FK constraints. | R6, R7 | Left outer join contract: non-municipalized areas get default baseline; API municipalities added to `dim_geografia`. |

---

## 9. Quality Risks and Quality Rules

| Rule ID | Layer | Attribute(s) | Quality Dimension | Quality Rule | Metric / Threshold | Severity | Related Req |
| :---: | :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| **DQ-RAW1-01** | Raw Primary | Schema / Columns | Completeness | Mandatory columns must exist in raw extract. | Missing cols = 0 | **Critical** | R1–R5 |
| **DQ-RAW1-02** | Raw Primary | `FECHA HECHO` | Validity & Format | Incident date matches `DD/MM/YYYY` format. | Parseable = 100% | **Critical** | R1 |
| **DQ-RAW1-03** | Raw Primary | `CODIGO DANE` | Format & Length | DANE code is 8-character string. | Length == 8 for >= 99.99% | **Critical** | R2, R5 |
| **DQ-RAW1-04** | Raw Primary | `CANTIDAD` | Validity & Range | Measure CANTIDAD must be positive integer >= 1. | Value >= 1 for 100% | **Critical** | R1–R5 |
| **DQ-RAW1-05** | Raw Primary | `GENERO` | Completeness | Unreported gender must not exceed 1% of extract. | Nulls <= 1.0% | **Warning** | R3 |
| **DQ-RAW2-01** | Raw API | Schema / Columns | Completeness | Mandatory API attributes present in payload. | Missing cols = 0 | **Critical** | R6, R7 |
| **DQ-RAW2-02** | Raw API | `c_digo_dane_municipio` | Validity | DANE code length between 4 and 5 characters. | Valid for 100% | **Critical** | R6, R7 |
| **DQ-RAW2-03** | Raw API | `categoria_municipio` | Domain Validity | Municipal category belongs to legal set (1–6, ESP). | Unexpected <= 2.0% | **Warning** | R7 |
| **DQ-RAW2-04** | Raw API | `existencia_de_comisarias` | Validity & Range | Verified comisarías count must be >= 0. | Value >= 0 for >= 90% | **Critical** | R6, R7 |
| **DQ-PREP-01** | Prepared | Grain Columns | Uniqueness | Declared grain uniqueness in fact table. | Duplicates = 0 | **Critical** | R1–R7 |
| **DQ-PREP-02** | Prepared | Foreign Keys | Completeness | Foreign keys must not be null in fact table. | Null FKs = 0 | **Critical** | R1–R7 |
| **DQ-PREP-03** | Prepared | Foreign Keys | Referential Integrity | All fact foreign keys exist in dimensions. | Orphan FKs = 0 | **Critical** | R1–R7 |
| **DQ-PREP-04** | Prepared | `comisarias_instaladas` | Range | Installed comisarías count non-negative. | Value >= 0 for 100% | **Critical** | R6, R7 |
| **DQ-PREP-05** | Prepared | `cantidad_victimas` | Reconciliation | Loaded victims match raw extract total exactly. | Delta = 0 | **Critical** | All |

---

## 10. Great Expectations Design and Rule Traceability

* **GX Version:** 1.24.0 (Fluent DataContext API).
* **Declarative Suite Repository:** `gx/` root directory containing:
  * `gx/expectations/primary_raw_suite.json` (Gate 1: Raw Primary Validation)
  * `gx/expectations/api_raw_suite.json` (Gate 2: Raw API Validation)
  * `gx/expectations/prepared_data_suite.json` (Gate 3: Prepared Data & Reconciliation Validation)
  * `gx/checkpoints/` and `gx/validation_definitions/` for declarative execution.
  * `gx/gx_config.yaml` and `gx/README_GX.md` with complete rule traceability matrix.
* **Implementation:** `src/validate_gx.py` loads and synchronizes suites directly with the `gx/` directory.
* **Execution Evidence:** JSON execution results saved automatically in `docs/evidence/` with timestamped and latest pointers.
* **Severity Enforcement:**
  * **Critical:** Raises `ValidationError` in Python and `AirflowFailException` in Airflow 3.1.8. Task fails with exit code 1; downstream dependencies are immediately marked `UPSTREAM_FAILED` and aborted.
  * **Warning:** Logs details, records unexpected counts/indices in JSON evidence, and allows normal pipeline continuation.

### 10.1 GX Elements and Pipeline Interpretation (Table 10)

| GX Element | What the Team Must Explain | Project Implementation |
| :--- | :--- | :--- |
| **Data object** | Which batch, table, file, or prepared representation is being validated. | Raw primary batch (`df_raw`), raw API payload (`df_api`), and prepared dimensional tables (`fact_violencia_intrafamiliar`, `dim_geografia`, `dim_tiempo`, `dim_victima`, `dim_medio`). |
| **Expectation** | Which explicit quality rule the Expectation implements and which parameters represent its metric or threshold. | Reglas `DQ-RAW1-01` a `05`, `DQ-RAW2-01` a `04` y `DQ-PREP-01` a `05` implementadas con `gxe.ExpectTableColumnsToMatchSet`, `gxe.ExpectColumnValueLengthsToBeBetween`, `gxe.ExpectColumnValuesToBeBetween`, etc. |
| **Expectation Suite** | Why the grouped checks belong to the same data object and layer. | Agrupadas en 3 suites independientes por ciclo de vida (`primary_raw_suite.json`, `api_raw_suite.json`, `prepared_data_suite.json`) para evitar acoplamiento entre fuentes. |
| **Validation Definition** | How the data definition and Expectation Suite are associated for repeatable execution. | Mapeados en `gx/validation_definitions/*.json` vinculando cada Data Asset y Batch Definition a su Expectation Suite correspondiente. |
| **Checkpoint or controlled execution** | How validation is invoked and how results become available to the pipeline. | Invocado programáticamente en `src/validate_gx.py` mediante el Fluent Context de GX 1.X y Checkpoints formales en `gx/checkpoints/*.json`. |
| **Validation result** | How success, failure, unexpected counts or percentages, and relevant examples are interpreted. | Los objetos de resultado evalúan `res.success`, `res.result['unexpected_count']` y `res.result['unexpected_percent']`. |
| **Pipeline response** | How severity and policy translate the validation result into continue, warn, stop, or another justified action. | `Critical` $\rightarrow$ Dispara `ValidationError` y `AirflowFailException` (bloquea downstream). `Warning` $\rightarrow$ Registra auditoría en JSON y permite continuar. |

---

## 11. Raw Validation Design for Both Sources

* **Primary Branch:** `extract_primary` → `validate_primary_raw`.
  Evaluates raw extract directly before any transformation touches the data.
* **API Branch:** `extract_api` → `validate_api_raw`.
  Evaluates raw SODA API JSON payload.
* **Independent Observability:** Each branch runs independently in Airflow. Failure in one raw branch halts the pipeline before transformation, avoiding partial processing.

---

## 12. Transformation Strategy and Integration Contract

### 12.1 Significant Transformations (Table 13)

| Transformation ID | Rule or Rationale | Affected Fields | Before and After Behavior | Exception Handling | Analytical or Dimensional Impact |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **TR-01** | Truncamiento de código DANE a grano municipal declarado. | `CODIGO DANE` $\rightarrow$ `codigo_dane_municipio` | Código de 8 dígitos a centro poblado $\rightarrow$ Primeros 5 dígitos (`DDMMM`). | 00000 asignado a 05001 (Medellín); 52000 a 52999. | Permite agregación exacta al grano municipal y equi-join con API. |
| **TR-02** | Estandarización de nombres canónicos y bandera de capital. | `MUNICIPIO` $\rightarrow$ `municipio`, `es_capital` | Nombres con variación y sufijo `(CT)` $\rightarrow$ Nombre modal por código DANE; `es_capital = TRUE`. | Si no tiene nombre modal se asigna `NO ESPECIFICADO`. | Elimina 64 duplicados superficiales de nombres y apoya R2. |
| **TR-03** | Armonización de armas y derivación de letalidad. | `ARMAS MEDIOS` $\rightarrow$ `medio_agresion`, `es_arma_letal` | 4 categorías cortopunzantes $\rightarrow$ `ARMA BLANCA`; flag letal en fuego/blanca. | Armas no catalogadas van a `OTROS`. | Clasificación homogénea para análisis de letalidad en R4, R5 y R7. |
| **TR-04** | Imputación explícita de variables demográficas. | `GENERO`, `GRUPO ETARIO` | Valores nulos $\rightarrow$ `NO REPORTADO`; derivación `es_menor_de_edad`. | Imputación sin descartar registros (0 víctimas eliminadas). | Preserva 100% de víctimas (1.501.809) para auditoría exacta. |

### 12.2 Integration Contract (Table 13.1)

| Contract Element | Required Decision and Evidence |
| :--- | :--- |
| **Integration key or keys** | Código DANE municipal de 5 dígitos (`codigo_dane_municipio`). |
| **Cardinality** | 1:1 a nivel municipal (directorio de 1.249 comisarías agregado a 1.113 municipios consolidados). |
| **Preprocessing** | `.str.strip().str.zfill(5)` aplicado a ambas fuentes para evitar pérdida de ceros a la izquierda. |
| **Temporal alignment** | Datos acumulados DIJIN (2010–2026) integrados con directorio institucional vigente (2026). |
| **Unmatched records** | 11 áreas no municipalizadas reciben valores por defecto (`comisarias_instaladas=0`, `brecha=1`); 0 víctimas descartadas. |
| **Duplicate or ambiguous matches** | Múltiples comisarías en un mismo municipio se agrupan en suma agregada en `dim_geografia` y se conservan individualmente en `dim_comisaria`. |
| **Assumptions** | Requerimiento de Ley 2126 asume escalones de 1 comisaría por cada 100.000 habitantes. |
| **Limitations** | Los datos reflejan denuncias ante Policía Nacional; no capturan la cifra negra no denunciada. |

---

## 13. Refined Dimensional Model and Change Justification

![Star Schema](docs/star_schema.png)

### 13.1 Changes from Delivery 1
1. **`dim_geografia` Enriched:** Added attributes `categoria_municipio`, `comisarias_instaladas`, `comisarias_requeridas_ley`, `brecha_comisarias`, and `tiene_comisaria`.
   * *Justification:* Supports R6 and R7 directly through star schema joins without requiring changes to the fact table grain or creating snowflake complexity.
2. **`dim_comisaria` Added (Outrigger):** Contains 1,247 physical comisarías with name, address, telephone, schedule, and category.
   * *Justification:* Supports operational drill-downs and geospatial mapping while keeping `dim_geografia` at the municipal grain.
3. **`fact_violencia_intrafamiliar` Preserved:** Declared municipal grain `(id_tiempo, id_geografia, id_victima, id_medio)` strictly preserved with unique constraint `uq_fact_grano`.

### 13.2 Dimensional Model Review (Table 12)

| Model Element | Required Review |
| :--- | :--- |
| **Business process** | Registro de hechos delictivos de violencia intrafamiliar y oferta de protección institucional de comisarías. |
| **Fact-table grain** | Una fila por combinación única de evento espacio-temporal y perfil: `(id_tiempo, id_geografia, id_victima, id_medio)`. |
| **Fact table or tables** | `fact_violencia_intrafamiliar` (701.714 filas; 1.501.809 víctimas). Mantiene el grano municipal intacto. |
| **Dimensions** | `dim_tiempo` (fechas y calendario denso), `dim_geografia` (enriquecida con indicadores de comisarías), `dim_victima` (género, grupo etario), `dim_medio` (mecanismo y letalidad), `dim_comisaria` (outrigger con directorio físico). |
| **Measures** | `cantidad_victimas` (suma aditiva), `numero_registros` (conteo de denuncias policiales base). |
| **Keys and relationships** | PKs surrogadas enteros seriales; FKs indexadas en la Fact table; restricción de unicidad declarada `uq_fact_grano`. |
| **Requirement coverage** | R1 (tiempo), R2 (geografía), R3 (víctimas/demografía), R4 (mecanismos), R5 (menores y letalidad), R6 (sobrecarga operativa), R7 (déficit legal Ley 2126). |

---

## 14. Prepared Data Validation

Executed at **Gate 3 (`validate_prepared`)** prior to Data Warehouse loading:
1. Uniqueness of grain combination `(id_tiempo, id_geografia, id_victima, id_medio)`.
2. Zero null foreign keys in the fact table.
3. Referential integrity: Fact FKs verified against PKs of all 4 dimensions.
4. Exact measure reconciliation against source extract manifests.

---

## 15. Data Warehouse Implementation and Load

* **Engine:** PostgreSQL 16 Alpine running in Docker container `etl_c2_postgres_dw`.
* **DDL Definition:** `sql/create_dw.sql`.
* **Loading Mechanism:** Fast streaming bulk COPY via `psycopg2.copy_expert` with CSV formatting and quote escaping.
* **Load Performance:** 701,714 fact rows loaded in **16.8 seconds**.
* **Automated Reconciliation Report (`docs/evidence/reconciliation_report.json`):**
  * Expected Source Records: 704,551 | Loaded: 704,551 | Delta: **0**
  * Expected Source Victims: 1,501,809 | Loaded: 1,501,809 | Delta: **0**
  * Orphan Foreign Keys: **0**
  * Exact Reconciliation Pass: **TRUE**

---

## 16. Airflow DAG Design and Task Interfaces
 
* **DAG File:** `dags/etl_violencia_intrafamiliar_dag.py`.
* **Authoring Interface:** Apache Airflow 3.1.8 Task SDK (`from airflow.sdk import dag, task`).
* **Task Interfaces (No Bulk XCom):**
  * Tasks pass small JSON dictionaries containing file paths, checksums, and record counts.
  * Extracted and prepared datasets are persisted on disk (`data/raw/*.csv`, `data/processed/*.parquet`).
* **Task Sequence:**
  `extract_primary` → `validate_primary_raw`  
  `extract_api` → `validate_api_raw`  
  Convergence: `transform_and_clean_and_integrate` → `validate_prepared` → `load_dimensional_dw`.

### 16.1 Task Interfaces Contract (Table 17)

| Interface Concern | Required Decision and Evidence |
| :--- | :--- |
| **Input contract** | Referencias compactas pasadas por argumentos TaskFlow (rutas en `data/raw/*.csv` o `data/processed/*.parquet`, hashes y conteos esperados). |
| **Output contract** | Diccionarios ligeros con metadatos del lote (`gate`, `passed`, `critical_failure`, `total_records`, rutas de persistencia). Nunca DataFrames por XCom. |
| **Batch identity** | Identificado unívocamente mediante la ruta del archivo fuente, timestamp ISO de extracción y hash criptográfico SHA-256 en los manifiestos. |
| **Failure signal** | Violaciones críticas lanzan `AirflowFailException`, marcando la tarea como `FAILED` con `retries=0` e interrumpiendo aguas abajo. |
| **Rerun behavior** | Idempotente: recarga atómica protegida por DDL transaccional y restricción `UNIQUE` en el grano (`uq_fact_grano`). Cero duplicados silenciosos. |

---

## 17. Failure and Selective Retry Policies

Generic DAG-wide retries (`retries=3`) are strictly prohibited by the rubric. Each task defines an explicit, justified policy:

| Failure Class | Example / Root Cause | Task / Scope | Selective Retry Configuration | Engineering Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Transient Operational I/O** | Temporary file locks, I/O latency | `extract_primary` | `retries=2, retry_delay=timedelta(minutes=1)` | Temporary disk or file lock contention typically clears within a short wait. |
| **Transient External API** | SODA API timeouts, HTTP 429 rate limits | `extract_api` | `retries=3, retry_delay=timedelta(minutes=2)` | Remote endpoints and rate limits recover after backoff without human intervention. |
| **Transient Database Connection** | PostgreSQL connection pool saturation | `load_dimensional_dw` | `retries=2, retry_delay=timedelta(minutes=1)` | Temporary DB connection pool exhaustion resolves once active transactions complete. |
| **Deterministic Data Quality / Contract** | Missing mandatory columns, invalid DANE lengths | `validate_primary_raw`, `validate_api_raw` | `retries=0` (Fail Fast) | Rerunning validation against unchanged payload reproduces the exact failure. Fail immediately. |
| **Deterministic Integration Logic** | Business logic, schema mismatch | `transform_and_clean_and_integrate` | `retries=0` (Fail Fast) | Deterministic transformation errors cannot self-heal. Immediate halt preserves pipeline integrity. |
| **Deterministic Dimensional Quality** | Grain duplicates, orphan FKs, reconciliation delta | `validate_prepared` | `retries=0` (Fail Fast) | Invariant violations require data engineering review before touching the Data Warehouse. |

---

## 18. Successful-Run Evidence (Test A)

* **Evidence File:** [`docs/evidence/test_a_successful_run.json`](docs/evidence/test_a_successful_run.json).
* **Total Execution Duration:** 19.63 seconds.
* **Audit Summary:**
  * `extract_primary`: 704,551 rows extracted.
  * `validate_primary_raw`: Gate 1 passed (0 critical errors).
  * `extract_api`: 1,249 entries retrieved from SODA REST API.
  * `validate_api_raw`: Gate 2 passed (0 critical errors).
  * `transform_and_clean_and_integrate`: 701,714 fact rows constructed.
  * `validate_prepared`: Gate 3 passed (100% referential integrity, 0 grain duplicates).
  * `load_dimensional_dw`: Loaded into PostgreSQL; 1,501,809 victims verified.

---

## 19. Controlled-Failure Evidence (Test B)

* **Evidence File:** [`docs/evidence/test_b_controlled_failure.json`](docs/evidence/test_b_controlled_failure.json).
* **Controlled Condition Injected:** Dropped mandatory column `existencia_de_comisarias` from incoming API payload.
* **Observed Pipeline Behavior:**
  1. `extract_primary` and `extract_api` completed.
  2. `validate_api_raw` detected Critical violation of rule **DQ-RAW2-01** (Schema Completeness) and failed with `ValidationError`.
  3. Downstream tasks `transform_and_clean_and_integrate`, `validate_prepared`, and `load_dimensional_dw` were marked **`BLOCKED (UPSTREAM_FAILED)`** and never executed.
  4. The PostgreSQL Data Warehouse remained completely protected from corrupted data.

### 19.1 Logging and Observability Operational Evidence (Table 19)

| Operational Question | Expected Evidence | Project Implementation / Location |
| :--- | :--- | :--- |
| **What ran?** | DAG Run, Task Instance, source or branch, and relevant operation. | Airflow DAG `etl_violencia_intrafamiliar_segunda_entrega` y logs de tarea en TaskFlow. |
| **When did it run?** | Logical or run date and material start and completion timestamps. | Timestamps ISO registrados en `docs/evidence/*.json` y en Task Instance execution context. |
| **Which batch or source?** | Batch identifier, extraction timestamp, path, table, or compact source reference. | Manifiestos `primary_source_manifest.json` y `api_source_manifest.json` con hash SHA-256. |
| **How many records were processed?** | Relevant extracted, accepted, rejected, matched, or loaded counts. | Primaria: 704.551 extraídos / Fact: 701.714 cargados / Víctimas: 1.501.809 reconciliadas al 100%. |
| **Did validation pass?** | Overall and relevant rule-level GX outcomes. | Reportes de auditoría en `docs/evidence/gx_validation_*_latest.json`. |
| **Where and why did failure occur?** | Failed task state and actionable log or validation evidence. | Registrado en `test_b_controlled_failure.json` mostrando fallo en `validate_api_raw` por regla `DQ-RAW2-01`. |
| **What happened next?** | Retry, blocked dependency, warning continuation, recovery, or other policy response. | Downstream dependientes marcadas inmediatamente como `BLOCKED (UPSTREAM_FAILED)`. |

---

## 20. Repeatability and Safe-Rerun Strategy (Test C)

* **Evidence File:** [`docs/evidence/test_c_safe_rerun.json`](docs/evidence/test_c_safe_rerun.json).
* **Idempotency Strategy:** Atomic transactional DDL re-creation and bulk COPY guarded by `CONSTRAINT uq_fact_grano UNIQUE (id_tiempo, id_geografia, id_victima, id_medio)`.
* **Before & After Rerun Comparison:**
  * Fact Rows Before: 701,714 | After: 701,714 | Delta: **0**
  * Total Victims Before: 1,501,809 | After: 1,501,809 | Delta: **0**
  * Total Source Records Before: 704,551 | After: 704,551 | Delta: **0**
  * Silent Duplicates Detected: **FALSE** (100% Idempotent).

---

## 21. Dashboard and Analytical Outputs (Power BI)

La capa de Business Intelligence y visualización analítica se desarrolla en **Microsoft Power BI Desktop**, conectándose de forma directa y en tiempo real al Data Warehouse en PostgreSQL.

### 21.1 Parámetros de Conexión en Power BI Desktop

Para conectar Power BI al Data Warehouse:
1. En Power BI Desktop, seleccione **Obtener datos (Get Data) $\rightarrow$ Base de datos PostgreSQL**.
2. Configure los parámetros de conexión:
   * **Servidor:** `localhost:5432`
   * **Base de datos:** `etl_dw`
   * **Modo de conectividad:** `Import` o `DirectQuery`
3. Ingrese las credenciales de acceso:
   * **Usuario:** `postgres`
   * **Contraseña:** `postgres123`

### 21.2 Vistas Analíticas Disponibles para Power BI

El pipeline ETL ejecuta automáticamente el script `sql/bi_views.sql`, exponiendo vistas relacionales ya calculadas y optimizadas para visualización:

| Vista SQL | Requisito Analítico | Descripción y KPIs |
| :--- | :---: | :--- |
| `vw_r1_tendencia_anual` | **R1** | Evolución temporal anual (2010–2026), crecimiento interanual YoY y filtro de año completo. |
| `vw_r2_concentracion_geografica` | **R2** | Ranking departamental y municipal; participación porcentual y concentración en capitales. |
| `vw_r3_caracterizacion_victimas` | **R3** | Caracterización demográfica por género (mujeres 77.3%), grupo etario y flag de menores de edad. |
| `vw_r4_mecanismos_letalidad` | **R4** | Distribución de medios y armas; ratio de víctimas por reporte e indicador de letalidad. |
| `vw_r6_sobrecarga_comisarias` | **R6** | Tasa de carga operativa (víctimas/comisaría) y clasificación de sobrecarga crítica (>2.000). |
| `vw_r7_prioridad_intervencion` | **R7** | Matriz de priorización (Déficit Ley 2126 vs. ataques letales a menores y violencia de género). |

### 21.3 Business Intelligence Analytical Product (Table 21)

| Requirement | DW Element or Query | KPI or Visualization | Integration Value Demonstrated |
| :---: | :--- | :--- | :--- |
| **R6** | `dim_geografia.comisarias_instaladas`, `fact.cantidad_victimas` | Tasa de víctimas por comisaría instalada (Gráfico de barras de sobrecarga crítica). | Revela saturación extrema oculta en ciudades intermedias (Cúcuta con 20.389 víctimas por comisaría). |
| **R7** | `dim_geografia.brecha_comisarias`, `dim_geografia.categoria_municipio`, filtros R3 y R5 | Matriz de Intervención Prioritaria: Déficit legal (Ley 2126) vs Agresiones letales a menores (Gráfico de dispersión y priorización). | Identifica y jerarquiza los 114 municipios en incumplimiento legal donde además hay riesgo letal contra niños y niñas. |

---

## 22. Requirement-to-KPI and End-to-End Traceability Matrix (Table 6)

**Required reasoning chain:**  
`Analytical Requirement → Required Data → Source → Profiling Evidence → Quality Risk → Quality Dimension → Quality Rule → Metric and Threshold → Severity → GX Expectation → Validation Result → Pipeline Action → Transformation and Integration → DW Element → KPI or Visualization`

| Requirement | Primary Attribute | API Attribute | Profiling Finding | Quality Rule | GX Check | Transformation / Integration | DW Target | Final KPI / Visualisation |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **R1** | `FECHA HECHO`, `CANTIDAD` | N/A | Dense daily series (6,056 days); 2026 partial. | DQ-RAW1-02, DQ-RAW1-04 | `ExpectColumnValuesToMatchRegex` | ISO date parse; derive `es_periodo_completo`. | `dim_tiempo.anio`, `fact.cantidad_victimas` | Serie anual y tasa de crecimiento YoY excluyendo 2026. |
| **R2** | `CODIGO DANE`, `MUNICIPIO` | N/A | 2,397 sub-municipal codes; 64 duplicate names. | DQ-RAW1-03 | `ExpectColumnValueLengthsToBeBetween` | Rollup to 5 digits (`DDMMM`); strip `(CT)` into `es_capital`. | `dim_geografia.es_capital` | Ranking departamental y % de concentración en capitales. |
| **R3** | `GENERO`, `GRUPO ETARIO` | N/A | Nulls in gender (0.48%) and age group (0.20%). | DQ-RAW1-05 | `ExpectColumnValuesToNotBeNull(mostly=0.99)` | Impute `NO REPORTADO`; derive `es_menor_de_edad`. | `dim_victima.perfil_demografico` | Distribución de víctimas por cohorte y proporción de mujeres. |
| **R4** | `ARMAS MEDIOS`, `CANTIDAD` | N/A | 4 blade weapon labels; unarmed violence highest volume. | DQ-RAW1-04 | `ExpectColumnValuesToBeBetween(min=1)` | Harmonise labels; derive `categoria_mecanismo`. | `dim_medio.categoria_mecanismo` | Proporción por mecanismo y ratio víctimas por denuncia. |
| **R5** | `CODIGO DANE`, `ARMAS MEDIOS` | N/A | 3,035 minors attacked with lethal weapons. | DQ-RAW1-03, DQ-RAW1-04 | Grain check | Combine minor flag and lethality filter. | `fact` joined with `dim_victima` and `dim_medio` | Hotspots municipales de agresiones letales contra menores. |
| **R6** | `CANTIDAD`, `CODIGO DANE` | `existencia_de_comisarias` | Codes with 4-5 digits; 1,102 distinct municipalities. | DQ-RAW2-02, DQ-RAW2-04 | `ExpectColumnValueLengthsToBeBetween` | Zero-pad DANE to 5 digits; aggregate installed count. | `dim_geografia.comisarias_instaladas` | **Tasa de víctimas por comisaría instalada (Ranking sobrecarga)**. |
| **R7** | `CANTIDAD` (R3, R5 filters) | `comisarias_ley_2126`, `categoria_municipio` | Deficit in 114 municipalities; concentrated in Cat 1/ESP. | DQ-RAW2-01, DQ-PREP-04 | `ExpectTableColumnsToMatchSet` | Calculate `max(0, req - inst)`; derive priority index. | `dim_geografia.brecha_comisarias` | **Matriz de Intervención Urgente (Déficit Legal vs Letalidad Menores)**. |

---

## 23. Setup and Execution Instructions

### 23.1 Prerequisites
* **Docker & Docker Compose** (Docker Desktop activo).
* **Python 3.10+** y gestor `pip`.

### 23.2 Step-by-Step Execution

#### 1. Configure Environment and Infrastructure
* **En Windows (PowerShell):**
  ```powershell
  copy .env.example .env
  docker compose up -d
  ```
* **En Linux / macOS:**
  ```bash
  cp .env.example .env
  docker compose up -d
  ```

#### 2. Virtual Environment and Python Dependencies
* **En Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```
* **En Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

#### 3. Execute Pipeline and Reliability Tests (Two Options)

* **Option A — Automated CLI Runner (Recommended for fast grading):**
  Ejecuta consecutivamente **Test A**, **Test B** y **Test C**, validando compuertas Great Expectations y generando las evidencias en `docs/evidence/`:
  ```powershell
  # En Windows:
  python src/run_pipeline.py

  # En Linux / macOS:
  python3 src/run_pipeline.py
  ```

* **Option B — Apache Airflow 3.1.8 Web UI (Interactive Orchestration):**
  1. Ingrese desde su navegador a: **`http://localhost:8080`**
  2. Inicie sesión: **Username:** `admin` | **Password:** `admin`
  3. Seleccione el DAG: `etl_violencia_intrafamiliar_segunda_entrega`.
  4. Haga clic en **Trigger (▶️) $\rightarrow$ Opciones Avanzadas** y seleccione en el menú `test_mode`:
     - **`TEST_A_SUCCESSFUL_RUN`**: Ejecución completa exitosa de punta a punta (todas las tareas en **VERDE**).
     - **`TEST_B_CONTROLLED_FAILURE`**: Simulación de falla crítica en fuente primaria (Compuerta 1 en **ROJO** y downstream bloqueado en **NARANJA**).
     - **`TEST_C_SAFE_RERUN`**: Re-ejecución sobre la base de datos existente demostrando **idempotencia total** (0 registros y 0 víctimas duplicadas).

#### 4. Verify Data Warehouse with Analytical Queries
```bash
# Ejecutar todas las consultas analíticas de R1 a R7
docker compose exec postgres_dw psql -U postgres -d etl_dw -f /sql/analytical_queries.sql

# Consulta rápida de conciliación (Esperado: 701.714 hechos | 1.501.809 víctimas | 704.551 reportes)
docker compose exec postgres_dw psql -U postgres -d etl_dw -c "SELECT COUNT(*) AS total_hechos, SUM(cantidad_victimas) AS total_victimas, SUM(numero_registros) AS total_reportes FROM fact_violencia_intrafamiliar;"
```

#### 5. Solución de Problemas Frecuentes (Troubleshooting)
* **Puerto 5432 u 8080 ocupado:** Modifique `DB_PORT=5433` en `.env` y `docker-compose.yaml`.
* **Reinicio limpio de contenedores:** Ejecute `docker compose down -v` y luego `docker compose up -d`.
* **Conectividad con la API:** Si la red externa falla, el sistema utiliza automáticamente la caché local de `data/raw/api_comisarias_raw.json` para garantizar reproducibilidad sin cortes.

### 23.3 Comandos de Gestión y Operación de Airflow

| Acción | Comando (Windows PowerShell / Bash) | Descripción |
| :--- | :--- | :--- |
| **Prender Airflow (y Base de Datos)** | `docker compose up -d` | Inicia Airflow y PostgreSQL en segundo plano (Web UI lista en `http://localhost:8080`). |
| **Apagar todo en general** | `docker compose down` | Detiene y remueve todos los contenedores, liberando los puertos 8080 y 5432. |
| **Ver si está activo** | `docker compose ps` | Muestra el estado del contenedor (`Up`) y el puerto activo (`8080`). |
| **Ver si el DAG está pausado** | `docker compose exec airflow airflow dags list` | Lista los DAGs y confirma si `is_paused` es `False` (activo) o `True`. |
| **Despausar el DAG** | `docker compose exec airflow airflow dags unpause etl_violencia_intrafamiliar_segunda_entrega` | Activa el DAG para que responda a ejecuciones manuales o programadas. |
| **Pausar el DAG** | `docker compose exec airflow airflow dags pause etl_violencia_intrafamiliar_segunda_entrega` | Pausa el DAG para evitar ejecuciones automáticas. |
| **Ver historial de ejecuciones** | `docker compose exec airflow airflow dags list-runs -d etl_violencia_intrafamiliar_segunda_entrega` | Muestra la lista de ejecuciones pasadas, fecha y estado (`success`/`failed`). |
| **Limpiar historial / Reset** | `docker compose exec airflow airflow db reset -y` | Reinicia la base de metadatos de Airflow, limpiando logs y ejecuciones anteriores. |

### 23.4 Quick Reference Table

| Action | Windows (PowerShell / CMD) | Linux / macOS |
| :--- | :--- | :--- |
| **1. Environment** | `copy .env.example .env` | `cp .env.example .env` |
| **2. Infrastructure** | `docker compose up -d` | `docker compose up -d` |
| **3. Virtual Env** | `python -m venv .venv` y `.\.venv\Scripts\Activate.ps1` | `python3 -m venv .venv` y `source .venv/bin/activate` |
| **4. Dependencies** | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| **5. Run Pipeline** | `python src/run_pipeline.py` | `python3 src/run_pipeline.py` |
| **6. Airflow UI** | Abrir `http://localhost:8080` (`admin`/`admin`) | Abrir `http://localhost:8080` (`admin`/`admin`) |
| **7. Verify Queries** | `docker compose exec postgres_dw psql -U postgres -d etl_dw -f /sql/analytical_queries.sql` | `docker compose exec postgres_dw psql -U postgres -d etl_dw -f /sql/analytical_queries.sql` |
| **8. Stop Services** | `docker compose down` | `docker compose down` |

---

## 24. Assumptions and Limitations

1. **Denuncias Policiales vs Incidencia:** Los datos reflejan violencia intrafamiliar registrada por la Policía Nacional. Los cambios históricos también reflejan variaciones en la propensión y capacidad institucional de denuncia.
2. **Corte Temporal Parcial:** El extracto finaliza el 31 de julio de 2026; comparaciones anuales deben filtrar `es_periodo_completo = TRUE`.
3. **Población en Ley 2126:** La exigencia legal de comisarías reportada por el Ministerio de Justicia asume escalones de 100.000 habitantes.
4. **Áreas No Municipalizadas:** 11 corregimientos departamentales en la Amazonía no disponen de administración municipal bajo Ley 617; fueron imputados con valores por defecto documentados para no descartar víctimas.
5. **Idempotencia:** La recarga atómica reconstruye las estructuras asegurando cero duplicados sin pérdida de trazabilidad.

---

## 25. Team Members and Responsibilities

* **Course:** ETL (G01) — Academic Period 2026-2
* **Delivery 2 Repository:** [https://github.com/Macowli-0611/Proyecto_etl_c2](https://github.com/Macowli-0611/Proyecto_etl_c2)

| Team Member | Core Responsibilities in Second Delivery |
| :--- | :--- |
| **Michael Macowli Cardona Rodríguez** | Formulation of R6 and R7; Apache Airflow DAG design; integration contract; repository architecture and end-to-end orchestration. |
| **Sebastián Manrique Mejía** | SODA REST API extraction; cross-source profiling; Great Expectations validation suites (Gate 1, Gate 2, Gate 3). |
| **David Hernández Paz** | Dimensional model refinement (`dim_geografia` enrichment, `dim_comisaria`); PostgreSQL 16 DDL; bulk load and automated reconciliation. |
| **Sebastián Torres Pantoja** | Business Intelligence semantic layer; analytical SQL queries for R1–R7; Power BI dashboard integration and reliability testing. |

---

## 26. Minimum Evidence Set and Submission Verification (Rubric Sections 25 & 29)

- [x] **R1–R5 status and refined analytical requirements** (Sección 3 documentada con justificación analítica).
- [x] **Completed R6–R7 integrated-requirements matrix** (Sección 4 con atributos, claves, métricas y detalle).
- [x] **Architecture diagram** (Sección 7 y archivo generado en `docs/architecture.png`).
- [x] **Profiling evidence for both sources** (Sección 8 y evidencia JSON en `docs/evidence/profiling_evidence.json`).
- [x] **Quality risks and completed quality-rule table** (Sección 9 con las 14 reglas documentadas).
- [x] **Programmatic API extraction evidence** (Sección 5.2, código en `src/extract_api.py` y manifiesto en `data/raw/api_source_manifest.json`).
- [x] **Great Expectations raw-validation evidence for both branches** (Sección 10, suites en `gx/expectations/` y resultados en `docs/evidence/`).
- [x] **Transformation and integration evidence, including integration contract** (Sección 12 con Tabla 13 y Tabla 13.1).
- [x] **Refined dimensional model and Data Warehouse scripts** (Sección 13, DDL en `sql/create_dw.sql` y diagrama en `docs/star_schema.png`).
- [x] **Prepared-data validation evidence** (Sección 14 y `docs/evidence/gx_validation_prepared_latest.json`).
- [x] **Airflow DAG and successful-run evidence** (Sección 16, DAG en `dags/etl_violencia_intrafamiliar_dag.py` y evidencia de Test A).
- [x] **Controlled-failure evidence and failed-task logs** (Sección 19 y `docs/evidence/test_b_controlled_failure.json`).
- [x] **Retry-policy evidence or justified no-retry decisions** (Sección 17 con política selectiva y justificación técnica).
- [x] **Safe-rerun evidence and before-and-after comparison** (Sección 20 y `docs/evidence/test_c_safe_rerun.json`).
- [x] **Dashboard evidence and requirement-to-KPI traceability** (Sección 21 con vistas semánticas en `sql/bi_views.sql`, capa analítica en Power BI y Tabla 21).
- [x] **Final end-to-end traceability matrix** (Sección 22 con cadena de razonamiento completa).
