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

## 2. ¿Qué Exigía el Pliego de la Segunda Entrega?

El documento de especificación académica (`ETL_2026-2_Project_SecondDelivery_v2.pdf`) fijó las siguientes 12 exigencias obligatorias:

1. **Continuidad con la Primera Entrega:** Preservar el problema analítico, los ODS y los requerimientos R1–R5 (con justificación explícita de cualquier refinamiento). El repositorio de la Entrega 1 debe permanecer intacto.
2. **Segunda Fuente Programática vía API:** Incorporar un origen de datos secundario consumido programáticamente (sin descargas manuales) desde una API pública que aporte variables ausentes en la fuente primaria.
3. **Requerimientos Integrados R6 y R7:** Formular dos nuevas preguntas analíticas de alto impacto que requieran obligatoriamente combinar datos de la fuente primaria y de la API (uniones de resultados no son válidas; se requiere integración dimensional profunda).
4. **Perfilamiento de Datos Separado:** Realizar perfilamiento estadístico y estructural de ambas fuentes de manera independiente antes de transformar. El perfilamiento debe observar sin modificar los datos.
5. **Matriz de Riesgos y Reglas de Calidad (Data Quality):** Definir un marco formal de calidad con reglas trazables, dimensiones de calidad (completitud, validez, conformidad, unicidad, consistencia), métricas, umbrales y niveles de severidad (Crítica, Advertencia, Informativa).
6. **Validación Automatizada con Great Expectations (GX 1.X):** Implementar tres compuertas de validación:
   - Compuerta 1 (`validate_primary_raw`): Valida los datos brutos primarios tras la extracción.
   - Compuerta 2 (`validate_api_raw`): Valida los datos brutos de la API tras la extracción.
   - Compuerta 3 (`validate_prepared`): Valida el dataset integrado y transformado antes de permitir su carga en el Data Warehouse.
7. **Contrato de Integración de Ingeniería:** Especificar formalmente la llave de cruce, cardinalidad, transformaciones previas, armonización temporal, manejo de no emparejados (unmatched) y limitaciones.
8. **Refinamiento del Modelo Dimensional (Ralph Kimball):** Ajustar el esquema estrella de la Primera Entrega para incorporar las nuevas entidades o atributos enriquecidos, justificando el grano de hechos y las dimensiones.
9. **Data Warehouse Relacional en PostgreSQL:** Implementar el esquema físico con DDL, tipos de datos óptimos, llaves primarias/foráneas, constraints de unicidad y un mecanismo de carga masiva de alto rendimiento con reconciliación post-carga exacta.
10. **Orquestación con Apache Airflow 3.X:** Orquestar el flujo de datos completo mediante el TaskFlow API (`@dag`, `@task`), garantizando interfaces compactas (sin transferir datasets masivos por XCom), dependencias estrictas y políticas de reintento diferenciadas.
11. **Pruebas de Confiabilidad Obligatorias (Sección 20):** Demostrar el comportamiento del sistema bajo tres escenarios:
    - **Test A (Éxito completo):** Pipeline de punta a punta con todas las compuertas aprobadas y reconciliación exacta.
    - **Test B (Falla Crítica Controlada):** Inyección de datos anómalos que violen una regla crítica; la compuerta debe fallar y las tareas dependientes aguas abajo deben quedar bloqueadas (`UPSTREAM_FAILED`), protegiendo el Data Warehouse.
    - **Test C (Reejecución Segura / Idempotencia):** Reejecución con el mismo lote que demuestre que no se generan duplicados ni se corrompen las métricas (Deltas = 0).
12. **Producto Analítico / Dashboard:** Crear un dashboard interactivo conectado directamente al Data Warehouse que responda visualmente a R1–R7, con especial énfasis en R6 y R7.

---

## 3. ¿Qué Herramientas y Tecnologías se Utilizaron?

| Herramienta / Tecnología | Versión | Rol en la Solución | Justificación de Ingeniería |
| :--- | :--- | :--- | :--- |
| **Python** | 3.13 / 3.11 | Lenguaje principal del sistema | Ecosistema líder en Data Engineering, compatibilidad nativa con GX, Airflow y Pandas. |
| **PostgreSQL** | 16 (Alpine) | Motor de Data Warehouse | Base de datos relacional robusta con soporte para streaming `COPY`, llaves foráneas estrictas y vistas analíticas optimizadas. |
| **Docker & Docker Compose** | 29.4+ | Contenerización de infraestructura | Garantiza reproducibilidad de entorno del Data Warehouse en cualquier máquina host con un único comando. |
| **Great Expectations** | 1.24.0 | Validación de calidad automatizada | Estándar de la industria para compuertas de calidad declarativas (GX 1.X Fluent API). |
| **Apache Airflow** | 3.3.2 | Orquestación de flujos de trabajo | Orquestador líder. Permite modelar dependencias DAG, reintentos selectivos y observabilidad de estado. |
| **Pandas & NumPy** | 2.2+ / 2.0+ | Transformación y normalización | Procesamiento vectorial eficiente en memoria para datasets de tamaño medio (700k filas). |
| **PyArrow** | 15.0+ | Persistencia intermedia (Parquet) | Formato columnar comprimido con preservación estricta de tipos de datos para la capa procesada. |
| **psycopg2-binary** | 2.9.12 | Conector nativo de PostgreSQL | Permite el uso del protocolo de streaming `COPY ... FROM STDIN WITH (FORMAT CSV)`, cargando 700k registros en 16 segundos. |
| **HTML5 & Vanilla CSS** | W3C Modern | Interfaz de usuario del Dashboard | Arquitectura web ligera sin dependencias pesadas de Node/npm, con estética Glassmorphism, Dark Mode y responsive layout. |
| **Chart.js** | 4.4.1 | Visualizaciones interactivas | Gráficos dinámicos de series de tiempo, barras apiladas, donas y dispersión para R1–R7. |
| **Matplotlib** | 3.10.9 | Generación de diagramas técnicos | Creación programática de los diagramas de arquitectura del sistema y del modelo estrella relacional. |
| **Jupyter & nbclient** | 7.3+ / 0.11+ | Notebook reproducible | Documentación viva del perfilamiento y validación con celdas ejecutadas y salidas persistidas. |

---

## 4. ¿Cómo se Hizo y de Qué Manera Funciona el Sistema?

### 4.1 Selección Justificada de la API: Directorio de Comisarías de Familia (MinJusticia)
* **Entidad Emisora:** Ministerio de Justicia y del Derecho.
* **Plataforma:** Portal de Datos Abiertos de Colombia (`datos.gov.co`).
* **Endpoint SODA REST:** `https://www.datos.gov.co/resource/7tuu-upb2.json`
* **Volumen:** 1.249 registros de comisarías cubriendo 1.102 municipios colombianos.
* **Atributos Clave Incorporados:**
  - Código DANE del municipio (`c_digo_dane_municipio`).
  - Número de comisarías verificadas instaladas por municipio (`existencia_de_comisarias`).
  - Número de comisarías mínimas requeridas por mandato de la **Ley 2126 de 2021** (`numero_de_comisarias_a_crear_por_ley_2126_de_2021`), calculada con base en el estándar de al menos 1 comisaría por cada 100.000 habitantes.
  - Categoría municipal según la **Ley 617 de 2000** (`categoria_del_municipio`: Especial, 1, 2, 3, 4, 5, 6), que mide la capacidad presupuestal y administrativa del ente territorial.
  - Datos operativos: dirección física, teléfono de contacto, correo institucional y horarios de atención al público.

### 4.2 Formulación de los Nuevos Requerimientos Integrados R6 y R7
Los requerimientos R6 y R7 responden a preguntas que ninguna de las dos fuentes puede responder por sí sola:

#### Requerimiento R6: Sobrecarga Institucional y Presión Operativa por Comisaría
* **Pregunta de Negocio:** ¿Cuál es la carga acumulada de víctimas de violencia intrafamiliar por comisaría instalada en cada municipio colombiano, y en qué territorios existe un colapso operativo por sobredemanda de justicia?
* **Lógica de Integración:**
  $$\text{Tasa de Carga} = \frac{\sum(\text{cantidad\_victimas})}{\text{MAX}(\text{comisarias\_instaladas})}$$
* **Hallazgo de Impacto:** Las ciudades con mayor sobrecarga relativa no son las tres grandes metrópolis (Bogotá, Medellín, Cali cuentan con múltiples comisarías), sino **ciudades intermedias con déficit de infraestructura**:
  1. **Cúcuta (Norte de Santander):** 20.389 víctimas históricas atendidas por **1 sola comisaría** (20.389 víctimas/comisaría).
  2. **Popayán (Cauca):** 17.070 víctimas históricas con **1 sola comisaría** (17.070 víctimas/comisaría).
  3. **Bello (Antioquia):** 16.984 víctimas históricas con **1 sola comisaría** (16.984 víctimas/comisaría).
  4. **Soacha (Cundinamarca):** 33.390 víctimas con 2 comisarías (16.695 víctimas/comisaría).

#### Requerimiento R7: Déficit Legal de Comisarías (Ley 2126) vs. Severidad Letal en Menores y Mujeres
* **Pregunta de Negocio:** ¿En qué municipios el incumplimiento del estándar legal de comisarías de familia (Ley 2126 de 2021) coincide críticamente con focos de agresión letal contra menores de edad (R5) y mujeres (R3)?
* **Lógica de Integración:**
  $$\text{Brecha Legal} = \max(0, \text{comisarias\_requeridas\_ley} - \text{comisarias\_instaladas})$$
  Cruzado con el conteo de menores atacados con armas de fuego o cortopunzantes.
* **Hallazgo de Impacto:**
  - A nivel nacional existe un **déficit acumulado de 114 comisarías de familia** para cumplir con la Ley 2126.
  - El caso más grave de Colombia es **Cúcuta**, que requiere legalmente 9 comisarías por su población, tiene solo 1 (**brecha de 8 comisarías**) y acumula **51 menores de edad agredidos en el hogar con armas letales**. Se clasifica como **Prioridad 1 Urgente** de intervención para el ICBF y MinJusticia.
  - **Soacha** presenta una brecha de 4 comisarías y 13 menores atacados con armas letales.

### 4.3 Arquitectura por Capas y Contrato de Integración
El pipeline sigue la arquitectura de capas **Medallion (Bronze $\rightarrow$ Silver $\rightarrow$ Gold)**:

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

#### Reglas del Contrato de Integración:
1. **Llave de Cruce:** Código DANE municipal de 5 dígitos (`codigo_dane_municipio`).
2. **Preprocesamiento:**
   - La fuente primaria DIJIN contenía códigos DANE de 8 dígitos (`DDMMMCCC` a nivel centro poblado). Se truncaron a los primeros 5 dígitos (`DDMMM`) para estandarizarlos a nivel municipal.
   - La API de Comisarías contenía códigos de 4 o 5 dígitos en formato de texto. Se aplicó `.str.zfill(5)` para recuperar ceros iniciales perdidos (ej. Antioquia `05088`).
3. **Manejo de Casos No Emparejados (Unmatched):**
   - **11 áreas no municipalizadas** en la fuente primaria (corregimientos de Amazonas, Vaupés, Guainía sin personería municipal): Se conservaron en `dim_geografia` asignándoles categoría `'ÁREA NO MUNICIPALIZADA'`, `comisarias_instaladas = 0` y `brecha_comisarias = 1`. **Ninguna víctima fue descartada**.
   - **2 municipios en la API sin denuncias históricas:** Carmen del Darién (`27150`) y Barrancominas (`94343`) registraban comisaría física pero cero denuncias policiales en el período. Fueron agregados a `dim_geografia` para que `dim_comisaria` tenga integridad referencial absoluta (**cero claves huérfanas**).

### 4.4 Matriz de Calidad y Validación Automatizada con Great Expectations 1.X
Se diseñaron **14 reglas de calidad de datos** estructuradas en tres compuertas:

| ID Regla | Compuerta | Atributo Evaluado | Dimensión de Calidad | Métrica / Umbral | Severidad | Acción Pipeline |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DQ-RAW1-01** | Gate 1 (Primaria) | `FECHA HECHO`, `CODIGO DANE`, `CANTIDAD` | Completitud | Columnas existen y no nulas | Crítica | Bloquea pipeline |
| **DQ-RAW1-02** | Gate 1 (Primaria) | `FECHA HECHO` | Validez | Formato fecha ISO/estándar | Crítica | Bloquea pipeline |
| **DQ-RAW1-03** | Gate 1 (Primaria) | `CODIGO DANE` | Conformidad | Longitud string == 8 chars | Advertencia | Registra warning |
| **DQ-RAW1-04** | Gate 1 (Primaria) | `CANTIDAD` | Validez | Valor entero > 0 | Crítica | Bloquea pipeline |
| **DQ-RAW1-05** | Gate 1 (Primaria) | `GENERO` | Completitud | Tasa de nulos <= 1% | Advertencia | Registra warning |
| **DQ-RAW2-01** | Gate 2 (API) | `c_digo_dane_municipio`, `existencia_de_comisarias` | Completitud | Columnas mandatorias existen | Crítica | Bloquea pipeline |
| **DQ-RAW2-02** | Gate 2 (API) | `c_digo_dane_municipio` | Conformidad | Longitud string entre 4 y 5 | Crítica | Bloquea pipeline |
| **DQ-RAW2-03** | Gate 2 (API) | `categoria_del_municipio` | Validez | Valores en catálogo Ley 617 | Advertencia | Registra warning |
| **DQ-RAW2-04** | Gate 2 (API) | `existencia_de_comisarias` | Validez | Valor numérico >= 0 | Crítica | Bloquea pipeline |
| **DQ-PREP-01** | Gate 3 (Prepared) | `id_tiempo, id_geografia, id_victima, id_medio` | Unicidad | Unicidad estricta del grano | Crítica | Bloquea carga DW |
| **DQ-PREP-02** | Gate 3 (Prepared) | Claves foráneas | Completitud | Nulos en FKs == 0 | Crítica | Bloquea carga DW |
| **DQ-PREP-03** | Gate 3 (Prepared) | Claves de dimensión | Consistencia | 100% match con dimensiones | Crítica | Bloquea carga DW |
| **DQ-PREP-04** | Gate 3 (Prepared) | `comisarias_instaladas` | Validez | Valores enteros >= 0 | Crítica | Bloquea carga DW |
| **DQ-PREP-05** | Gate 3 (Prepared) | `cantidad_victimas` | Consistencia | Suma == 1.501.809 (Delta = 0) | Crítica | Bloquea carga DW |

### 4.5 El Modelo Dimensional Refinado (PostgreSQL 16)
Siguiendo los principios de modelado de Ralph Kimball:
1. **`dim_geografia` (1.113 filas):** Actúa como dimensión consolidada y enriquecida con los atributos de la API (`categoria_municipio`, `comisarias_instaladas`, `comisarias_requeridas_ley`, `brecha_comisarias`, `tiene_comisaria`). Esta decisión de diseño permite resolver las consultas de R1, R2, R6 y R7 mediante consultas SQL simples a nivel de estrella sin desnormalizar la tabla de hechos.
2. **`dim_comisaria` (1.247 filas - Outrigger):** Almacena el directorio operacional de sedes físicas con dirección, horario de atención, teléfono y correo electrónico para soporte operativo.
3. **`dim_tiempo` (6.056 filas):** Cubre el calendario diario continuo entre 2010 y 2026. Incluye la bandera booleana `es_periodo_completo` para excluir el año parcial 2026 de los cálculos de series de tiempo interanuales.
4. **`dim_victima` (11 cohortes):** Clasificación por género (`FEMENINO`, `MASCULINO`, `NO REPORTADO`) y ciclo vital (`ADULTOS`, `MENORES`, `ADOLESCENTES`, `NO REPORTADO`), con la bandera `es_menor_de_edad`.
5. **`dim_medio` (6 miembros):** Armas y mecanismos armonizados con la bandera `es_arma_letal`.
6. **`fact_violencia_intrafamiliar` (701.714 filas):** Grano formal declarado:
   $$\text{Grano} = (\text{id\_tiempo}, \text{id\_geografia}, \text{id\_victima}, \text{id\_medio})$$
   Protegido por el constraint de base de datos `CONSTRAINT uq_fact_grano UNIQUE (...)`. Contiene las medidas aditivas `cantidad_victimas` (1.501.809 víctimas totales) y `numero_registros` (704.551 reportes consolidados).

### 4.6 Carga Masiva y Reconciliación Automatizada
El script `src/load_dw.py` implementa el protocolo de streaming binario `COPY ... FROM STDIN WITH (FORMAT CSV)` de PostgreSQL. Esto permite insertar los 701.714 registros de hechos en **16,8 segundos**.

Inmediatamente después de la carga, el script ejecuta queries de reconciliación matemática estricta:
* Total de víctimas en origen primario: **1.501.809**
* Total de víctimas en `fact_violencia_intrafamiliar`: **1.501.809**
* **Diferencia (Delta de víctimas): 0 (0,000000%)**
* Total de reportes en origen primario: **704.551**
* Total de reportes en `fact_violencia_intrafamiliar`: **704.551**
* **Diferencia (Delta de reportes): 0 (0,000000%)**
* Claves foráneas huérfanas en el Data Warehouse: **0**

### 4.7 Orquestación con Apache Airflow 3.X
El archivo `dags/etl_violencia_intrafamiliar_dag.py` implementa la orquestación mediante el moderno TaskFlow API de Airflow:
* **Interfaces Compactas:** Las tareas no intercambian DataFrames masivos por XCom (lo cual colapsaría la base de datos de metadatos de Airflow). En su lugar, intercambian metadatos de manifiesto tipo JSON (`{"status": "SUCCESS", "records": 704551, "file_path": "..."}`).
* **Políticas de Reintento Selectivas y Justificadas:**
  - `extract_api_task`: `retries=3, retry_delay=10s, retry_exponential_backoff=True` (diseñado para tolerancia a fallos ante microcortes o límites de tasa de la API remota).
  - `load_dw_task`: `retries=1, retry_delay=5s` (tolerancia a fallos por reinicios transitorios del socket de PostgreSQL).
  - Tareas de Calidad (`validate_primary_raw_task`, `validate_api_raw_task`, `validate_prepared_task`): `retries=0` (Fail Fast; un error de esquema o calidad es determinista y no debe reintentarse automáticamente).

---

## 5. Demostración de Confiabilidad de Ingeniería (Las 3 Pruebas Obligatorias)

El script `src/run_pipeline.py` ejecuta y documenta las tres pruebas obligatorias exigidas por la Sección 20 del PDF:

### Prueba A: Ejecución Exitosa de Punta a Punta (Success Path)
* **Objetivo:** Demostrar que el pipeline procesa los datos reales, aprueba las 3 compuertas de validación y puebla el Data Warehouse con reconciliación exacta.
* **Resultado:**
  - Gate 1 (`validate_primary_raw`): **Aprobada** (5/5 checks superados).
  - Gate 2 (`validate_api_raw`): **Aprobada** (4/4 checks superados).
  - Transformación e Integración: **Completada** (1.100 municipios emparejados, 11 no municipalizados integrados, 0 víctimas descartadas).
  - Gate 3 (`validate_prepared`): **Aprobada** (5/5 invariantes dimensionales superados).
  - Carga a PostgreSQL DW: **Completada** en 19,63 segundos.
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

## 6. Estructura de Evidencias y Directorios

El repositorio `Proyecto_etl_C2` cuenta con la siguiente arquitectura de archivos:

```
Proyecto_etl_C2/
├── .env.example                       # Plantilla de variables de entorno seguras
├── .gitignore                         # Exclusión de artefactos, pycache y temporales
├── Dockerfile                         # Contenedor para ejecución reproducible del pipeline
├── docker-compose.yaml                # Orquestación de PostgreSQL 16
├── requirements.txt                   # Dependencias fijadas (GX, Airflow, Pandas, etc.)
├── README.md                          # Documentación maestra con las 25 secciones del PDF
├── CONTEXTO_Y_EXPLICACION_TECNICA.md  # Este documento de contexto técnico detallado
├── GUIA_EJECUCION_PASO_A_PASO.md      # Guía paso a paso para evaluadores externos
├── dags/
│   └── etl_violencia_intrafamiliar_dag.py  # DAG de Airflow 3.X con TaskFlow API
├── dashboard/
│   ├── index.html                     # Frontend Glassmorphism / Dark Mode
│   ├── styles.css                     # Estilos visuales de alto impacto
│   ├── app.js                         # Lógica cliente y gráficos Chart.js
│   ├── data_dw.json                   # Datos analíticos agregados del DW
│   ├── export_dw_data.py              # Exportador automatizado desde PostgreSQL
│   └── server.py                      # Servidor HTTP local embebido
├── data/
│   ├── raw/                           # Datasets brutos (fuente primaria y API)
│   └── processed/                     # Datos limpios y enriquecidos en formato Parquet
├── docs/
│   ├── architecture.png               # Diagrama arquitectónico generado
│   ├── star_schema.png                # Diagrama entidad-relación del modelo estrella
│   ├── generate_diagrams.py           # Generador programático de diagramas
│   └── evidence/                      # Evidencias de ejecución y perfilamiento
│       ├── profiling_evidence.json    # Resultados estadísticos de ambas fuentes
│       ├── test_a_success.json        # Evidencia de ejecución exitosa
│       ├── test_b_controlled_failure.json  # Evidencia de falla controlada
│       └── test_c_safe_rerun.json     # Evidencia de idempotencia (Deltas = 0)
├── notebooks/
│   └── profiling_and_validation.ipynb # Notebook ejecutable con outputs persistidos
├── sql/
│   ├── create_dw.sql                  # DDL de PostgreSQL con constraints y tipos
│   └── analytical_queries.sql         # Consultas analíticas SQL para R1 a R7
└── src/
    ├── extract_primary.py             # Extracción con validación de hash SHA-256
    ├── extract_api.py                 # Extracción REST SODA API de Comisarías
    ├── profiling.py                   # Perfilamiento estadístico independiente
    ├── transform_and_integrate.py     # Limpieza, normalización DANE y cruce
    ├── dimensional_model.py           # Generación de dimensiones y hechos
    ├── validate_gx.py                 # Great Expectations 1.X (Gates 1, 2 y 3)
    ├── load_dw.py                     # Streaming COPY y reconciliación exacta
    └── run_pipeline.py                # Ejecutor de las 3 pruebas de confiabilidad
```
