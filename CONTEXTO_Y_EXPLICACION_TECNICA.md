# Contexto del Proyecto, Arquitectura y Explicación Técnica Integral
## Segunda Entrega: Automatización de Pipeline, Integración de API y Validación de Datos
### Maestría / Pregrado en Ingeniería de Datos e Inteligencia Artificial — Asignatura ETL (G01)

---

## 1. Resumen Ejecutivo y Contexto del Problema

### 1.1 El Problema Colombiano de Violencia Intrafamiliar
La violencia intrafamiliar constituye una de las crisis estructurales de derechos humanos y salud pública más severas en Colombia. A través del análisis histórico de los registros de la Policía Nacional (DIJIN), se constata que los registros pasaron de **23.171 víctimas en 2010 a 138.803 en 2025**, lo que representa un **incremento acumulado de 6 veces (500% de crecimiento)** en 16 años de serie histórica.

El fenómeno está atravesado por tres asimetrías críticas:
1. **Asimetría Estructural de Género:** El **77,33% de las víctimas históricas son mujeres** (1.161.392 mujeres frente a 340.417 hombres). En la población adulta, 3 de cada 4 agresiones son sufridas por mujeres (73,36% del total nacional).
2. **Asimetría Etaria y Vulnerabilidad en Menores:** 93.986 víctimas registradas son niñas, niños y adolescentes (menores de 18 años). De ellos, **3.035 fueron atacados en el interior de su hogar con armas letales** (armas de fuego o armas cortopunzantes/blancas), lo que evidencia un riesgo inminente de homicidio intrafamiliar.
3. **Asimetría y Concentración Territorial:** El **63,99% de las denuncias históricas se concentran en las 32 capitales de departamento**, mientras que los 1.079 municipios restantes comparten el 36,01%.

### 1.2 Alineación Estratégica con los Objetivos de Desarrollo Sostenible (ODS)
* **ODS 5 (Igualdad de Género) — Meta 5.2:** *"Eliminar todas las formas de violencia contra todas las mujeres y las niñas en los ámbitos público y privado, incluidas la trata y la explotación sexual y otros tipos de explotación"*.
* **ODS 16 (Paz, Justicia e Instituciones Sólidas) — Meta 16.1:** *"Reducir significativamente todas las formas de violencia y las correspondientes tasas de mortalidad en todo el mundo"*.

### 1.3 Línea Base de la Primera Entrega y su Limitación Metodológica Fundamental
En la Primera Entrega del proyecto (`Proyecto_etl_C1`) se implementó un pipeline inicial y un Data Warehouse en PostgreSQL modelando las denuncias de la Policía Nacional (704.551 filas brutas, 1.501.809 víctimas). A través de ese modelo se respondieron los requerimientos **R1 a R5**:
* **R1:** Dinámica temporal de víctimas por año y mes.
* **R2:** Concentración geográfica por departamento y municipio.
* **R3:** Perfil demográfico de las víctimas (género y etapa del ciclo vital).
* **R4:** Mecanismos o armas utilizadas en la agresión.
* **R5:** Casos graves de menores de edad agredidos con armas letales.

**La Limitación Crítica del Modelo Inicial:**
> *Las denuncias policiales miden exclusivamente **volumen de denuncias registradas**, una métrica altamente sesgada por la presencia estatal y la accesibilidad a las autoridades judiciales. En municipios sin presencia institucional de comisarías o juzgados, la cifra de denuncias es artificialmente baja o nula ("cero denuncias"), lo cual no significa ausencia de violencia, sino desprotección ciudadana y barreras de acceso a la justicia. Por el contrario, en las grandes ciudades el volumen es alto en gran parte por la disponibilidad de canales formales.*

Para transformar el dato de denuncia en una herramienta efectiva de política pública, era mandatorio cruzar la oferta de justicia con la demanda de atención.

---

## 2. ¿Qué Exigía el Pliego de la Segunda Entrega? (Tabla Resumen)

El documento de especificación académica (`ETL_2026-2_Project_SecondDelivery_v2.pdf`) fijó las siguientes capacidades y criterios de evaluación:

| # | Requisito del PDF | Detalle de la Exigencia | Cómo se Cumplió en la Solución |
| :-: | :--- | :--- | :--- |
| **1** | **Continuidad Entrega 1** | Preservar R1–R5, problema y ODS. Dejar intacto el repo anterior. | R1–R5 preservados y documentados en tabla comparativa. `Proyecto_etl_C1` quedó 100% inalterado. |
| **2** | **Segunda Fuente (API)** | Extracción programática vía API pública con datos ausentes en la fuente primaria. | Extracción REST de la API SODA de Comisarías de Familia (MinJusticia / `datos.gov.co`). |
| **3** | **Requisitos R6 y R7** | Dos nuevos requisitos que requieran cruzar ambas fuentes (unir resultados no basta). | **R6:** Sobrecarga por comisaría (`víctimas / comisarías`).<br>**R7:** Déficit legal Ley 2126 vs violencia letal contra niños y mujeres. |
| **4** | **Perfilamiento Separado** | Perfilar estadísticamente ambas fuentes por separado y medir riesgo de integración antes de transformar. | Script [src/profiling.py](file:///Users/usuario/Desktop/ETLproyecto2/Proyecto_etl_C2/src/profiling.py) y notebook: 98,92% de match territorial en DANE 5 dígitos. |
| **5** | **Matriz de Calidad (DQ)** | Mínimo 6 reglas formales con atributos, dimensiones, métricas, umbrales y severidad. | 14 reglas documentadas (`DQ-RAW1-*`, `DQ-RAW2-*`, `DQ-PREP-*`) trazables a R1–R7. |
| **6** | **Great Expectations (GX 1.X)** | Tres compuertas automáticas: datos brutos primarios, datos brutos de la API y datos preparados. | Implementado con GX Fluent API en [src/validate_gx.py](file:///Users/usuario/Desktop/ETLproyecto2/Proyecto_etl_C2/src/validate_gx.py) (Gates 1, 2 y 3). |
| **7** | **Contrato de Integración** | Documentar llaves de cruce, cardinalidad, manejo de no emparejados y supuestos. | Llave DANE 5 dígitos. 11 corregimientos amazónicos conservados como áreas no municipalizadas (**0 víctimas descartadas**). |
| **8** | **Modelo Dimensional** | Refinar el esquema estrella (Kimball): evaluar grano, dimensiones enriquecidas y outriggers. | `dim_geografia` enriquecida con comisarías y categorías de ley; `dim_comisaria` como outrigger físico; hechos con constraint de grano único. |
| **9** | **Data Warehouse Relacional** | PostgreSQL o MySQL con DDL, tipos, constraints y carga masiva de alto rendimiento. | PostgreSQL 16 en Docker con streaming binario `COPY` (701.714 hechos cargados en 16 segundos). |
| **10** | **Reconciliación Exacta** | Demostrar que los totales cargados coinciden exactamente con la fuente primaria. | Verificación SQL automática: **1.501.809 víctimas cargadas (Delta = 0, 0,0000%)**, 0 claves huérfanas. |
| **11** | **Orquestación Airflow 3.X** | Orquestar el flujo con TaskFlow API (`@dag`, `@task`), interfaces compactas y reintentos selectivos. | DAG modular en [dags/etl_violencia_intrafamiliar_dag.py](file:///Users/usuario/Desktop/ETLproyecto2/Proyecto_etl_C2/dags/etl_violencia_intrafamiliar_dag.py); metadatos ligeros por XCom, datos en Parquet. |
| **12** | **Pruebas de Confiabilidad** | Demostrar obligatoriamente Test A (Éxito), Test B (Falla controlada con bloqueo) y Test C (Idempotencia). | [src/run_pipeline.py](file:///Users/usuario/Desktop/ETLproyecto2/Proyecto_etl_C2/src/run_pipeline.py) ejecuta y certifica las 3 pruebas con reportes JSON persistidos. |
| **13** | **Producto Analítico / Dashboard** | Dashboard conectado al Data Warehouse que responda R1–R7 y muestre el valor de la API. | Dashboard web interactivo con Chart.js y Dark Mode en puerto 8080 con KPIs de déficit y gráficos de sobrecarga. |
| **14** | **Nuevo Repositorio Autónomo** | Repositorio independiente con archivos de entorno y README de 25 secciones. | Carpeta `Proyecto_etl_C2/` con Dockerfile, docker-compose, requirements.txt, .env.example y README exhaustivo. |

---

## 3. La API Utilizada: ¿Cuál fue, Cómo Funciona y qué Datos Aportó?

### 3.1 Identificación Técnica de la API
* **Entidad Emisora:** Ministerio de Justicia y del Derecho / Presidencia de la República.
* **Nombre Oficial del Dataset:** *Caracterización de las Comisarías de Familia en el Territorio Nacional*.
* **Plataforma Tecnológica:** Portal de Datos Abiertos de Colombia (`datos.gov.co`), provisto por la plataforma **Socrata Open Data API (SODA REST API)**.
* **Endpoint Base:**
  `https://www.datos.gov.co/resource/7tuu-upb2.json`
* **Volumen de Datos:** 1.249 registros detallados que cubren el directorio físico y administrativo de comisarías en 1.102 municipios colombianos.

### 3.2 ¿Cómo está Funcionando la Extracción? (Módulo `src/extract_api.py`)
1. **Llamadas Programáticas HTTP REST:**
   El módulo realiza solicitudes `GET` parametrizadas utilizando la librería `requests` de Python con parámetros SODA:
   - `$limit=2000`: Para extraer la totalidad del censo nacional en un solo lote consistente.
   - `$order=:id`: Para garantizar determinismo en el ordenamiento del resultado.
   - Headers: `Accept: application/json` y soporte opcional de autenticación mediante `X-App-Token` (variable `API_APP_TOKEN` en `.env`).
2. **Resiliencia y Tolerancia a Fallos de Red:**
   - Implementa **3 reintentos automáticos** con **backoff exponencial** (`sleep = 10s * (2 ** retry)`). Si el portal gubernamental experimenta microcortes de red o latencia transitoria, el extractor espera y reintenta automáticamente.
3. **Validación Criptográfica y Manifiesto de Pinned Data:**
   - Tras descargar los datos, calcula el hash SHA-256 del contenido (`data/raw/api_comisarias_raw.json`) y lo almacena en `data/raw/api_source_manifest.json` junto con la URL, cantidad de filas (1.249), timestamp y esquema de columnas detectado.
4. **Mecanismo de Caché Offline (Garantía de Sustentación en Clase):**
   - El pliego del PDF estipula explícitamente: *"The team must preserve prior evidence in case a remote API or external dependency is temporarily unavailable during the presentation"*.
   - Si durante la sustentación en clase no hay acceso a internet o la API de MinJusticia se cae, el extractor detecta la contingencia y utiliza automáticamente el archivo bruto respaldado en caché local, permitiendo que la demostración en vivo nunca falle.

### 3.3 ¿Los Datos de la API Eran Nuevos o Eran Repetidos?
**Eran datos 100% NUEVOS y completamente ortogonales a la fuente primaria.**

Para entender la enorme ganancia analítica, comparemos qué tenía la fuente primaria versus qué aportó la API:

| Característica / Variable | Fuente Primaria (Policía Nacional - DIJIN) | Fuente Secundaria (API MinJusticia - Comisarías) | ¿Eran Repetidos? |
| :--- | :--- | :--- | :---: |
| **Naturaleza del Dato** | Hechos delictivos y denuncias penales registradas. | Infraestructura física, capacidad institucional y marco normativo. | **No** (Ortogonales) |
| **Grano Transaccional** | Individual por reporte de víctima de violencia. | Directorio físico por sede de Comisaría de Familia. | **No** (Diferente grano) |
| **Presencia de Comisarías** | **Inexistente** (La Policía no registra comisarías). | `existencia_de_comisarias` (Cantidad verificada por municipio). | **NUEVO** |
| **Estándar Legal Ley 2126** | **Inexistente** (No contiene umbrales poblacionales). | `numero_de_comisarias_a_crear_por_ley_2126_de_2021` (Exigencia legal de 1 por cada 100k hab). | **NUEVO** |
| **Categoría Fiscal Ley 617** | **Inexistente** (Solo tenía nombres de municipio). | `categoria_del_municipio` (Especial, 1, 2, 3, 4, 5, 6). | **NUEVO** |
| **Datos de Contacto y Operación** | **Inexistente**. | Dirección, teléfono, correo y horarios de atención al público. | **NUEVO** |

**Resultado de la Integración:**
La fuente primaria aportó el **numerador** de la violencia (¿Cuántas víctimas hay en cada municipio?). La API aportó el **denominador** y el **estándar legal** (¿Con cuántas comisarías cuenta el Estado para atenderlas y cuántas debería tener por ley?).  
Al cruzarlas mediante el código DANE de 5 dígitos, se crearon los nuevos indicadores que resolvieron el sesgo de la Entrega 1.

---

## 4. El Producto Analítico y de Business Intelligence (Power BI Desktop)

### 4.1 Arquitectura del Dashboard de Business Intelligence
Para la Segunda Entrega, el producto analítico final se estructuró a través de un modelo semántico en **Power BI Desktop**, alojado en [`docs/powerbi/Dashboard-Poryecto2.pbix`](file:///Users/usuario/Desktop/ETLproyecto2/Proyecto_etl_C2/docs/powerbi/Dashboard-Poryecto2.pbix) y conectado directamente al Data Warehouse relacional **PostgreSQL 16** (`etl_dw`).

A diferencia de modelos desconectados o basados en archivos locales sueltos, el reporte se alimenta en modo **Import** mediante el conector nativo de PostgreSQL contra las tablas dimensionales y vistas semánticas optimizadas:
- `fact_violencia_intrafamiliar`
- `dim_tiempo`, `dim_geografia`, `dim_victima`, `dim_medio`, `dim_comisaria`
- `vw_r6_sobrecarga_comisarias` y `vw_r7_prioridad_intervencion`

### 4.2 Medidas DAX Principales y Controles de Reconciliación
El reporte implementa medidas DAX estandarizadas que reproducen con precisión exacta los totales de control del Data Warehouse:
* **Total Víctimas:** `1.501.809` (coincidencia exacta al centésimo con la fuente cruda).
* **Total Reportes:** `704.551` denuncias penales procesadas.
* **Menores en Riesgo Letal:** `3.035` víctimas menores atacadas con armas letales (R5).
* **Brecha Nacional Ley 2126:** `114` comisarías de familia faltantes en el territorio nacional (R7).
* **Tasa de Víctimas por Comisaría (R6):** Revela la sobrecarga crítica en municipios intermedios (ej. Cúcuta con 20.389 víctimas/comisaría y Popayán con 17.070).

### 4.3 Visualizaciones y Evidencias por Requerimiento (R1 a R7)
Para garantizar accesibilidad y evaluación independiente en cualquier sistema operativo (macOS, Linux o Windows sin Power BI instalado), se exportaron capturas de alta resolución de cada visual a `docs/powerbi/`:
1. **R1 (Evolución Anual 2010–2025):** [`r1_evolucion_anual.png`](file:///Users/usuario/Desktop/ETLproyecto2/Proyecto_etl_C2/docs/powerbi/r1_evolucion_anual.png) (Área con exclusión del año parcial 2026).
2. **R2 (Ranking Territorial y Capitales):** [`r2_departamentos.png`](file:///Users/usuario/Desktop/ETLproyecto2/Proyecto_etl_C2/docs/powerbi/r2_departamentos.png) (Treemap con drill-down a municipios; 63.99% en capitales).
3. **R3 (Distribución por Género):** [`r3_genero.png`](file:///Users/usuario/Desktop/ETLproyecto2/Proyecto_etl_C2/docs/powerbi/r3_genero.png) (Gráfico de dona; 77.33% mujeres).
4. **R4 (Mecanismos y Armas):** [`r4_mecanismos.png`](file:///Users/usuario/Desktop/ETLproyecto2/Proyecto_etl_C2/docs/powerbi/r4_mecanismos.png) (Embudo de armas contundentes, blancas y de fuego).
5. **R5 (Menores Agredidos con Armas Letales):** [`r5_mapa_menores.png`](file:///Users/usuario/Desktop/ETLproyecto2/Proyecto_etl_C2/docs/powerbi/r5_mapa_menores.png) (Mapa de burbujas georreferenciado).
6. **R6 (Sobrecarga Institucional por Comisaría):** [`r6_sobrecarga.png`](file:///Users/usuario/Desktop/ETLproyecto2/Proyecto_etl_C2/docs/powerbi/r6_sobrecarga.png) (Top 10 de sobrecarga por comisaría instalada).
7. **R7 (Matriz de Prioridad de Intervención Ley 2126):** [`r7_prioridad.png`](file:///Users/usuario/Desktop/ETLproyecto2/Proyecto_etl_C2/docs/powerbi/r7_prioridad.png) (Dispersión: Brecha Legal vs Violencia Letal Infantil).
8. **Diagrama Completo del Tablero:** [`Full Diagram - Domestic Violence.jpg`](file:///Users/usuario/Desktop/ETLproyecto2/Proyecto_etl_C2/docs/Full%20Diagram%20-%20Domestic%20Violence.jpg)

### 4.4 Conexión al Data Warehouse desde Cualquier Cliente SQL o BI
El Data Warehouse en PostgreSQL 16 está expuesto en el puerto `5432`:
- **Servidor:** `localhost:5432` | **Base de Datos:** `etl_dw`
- **Usuario:** `postgres` | **Contraseña:** `postgres123`
- **Vistas recomendadas para análisis:** `vw_r6_sobrecarga_comisarias` y `vw_r7_prioridad_intervencion`.

---

## 5. Arquitectura del Sistema y Funcionamiento de Extremo a Extremo

```
[Fuente Primaria: DIJIN] (CSV)  ──>  extract_primary.py  ──>  [Compuerta 1: validate_primary_raw]
                                                                        │
[Fuente Secundaria: MinJusticia] ──>  extract_api.py      ──>  [Compuerta 2: validate_api_raw]
                                                                        │
                                   ┌────────────────────────────────────┘
                                   ▼
                   transform_and_integrate.py (Limpieza, DANE 5d, Harmonización)
                                   │
                                   ▼
                   [Compuerta 3: validate_prepared] (Invariantes & Reconciliación)
                                   │
                                   ▼
                   load_dw.py (Streaming COPY masivo)
                                   │
                                   ▼
       PostgreSQL 16 DW (Star Schema: Hechos y Dimensiones)
         ├── dim_tiempo (6.056 filas)
         ├── dim_geografia (1.113 filas - Enriquecida con API)
         ├── dim_victima (11 cohortes)
         ├── dim_medio (6 miembros)
         ├── dim_comisaria (1.247 filas - Outrigger operativo)
         └── fact_violencia_intrafamiliar (701.714 filas - Grano exacto)
                                   │
                                   ▼
                   Dashboard Web Interactivo (Chart.js / SQL)
```

### 5.1 Las Tres Compuertas de Calidad con Great Expectations 1.X
1. **Compuerta 1 (`validate_primary_raw`):**
   - Evalúa la presencia de columnas mandatorias (`FECHA HECHO`, `CODIGO DANE`, `CANTIDAD`), formato de fechas DD/MM/YYYY, que CANTIDAD sea entero positivo y que nulos en género no superen el 1%.
2. **Compuerta 2 (`validate_api_raw`):**
   - Evalúa columnas obligatorias de la API (`c_digo_dane_municipio`, `existencia_de_comisarias`), longitud de código DANE entre 4 y 5 caracteres, valores válidos de categorías de Ley 617 y conteo no negativo de comisarías.
3. **Compuerta 3 (`validate_prepared`):**
   - Evalúa invariantes dimensionales antes de tocar la base de datos: unicidad del grano declarado, ausencia total de nulos en llaves foráneas, 100% de integridad referencial con dimensiones y **conciliación matemática exacta de víctimas (Suma = 1.501.809)**.

Cualquier infracción **Crítica** lanza un `ValidationError` que detiene el flujo y bloquea la carga al Data Warehouse.

### 5.2 El Modelo Dimensional Refinado (Ralph Kimball)
* **`dim_geografia` (1.113 filas):** Enriquecida con los atributos de la API (`comisarias_instaladas`, `comisarias_requeridas_ley`, `brecha_comisarias`, `categoria_municipio`). Permite resolver R1, R2, R6 y R7 mediante consultas directas a nivel de estrella.
* **`dim_comisaria` (1.247 filas - Outrigger):** Directorio detallado de comisarías físicas con dirección, teléfono, horario y ubicación para análisis operacional.
* **`dim_tiempo` (6.056 filas):** Calendario continuo 2010–2026 con bandera `es_periodo_completo` para aislar el año parcial 2026.
* **`dim_victima` (11 cohortes):** Género, grupo etario y bandera `es_menor_de_edad`.
* **`dim_medio` (6 miembros):** Mecanismos armonizados y bandera `es_arma_letal`.
* **`fact_violencia_intrafamiliar` (701.714 filas):** Grano formal municipal estricto `(id_tiempo, id_geografia, id_victima, id_medio)` protegido por `CONSTRAINT uq_fact_grano UNIQUE`. Medidas aditivas `cantidad_victimas` (1.501.809) y `numero_registros` (704.551 reportes colapsados).

### 5.3 Carga Masiva y Reconciliación Automatizada
* Utiliza el protocolo de streaming binario `COPY ... FROM STDIN WITH (FORMAT CSV)` de PostgreSQL vía `psycopg2`.
* Carga los 701.714 hechos en **menos de 17 segundos**.
* Ejecuta consultas SQL post-carga inmediatas:
  - Total registros esperados: 704.551 | Cargados: 704.551 | **Delta = 0**.
  - Total víctimas esperadas: 1.501.809 | Cargadas: 1.501.809 | **Delta = 0**.
  - Llaves foráneas huérfanas: **0**.

### 5.4 Orquestación y Confiabilidad (Airflow 3.X)
* El DAG implementa el TaskFlow API con dependencias estrictas:
  `extract_primary` $\rightarrow$ `validate_primary_raw`  
  `extract_api` $\rightarrow$ `validate_api_raw`  
  Ambas compuertas aprobadas $\rightarrow$ `transform_and_clean_and_integrate` $\rightarrow$ `validate_prepared` $\rightarrow$ `load_dimensional_dw`.
* **Políticas de Reintento Selectivas:**
  - Extracción Primaria: `retries=2, retry_delay=timedelta(minutes=1)` (resiliencia ante bloqueos u operaciones I/O temporales).
  - Extracción de API: `retries=3, retry_delay=timedelta(minutes=2)` (resiliencia ante microcortes de red, timeouts o límites 429 de SODA API).
  - Carga a DW: `retries=2, retry_delay=timedelta(minutes=1)` (resiliencia ante saturación transitoria de sockets/conexiones de base de datos).
  - Compuertas de Calidad y Transformación: `retries=0` (Fail Fast; los fallos deterministas de validación GX o de contrato de integración nunca deben reintentarse automáticamente con el mismo lote).

---

## 6. Demostración de Confiabilidad de Ingeniería (Las 3 Pruebas Obligatorias)

El script `src/run_pipeline.py` ejecuta y documenta las tres pruebas obligatorias exigidas por la Sección 20 del PDF:

### Prueba A: Ejecución Exitosa de Punta a Punta (Success Path)
* **Objetivo:** Demostrar que el pipeline procesa los datos reales, aprueba las 3 compuertas de validación y puebla el Data Warehouse con reconciliación exacta.
* **Resultado:**
  - Gate 1 (`validate_primary_raw`): **Aprobada** (5/5 checks superados).
  - Gate 2 (`validate_api_raw`): **Aprobada** (4/4 checks superados).
  - Transformación e Integración: **Completada** (1.100 municipios emparejados, 11 no municipalizados integrados, 0 víctimas descartadas).
  - Gate 3 (`validate_prepared`): **Aprobada** (5/5 invariantes dimensionales superados).
  - Carga a PostgreSQL DW: **Completada** en 20,01 segundos.
  - Reconciliación: **100% exacta** (Delta = 0).

### Prueba B: Falla Crítica Controlada y Bloqueo de Tareas (Controlled Failure)
* **Objetivo:** Demostrar que el sistema detecta anomalías severas y bloquea automáticamente las tareas aguas abajo para evitar corromper el Data Warehouse.
* **Método de Inyección:** Se inyectó un lote sintético anómalo en la compuerta Gate 2 de la API eliminando la columna crítica obligatoria `existencia_de_comisarias`.
* **Resultado:**
  - Gate 2 evaluó la anomalía y disparó un `ValidationError` con severidad `CRITICAL`.
  - El sistema abortó la ejecución de la rama.
  - Las tareas subsiguientes (`transform_and_clean_and_integrate`, `validate_prepared`, `load_dimensional_dw`) fueron marcadas como **`BLOCKED (UPSTREAM_FAILED)`**.
  - **El Data Warehouse quedó 100% intacto**, sin escrituras parciales ni datos corruptos.

### Prueba C: Reejecución Segura e Idempotencia (Safe Rerun)
* **Objetivo:** Demostrar que reejecutar el pipeline con el mismo lote o corregir una falla previa no genera registros duplicados ni altera las métricas acumuladas.
* **Resultado:**
  - Se capturó una instantánea de las tablas antes de la reejecución (`fact_rows = 701.714`, `victimas = 1.501.809`).
  - Se ejecutó el pipeline completo nuevamente sobre el Data Warehouse activo.
  - Las transacciones DDL/DML atómicas y el constraint de grano `CONSTRAINT uq_fact_grano UNIQUE` garantizaron un estado idéntico:
    - Delta en filas de hechos: **0**
    - Delta en suma de víctimas: **0**
    - Delta en municipios: **0**
  - **Idempotencia 100% demostrada**.

---

## 7. Herramientas y Tecnologías Utilizadas

| Herramienta / Tecnología | Versión | Rol en la Solución | Justificación de Ingeniería |
| :--- | :--- | :--- | :--- |
| **Python** | 3.13 / 3.11 | Lenguaje principal del sistema | Ecosistema líder en Data Engineering, compatibilidad nativa con GX, Airflow y Pandas. |
| **PostgreSQL** | 16 (Alpine) | Motor de Data Warehouse | Base de datos relacional robusta con soporte para streaming `COPY`, llaves foráneas estrictas y vistas analíticas optimizadas. |
| **Docker & Docker Compose** | 29.4+ | Contenerización de infraestructura | Garantiza reproducibilidad de entorno del Data Warehouse y Airflow con un único comando. |
| **Great Expectations** | 1.24.0 | Validación de calidad automatizada | Estándar de la industria para compuertas de calidad declarativas (GX 1.X Fluent API, Checkpoints y Suites JSON). |
| **Apache Airflow** | 3.1.8 (Docker) / 3.3.2 (Local) | Orquestación de flujos de trabajo | Orquestador líder. Permite modelar dependencias DAG, Task SDK (`airflow.sdk`), reintentos selectivos y observabilidad. |
| **Pandas & NumPy** | 2.2+ / 2.0+ | Transformación y normalización | Procesamiento vectorial eficiente en memoria para datasets de tamaño medio (700k filas). |
| **PyArrow** | 15.0+ | Persistencia intermedia (Parquet) | Formato columnar comprimido con preservación estricta de tipos de datos para la capa procesada. |
| **psycopg2-binary** | 2.9.12 | Conector nativo de PostgreSQL | Permite el uso del protocolo de streaming `COPY ... FROM STDIN WITH (FORMAT CSV)`, cargando 700k registros en 16 segundos con transacción atómica. |
| **Power BI Desktop** | 2.128+ | Capa de Business Intelligence | Modelo estrella conectado a PostgreSQL para navegación interactiva de R1–R7, KPIs y matrices de intervención. |
| **Jupyter & nbclient** | 7.3+ / 0.11+ | Notebook reproducible | Documentación viva del perfilamiento y validación con celdas ejecutadas y salidas persistidas. |

---

## 8. Estructura de Evidencias y Directorios

```
Proyecto_etl_C2/
├── .env.example                       # Plantilla de variables de entorno seguras
├── .gitignore                         # Exclusión de artefactos, pycache y temporales
├── Dockerfile                         # Contenedor para ejecución reproducible del pipeline y Airflow
├── docker-compose.yaml                # Orquestación de PostgreSQL 16 y Apache Airflow 3.1.8
├── requirements.txt                   # Dependencias fijadas (GX, Airflow, Pandas, etc.)
├── README.md                          # Documentación maestra con las 26 secciones de la rúbrica
├── CONTEXTO_Y_EXPLICACION_TECNICA.md  # Este documento de contexto técnico detallado
├── config/
│   └── simple_auth_manager_passwords.json # Credenciales de desarrollo para Airflow Web UI
├── dags/
│   └── etl_violencia_intrafamiliar_dag.py # DAG de Airflow 3.1.8 con Task SDK y reintentos selectivos
├── gx/                                # Infraestructura Great Expectations 1.X
│   ├── gx_config.yaml                 # Configuración global y manifiesto de calidad
│   ├── README_GX.md                   # Matriz de trazabilidad y documentación de suites
│   ├── expectations/                  # Expectation Suites JSON (Gates 1, 2 y 3)
│   ├── checkpoints/                   # Checkpoints declarativos de ejecución
│   └── validation_definitions/        # Definiciones de validación por dataset
├── data/
│   ├── raw/                           # Datasets brutos (fuente primaria y API)
│   └── processed/                     # Datos limpios y enriquecidos en formato Parquet
├── docs/
│   ├── Pipeline Workflow ETL-C2.png   # Diagrama de flujo del pipeline de datos
│   ├── Dimensional Modeling ETL-C2.png# Diagrama del modelo estrella relacional
│   ├── Full Diagram - Domestic Violence.jpg # Diagrama completo de arquitectura
│   ├── powerbi/                       # Archivo .pbix y capturas de alta resolución R1 a R7
│   │   ├── Dashboard-Poryecto2.pbix   # Archivo de Power BI conectado al DW
│   │   ├── r1_evolucion_anual.png     # Visual R1
│   │   ├── r2_departamentos.png       # Visual R2
│   │   ├── r3_genero.png              # Visual R3
│   │   ├── r4_mecanismos.png          # Visual R4
│   │   ├── r5_mapa_menores.png        # Visual R5
│   │   ├── r6_sobrecarga.png          # Visual R6
│   │   └── r7_prioridad.png           # Visual R7
│   └── evidence/                      # Evidencias de ejecución y perfilamiento
│       ├── profiling_evidence.json    # Resultados estadísticos de ambas fuentes
│       ├── reconciliation_report.json # Reporte de reconciliación exacta del DW
│       ├── test_a_successful_run.json # Evidencia de ejecución exitosa
│       ├── test_b_controlled_failure.json # Evidencia de falla controlada
│       ├── test_c_safe_rerun.json     # Evidencia de idempotencia (Deltas = 0)
│       └── gx_validation_*_latest.json# Evidencias de auditoría Great Expectations
├── notebooks/
│   └── profiling_and_validation.ipynb # Notebook ejecutable con outputs persistidos
├── sql/
│   ├── create_dw.sql                  # DDL de PostgreSQL con constraints y tipos
│   ├── bi_views.sql                   # Vistas semánticas para el dashboard
│   └── analytical_queries.sql         # Consultas analíticas SQL para R1 a R7
└── src/
    ├── extract_primary.py             # Extracción con validación de hash SHA-256
    ├── extract_api.py                 # Extracción REST SODA API de Comisarías
    ├── profiling.py                   # Perfilamiento estadístico independiente
    ├── transform_and_integrate.py     # Limpieza, normalización DANE y cruce
    ├── dimensional_model.py           # Generación de dimensiones y hechos
    ├── validate_gx.py                 # Great Expectations 1.X (Gates 1, 2 y 3)
    ├── load_dw.py                     # Streaming COPY atómico y reconciliación exacta
    └── run_pipeline.py                # Ejecutor de las 3 pruebas de confiabilidad
```
