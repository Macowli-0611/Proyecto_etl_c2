# 🎙️ Guion Maestro de Sustentación & Defensa Técnica — Proyecto 2 ETL & DW
> **Ecosistema:** Apache Airflow 3 Task SDK • Great Expectations 1.X • PostgreSQL 16 • Power BI  
> **Tema:** Pipeline Automatizado de Violencia Intrafamiliar y Capacidad Institucional (MinJusticia API SODA)  
> **Duración estimada:** 12 a 15 minutos en total (~3 a 3.5 minutos por compañero).

---

## 👥 Tabla Oficial de Asignación de Roles

| Expositor | Diapositivas | Eje Temático Principal | Especialidad en Preguntas |
| :--- | :---: | :--- | :--- |
| 👤 **Michael** | **1, 2 y 3** | **Contexto, Valor de la API y Arquitectura:** Portada, métricas globales (704k denuncias, 1.5M víctimas), valor de la API SODA y flujo modular punta a punta (zoom al diagrama). | Extracción dual, SODA REST API, tolerancia a fallos de red. |
| 👤 **Manrique** | **4, 5 y 6** | **Calidad y Modelado Dimensional:** Las 3 compuertas de Great Expectations (Gates 1, 2 y 3), contrato territorial DANE, deduplicación matemática al grano y modelo en estrella en PostgreSQL. | Reglas GX (DQ-RAW1 a DQ-PREP), reconciliación matemática, Star Schema y claves sustitutas. |
| 👤 **David** | **7, 8 y 9** | **Orquestación y Pruebas Airflow:** Airflow 3 Task SDK, XCom liviano con Parquet, reintentos selectivos, tabla de tareas en vivo de Airflow Web UI (Tests A, B y C) y primeros hallazgos en Power BI (R1 a R4). | Falla controlada en Airflow (Test B), AirflowFailException, trigger rules, tendencias R1-R4. |
| 👤 **Torres** | **10, 11 y 12** | **Capacidad Estatal y Cierre:** Hallazgos institucionales R5 a R7 (sobrecarga de comisarías con >1,200 casos/año y los 29 municipios sin comisarías), limitaciones, aprendizajes y cierre / demo. | Ratios analíticos R6-R7, vistas analíticas SQL, cifra negra, conclusiones de ingeniería. |

---

## ⌨️ Atajos de Control para la Exposición (`slides.html`)
- **Avanzar / Retroceder:** `Flecha Derecha (→)` / `Flecha Izquierda (←)` o `Espacio`.
- **Pantalla Completa:** Presionar tecla `F`.
- **Ampliar Diagramas / Gráficas:** Clic sobre cualquier imagen para activar el **Lightbox Zoom** interactivo.
- **Cambiar Tema de Color:** Botones superiores (`1`: Tono Medio Slate, `2`: Platino, `3`: Claro, `4`: Oscuro).

---

# 🗣️ PARTE 1: Discurso Paso a Paso por Diapositiva

---

## 🔵 BLOQUE 1: CONTEXTO, NEGOCIO Y ARQUITECTURA (Michael)

### 📌 Diapositiva 1: Portada y Presentación del Proyecto
* **Expositor:** **Michael**
* **Acción en pantalla:** Mantener visible la portada. Señalar las 4 tarjetas numéricas.
* **Discurso exacto:**
> *"Buenos días / tardes, profesor y compañeros. Hoy les presentamos la sustentación de la segunda entrega de nuestro proyecto de Ingeniería de Datos. Nuestro objetivo fue diseñar e implementar un pipeline ETL automatizado, resiliente y observable que conecta el registro histórico de violencia intrafamiliar en Colombia con la capacidad real de respuesta institucional del Estado.*
>
> *Para entender la escala del sistema:*
> *- Procesamos **704,551 denuncias policiales** históricas.*
> *- Reconciliamos matemáticamente **1,501,809 víctimas** con **cero pérdida de datos (delta = 0)**.*
> *- Integramos en tiempo real las **1,249 sedes activas de comisarías de familia** del Ministerio de Justicia mediante una API REST pública.*
> *- Todo está orquestado con el moderno **Task SDK de Apache Airflow 3**, validado con **Great Expectations 1.X** en tres compuertas automáticas y cargado en un **Data Warehouse PostgreSQL 16** modelado en estrella para responder a 7 preguntas analíticas en Power BI."*

---

### 📌 Diapositiva 2: El Problema de Negocio y el Aporte de la API SODA
* **Expositor:** **Michael**
* **Acción en pantalla:** Pasar a Diapositiva 2. Contrastar columna izquierda ("Lo que teníamos") con columna derecha ("Lo que logramos").
* **Discurso exacto:**
> *"En la primera entrega trabajamos únicamente con la fuente primaria de la Policía Nacional. Teníamos resueltas las preguntas R1 a R5: sabíamos cuántos casos ocurrían, en qué departamentos, la brecha de género y la afectación a menores.*
>
> *Sin embargo, nos dimos cuenta de un vacío analítico crítico: saber que en un municipio se denuncian 500 agresiones al año no nos decía si el Estado tenía capacidad instalada para atender a esas personas, si las comisarías estaban colapsadas o si directamente no existía presencia institucional.*
>
> *Por eso, en esta segunda entrega integramos la API SODA de Datos Abiertos del Ministerio de Justicia. Esta API aporta el directorio oficial georreferenciado de todas las comisarías del país, permitiéndonos resolver dos preguntas estratégicas que antes eran imposibles de responder:*
> *- **R6 (Sobrecarga Operativa):** Calculamos cuántas denuncias anuales debe atender en promedio cada comisaría instalada en el municipio.*
> *- **R7 (Vacíos de Cobertura):** Mapeamos los municipios que registran violencia recurrente pero tienen **cero comisarías de familia**.*
> *Así pasamos de una simple estadística delictiva a una herramienta de diagnóstico de capacidad del Estado."*

---

### 📌 Diapositiva 3: Arquitectura del Sistema y Flujo de Datos
* **Expositor:** **Michael**
* **Acción en pantalla:** Pasar a Diapositiva 3. **Dar un clic sobre el diagrama para abrir el Lightbox Zoom.** Explicar las 4 fases.
* **Discurso exacto:**
> *(Con el diagrama ampliado)*: *"Nuestra arquitectura está diseñada bajo un principio modular y desacoplado en cuatro etapas:*
>
> *1. **Extracción Dual en Paralelo:** Descargamos la data de la Policía y, en paralelo, consumimos la API REST de comisarías mediante paginación automática con limit y offset. Implementamos tolerancia a fallos: si la API se cae o no hay internet, el extractor conmuta automáticamente a una copia local versionada con hash SHA-256.*
> *2. **Control de Calidad Separado:** No mezclamos limpieza con validación. Auditamos la data cruda en las compuertas 1 y 2. Si un archivo viene dañado o sin columnas mandatorias, el pipeline se frena de inmediato.*
> *3. **Armonización por Contrato DANE:** El código municipal DIVIPOLA de 5 dígitos actúa como puente territorial entre ambas fuentes.*
> *4. **Carga Atómica Transaccional:** Cargamos las 6 tablas del Data Warehouse en una única transacción ACID en PostgreSQL. Si algo falla, el motor ejecuta un ROLLBACK total, garantizando que la base nunca quede corrupta.*
>
> *Ahora mi compañero Manrique les explicará cómo garantizamos matemáticamente la calidad y la estructura del modelo dimensional."*
>
> *(Cerrar el Lightbox con la tecla ESC o clic en la X).*

---

## 🟢 BLOQUE 2: CALIDAD, INTEGRACIÓN Y MODELO DIMENSIONAL (Manrique)

### 📌 Diapositiva 4: Control de Calidad Automático con Great Expectations
* **Expositor:** **Manrique**
* **Acción en pantalla:** Pasar a Diapositiva 4. Señalar las 3 compuertas (Gates 1, 2 y 3).
* **Discurso exacto:**
> *"Para garantizar que la base de datos solo reciba información confiable, implementamos 16 reglas de calidad con Great Expectations 1.X, divididas en 3 compuertas automáticas:*
>
> *- **Compuerta 1 (Datos de Policía):** Auditamos las 704,551 filas policiales. Regla crítica `DQ-RAW1-01` valida las 8 columnas obligatorias; `DQ-RAW1-02` exige formato de fecha `DD/MM/YYYY`; y `DQ-RAW1-04` exige que la cantidad de víctimas sea un entero estrictamente mayor o igual a 1. Superó 6 de 6 reglas.*
> *- **Compuerta 2 (API de Comisarías):** Auditamos los 1,249 registros del MinJusticia. Regla crítica `DQ-RAW2-01` valida el schema con la columna obligatoria `existencia_de_comisarias`; `DQ-RAW2-02` valida que el código DANE tenga entre 4 y 5 dígitos; y `DQ-RAW2-04` exige que la cantidad de comisarías sea mayor o igual a cero. Superó 5 de 5 reglas.*
> *- **Compuerta 3 (Datos Preparados):** Se ejecuta justo antes de tocar la base de datos. Regla crítica `DQ-PREP-01` asegura la unicidad del grano atómico; `DQ-PREP-02` y `03` garantizan cero claves huérfanas en dimensiones; y `DQ-PREP-05` ejecuta la reconciliación matemática estricta: suma el total de víctimas en destino y comprueba que sea exactamente 1,501,809. Delta = 0."*

---

### 📌 Diapositiva 5: El Contrato de Integración y la Deduplicación al Grano
* **Expositor:** **Manrique**
* **Acción en pantalla:** Pasar a Diapositiva 5. Señalar las métricas inferiores (2,837 filas colapsadas y 1,501,809 víctimas conservadas).
* **Discurso exacto:**
> *"Al integrar dos fuentes encontramos dos retos técnicos importantes:*
>
> *1. **Heterogeneidad Territorial:** La Policía y la API tenían discrepancias ortográficas en los municipios. Resolvimos esto estandarizando el código DANE a 5 caracteres rellenado con ceros a la izquierda (por ejemplo, convirtiendo `'5001'` en `'05001'` para Medellín). Además, la API reportaba 2 municipios con comisarías pero donde la Policía no tenía denuncias; en lugar de descartarlos, los preservamos en la dimensión geográfica.*
>
> *2. **Deduplicación al Grano Declarado:** Definimos como grano atómico de la tabla de hechos la combinación de: `(Fecha, Municipio, Perfil Demográfico, Arma)`. En el archivo crudo existían **2,837 registros redundantes** que compartían el mismo grano. Si hubiéramos aplicado un `drop_duplicates` genérico, habríamos borrado víctimas.*
> *Lo que hicimos fue agrupar por el grano y ejecutar un `SUM(cantidad_victimas)`. Así colapsamos los 2,837 registros redundantes pero conservamos el 100% de las 1,501,809 víctimas. La información en origen y destino quedó matemáticamente idéntica."*

---

### 📌 Diapositiva 6: Modelo Dimensional en Estrella (Star Schema)
* **Expositor:** **Manrique**
* **Acción en pantalla:** Pasar a Diapositiva 6. **Dar clic en la imagen del esquema para abrir el Lightbox Zoom.**
* **Discurso exacto:**
> *(Con el esquema dimensional ampliado)*: *"Diseñamos un modelo dimensional en estrella en PostgreSQL 16 optimizado para el motor de consultas de Power BI:*
>
> *En el centro se encuentra la tabla de hechos: **`fact_violencia_intrafamiliar`**, con **701,714 filas**, que registra dos métricas fundamentales: `cantidad_victimas` y `numero_registros`.*
>
> *Alrededor gravitan 5 dimensiones conformadas:*
> *- **`dim_tiempo`:** 6,056 filas, con calendario diario desde 2010 hasta 2026, descomponiendo año, mes, trimestre, día de la semana y si es fin de semana.*
> *- **`dim_geografia`:** 1,113 municipios con departamento, categoría municipal y el total de comisarías instaladas.*
> *- **`dim_victima`:** 11 perfiles combinando sexo (`MASCULINO`, `FEMENINO`) y grupo etario (`MENORES`, `ADULTOS`, etc.).*
> *- **`dim_medio`:** 6 mecanismos de agresión (armas contundentes, blancas, de fuego, etc.).*
> *- y **`dim_comisaria`:** 1,247 sedes físicas georreferenciadas del Ministerio de Justicia.*
>
> *Todas las dimensiones utilizan claves sustitutas enteras (Surrogate Keys) con índices B-Tree, permitiendo que Power BI ejecute los joins en milisegundos.*
>
> *A continuación, David les explicará cómo orquestamos este pipeline en Apache Airflow y las pruebas de confiabilidad que ejecutamos."*
>
> *(Cerrar el Lightbox).*

---

## 🟡 BLOQUE 3: AIRFLOW 3, PRUEBAS DE CONFIABILIDAD Y POWER BI (David)

### 📌 Diapositiva 7: Orquestación en Airflow 3 Task SDK y Reintentos
* **Expositor:** **David**
* **Acción en pantalla:** Pasar a Diapositiva 7. Explicar XCom ligero y la tabla comparativa de reintentos.
* **Discurso exacto:**
> *"Para la orquestación implementamos Apache Airflow 3 utilizando el Task SDK con decoradores modernos `@dag` y `@task`, sin código deprecado.*
>
> *Aplicamos dos principios de ingeniería fundamentales:*
> *1. **Patrón XCom Ligero (Claim Check):** Un orquestador no debe saturar su memoria pasando 700,000 filas por XCom. En nuestro diseño, los datos masivos viajan por disco comprimidos en formato Parquet en la carpeta `data/processed/`, y XCom únicamente transporta metadatos ligeros: el `batch_id`, las rutas de los archivos y los hashes SHA-256 de verificación.*
>
> *2. **Política Justificada de Reintentos:** Siguiendo la rúbrica, diferenciamos fallas transitorias de determinísticas:*
> *- En tareas expuestas a la red (`extract_api` y `load_dimensional_dw`) configuramos **2 a 3 reintentos** con tiempo de espera, porque una caída momentánea de HTTP o saturación del pool de base de datos se resuelve sola.*
> *- Pero en las tareas de validación (`validate_primary_raw`, `validate_api_raw`, `validate_prepared`), configuramos **retries=0**. Si un archivo viene corrupto, volverlo a evaluar sobre los mismos datos dará el mismo error; reintentar solo desperdiciaría CPU. Ante un fallo crítico, la tarea lanza `AirflowFailException` y frena el pipeline de inmediato."*

---

### 📌 Diapositiva 8: Pruebas Reales de Confiabilidad en Airflow (A, B y C)
* **Expositor:** **David**
* **Acción en pantalla:** Pasar a Diapositiva 8. **Señalar la tabla comparativa con los estados de las tareas.** Si el docente pide verlo en vivo, dar clic en el botón *"Abrir Webserver ↗"* para abrir `localhost:8080`.
* **Discurso exacto:**
> *"Esta tabla refleja exactamente los estados y tiempos cronometrados en el Web UI de Airflow tras ejecutar las pruebas de confiabilidad obligatorias:*
>
> *- **Test A (Ejecución Exitosa Completa):** Las 7 tareas terminaron en estado verde de `success`. En solo 33 segundos se procesó todo el historial nacional, superando las 3 compuertas y cargando las 701,714 filas en PostgreSQL.*
>
> *- **Test B (Falla Crítica Controlada):** Simulamos la llegada de un lote de la API al que le faltaba la columna obligatoria `existencia_de_comisarias`. Como se ve en la columna de la derecha, `extract_api` terminó en `success`, pero la compuerta `validate_api_raw` detectó la violación crítica y pasó a estado **`failed` (rojo)** tras 6.0 segundos.*
> *Lo más valioso: gracias a la regla de dependencia `all_success`, las tareas downstream (`transform_and_clean_and_integrate`, `validate_prepared` y `load_dimensional_dw`) pasaron automáticamente a **`upstream_failed` (naranja)**. El pipeline se bloqueó y la base de datos no fue tocada, protegiendo al Data Warehouse.*
>
> *- **Test C (Idempotencia y Re-ejecución Segura):** Volvimos a correr el pipeline sobre el mismo lote. Consultamos los conteos en PostgreSQL antes y después: el delta de filas fue exactamente cero en las 6 tablas y no hubo duplicados."*

---

### 📌 Diapositiva 9: Hallazgos en Power BI: Patrones de Violencia (R1 a R4)
* **Expositor:** **David**
* **Acción en pantalla:** Pasar a Diapositiva 9. Puedes hacer clic en cualquiera de las 4 tarjetas para ampliar el gráfico en Lightbox Zoom.
* **Discurso exacto:**
> *"Con el Data Warehouse cargado, conectamos Power BI directamente a las vistas analíticas de PostgreSQL:*
>
> *- **R1 (Evolución Anual):** Observamos una tendencia creciente sostenida desde 2010 (~35k víctimas). El año 2024 marcó el récord histórico con más de 150,000 víctimas reportadas.*
> *- **R2 (Concentración Departamental):** Bogotá D.C. (~22%), Antioquia (~13%), Cundinamarca (~7%), Valle del Cauca (~6%) y Santander (~5%) concentran el 53% de todas las denuncias del país.*
> *- **R3 (Brecha de Género):** El 76.8% de las víctimas son mujeres, presentándose la mayor concentración en mujeres adultas jóvenes de entre 20 y 39 años.*
> *- **R4 (Mecanismos de Agresión):** El 91.4% de los ataques se cometen con elementos contundentes y violencia física directa sin armas de fuego, lo cual confirma que la agresión intrafamiliar ocurre en el ámbito privado y cotidiano.*
>
> *Ahora Torres les expondrá los hallazgos institucionales de las preguntas R5 a R7 y el cierre del proyecto."*

---

## 🟣 BLOQUE 4: CAPACIDAD ESTATAL, APRENDIZAJES Y DEMO (Torres)

### 📌 Diapositiva 10: Capacidad del Estado y Vacíos de Cobertura (R5 a R7)
* **Expositor:** **Torres**
* **Acción en pantalla:** Pasar a Diapositiva 10. Señalar con énfasis las tarjetas R6 (Sobrecarga) y R7 (Municipios Críticos).
* **Discurso exacto:**
> *"Aquí es donde se evidencia el verdadero valor de haber integrado la API del Ministerio de Justicia:*
>
> *- **R5 (Vulnerabilidad en Menores de Edad):** Identificamos más de 160,000 víctimas menores de 18 años, concentrándose en áreas metropolitanas como Bogotá, Medellín, Cali y Soacha.*
>
> *- **R6 (Sobrecarga Operativa de Comisarías):** Dividimos las denuncias anuales entre el número de comisarías del municipio. Municipios como Soacha, Cali y localidades de Bogotá superan los **1,200 casos al año por cada comisaría disponible**. Esto evidencia una saturación extrema del personal psicosocial y jurídico para emitir medidas de protección oportunas.*
>
> *- **R7 (Municipios Críticos sin Comisaría):** Este es el hallazgo de mayor impacto para política pública. Cruzamos los municipios con violencia recurrente contra aquellos donde el número de comisarías es cero. **Identificamos 29 municipios prioritarios que registran violencia activa pero no tienen ni una sola comisaría de familia**.*
> *Este tablero entrega al Ministerio de Justicia una justificación cuantitativa inmediata para priorizar la apertura de nuevas comisarías en esos 29 territorios desatendidos."*

---

### 📌 Diapositiva 11: Limitaciones y Aprendizajes de Ingeniería
* **Expositor:** **Torres**
* **Acción en pantalla:** Pasar a Diapositiva 11. Contrastar limitaciones del dominio con aprendizajes técnicos.
* **Discurso exacto:**
> *"Como ingenieros, debemos ser conscientes de los alcances y limitaciones de la solución:*
>
> *- **Limitaciones del Dominio:** Reconocemos la existencia de la 'cifra negra'. Estos 1.5 millones de víctimas reflejan solo a quienes interpusieron denuncia oficial ante la Policía; en zonas rurales o de conflicto el subregistro es significativo. Además, la API del MinJusticia tiene un desfase de actualización frente a comisarías creadas recientemente.*
>
> *- **Aprendizajes Clave de Ingeniería de Datos:**
>   *1. Diseñar asumiendo el fallo:* En producción la API se caerá o vendrán datos mal formateados. Las compuertas de validación y la transacción atómica fueron la mejor decisión del proyecto.
>   *2. Mantener al orquestador liviano:* Airflow coordina tareas y supervisa estados; no debe procesar tablas masivas en memoria. Parquet en disco y XCom ligero garantizaron estabilidad total.
>   *3. Idempotencia obligatoria:* Un pipeline que no pueda volver a ejecutarse con seguridad ante una falla no está listo para producción."*

---

### 📌 Diapositiva 12: Conclusiones y Demostración en Vivo
* **Expositor:** **Torres**
* **Acción en pantalla:** Pasar a Diapositiva 12. Señalar el cumplimiento de la rúbrica y los servicios en Docker.
* **Discurso exacto:**
> *"Para finalizar, confirmamos el cumplimiento del 100% de los requerimientos de la segunda entrega:*
> *- Repositorio GitHub limpio, documentado y libre de secretos.*
> *- Data Warehouse PostgreSQL 16 con 701,714 hechos y 5 dimensiones conformadas.*
> *- Pruebas de confiabilidad A, B y C documentadas con evidencia JSON en `docs/evidence/`.*
> *- Dashboard en Power BI conectado a las vistas de la base de datos respondiendo a R1-R7.*
>
> *Tanto la base de datos como Airflow están completamente listos y reproducibles en contenedores Docker para cualquier verificación en vivo que deseen realizar.*
>
> *Muchas gracias por su atención. Abrimos el espacio para preguntas."*

---

# 🧠 PARTE 2: Guía de Defensa Técnica Profunda (Para Preguntas Difíciles)

---

## 🛠️ SECCIÓN A: AIRFLOW PROFUNDO & CONTROL DE FALLAS (Para David y Michael)

### ❓ Pregunta 1: "¿Qué falló exactamente en el Test B y cuál fue la secuencia de eventos en Airflow?"
* **Respuesta técnica exacta (David):**
> *"En el Test B ejecutamos el DAG con el parámetro `test_mode="TEST_B_CONTROLLED_FAILURE"`. Este parámetro simula un fallo de contrato en la API de comisarías eliminando la columna obligatoria `existencia_de_comisarias`.*
>
> *La secuencia cronometrada en Airflow fue la siguiente:*
> *1. Las tareas de extracción `extract_primary` (1.6s) y `extract_api` (2.1s) terminaron en **`success`** porque la descarga fue exitosa a nivel de transporte.*
> *2. La compuerta `validate_primary_raw` (2.2s) terminó en **`success`** porque los datos policiales eran correctos.*
> *3. La compuerta `validate_api_raw` evaluó el payload contra la suite `api_raw_suite`. La regla `DQ-RAW2-01` (`expect_table_columns_to_match_set`) detectó que faltaba la columna obligatoria. Al tener severidad **Critical**, el validador marcó `critical_failure=True` y lanzó una excepción `AirflowFailException`.*
> *4. Airflow marcó `validate_api_raw` como **`failed` (rojo)** tras 6.0 segundos.*
> *5. Como las tareas posteriores (`transform_and_clean_and_integrate`, `validate_prepared` y `load_dimensional_dw`) tienen como regla de activación la política por defecto `trigger_rule="all_success"`, Airflow las marcó de inmediato como **`upstream_failed` (naranja)** sin ejecutarlas.*
> *6. Consecuencia: **El Data Warehouse quedó 100% intacto y protegido** contra la inserción de datos corruptos."*

### ❓ Pregunta 2: "¿Por qué usan `AirflowFailException` y no una excepción normal de Python?"
* **Respuesta técnica exacta (David):**
> *"En Apache Airflow, lanzar una excepción estándar como `ValueError` o `Exception` activa la política de reintentos de la tarea si tuviera reintentos configurados. En cambio, `AirflowFailException` le indica explícitamente al worker que se trata de un fallo terminal determinístico que no debe reintentarse bajo ninguna circunstancia, forzando la transición inmediata al estado `failed` y bloqueando las ramas downstream."*

### ❓ Pregunta 3: "¿Por qué usaron Airflow 3 Task SDK en lugar de los operadores tradicionales?"
* **Respuesta técnica exacta (Michael):**
> *"El Task SDK de Airflow 3 reemplaza los operadores monolíticos heredados (`PythonOperator`, `BashOperator`) por decoradores `@dag` y `@task` nativos basados en Python moderno. Esto nos dio tres ventajas:*
> *1. Cero advertencias de funciones deprecadas.*
> *2. Composición funcional directa: pasamos el retorno de una tarea como argumento de la siguiente (`task_transform(val1, val2)`), permitiendo que Airflow infiera automáticamente las dependencias del grafo sin escribir operadores `>>` manuales propensos a error.*
> *3. Pruebas unitarias desacopladas: cada función decorada con `@task` puede probarse fuera de Airflow como una simple función de Python."*

---

## 🔍 SECCIÓN B: CALIDAD AUTOMÁTICA & GREAT EXPECTATIONS (Para Manrique)

### ❓ Pregunta 4: "¿Cuáles son exactamente las 16 reglas de calidad implementadas?"
* **Respuesta técnica exacta (Manrique):**
> *"Están distribuidas en 3 compuertas (Quality Gates):*
>
> *1. **Compuerta 1 (Primary Raw - 6 reglas):**
>    - `DQ-RAW1-01` (Critical): `expect_table_columns_to_match_set` (8 columnas obligatorias presentes).
>    - `DQ-RAW1-02` (Critical): `expect_column_values_to_match_regex` (fechas en formato `DD/MM/YYYY`).
>    - `DQ-RAW1-03` (Critical): `expect_column_value_lengths_to_be_between` (código DANE policial de 8 dígitos).
>    - `DQ-RAW1-04` (Critical): `expect_column_values_to_not_be_null` y `min_value >= 1` (víctimas válidas).
>    - `DQ-RAW1-05` (Warning): `expect_column_values_to_not_be_null` con `mostly=0.99` en género.
>
> *2. **Compuerta 2 (API Raw - 5 reglas):**
>    - `DQ-RAW2-01` (Critical): `expect_table_columns_to_match_set` (columnas obligatorias: código DANE, categoría, comisarías ley 2126 y existencia de comisarías).
>    - `DQ-RAW2-02` (Critical): `expect_column_value_lengths_to_be_between` (DANE de 4 a 5 caracteres).
>    - `DQ-RAW2-03` (Warning): `expect_column_values_to_be_in_set` (categorías válidas: 1 a 6 y Especial).
>    - `DQ-RAW2-04` (Critical): `expect_column_values_to_be_between` (número de comisarías >= 0).
>    - `DQ-RAW2-05` (Warning): `expect_column_values_to_not_be_null` (`mostly=0.9`).
>
> *3. **Compuerta 3 (Prepared Data - 5 reglas de modelo):**
>    - `DQ-PREP-01` (Critical): `expect_compound_columns_to_be_unique` en `(id_tiempo, id_geografia, id_victima, id_medio)`.
>    - `DQ-PREP-02` y `03` (Critical): Integridad referencial en las 4 foreign keys (cero claves huérfanas).
>    - `DQ-PREP-04` (Critical): `comisarias_instaladas >= 0`.
>    - `DQ-PREP-05` (Critical): Reconciliación matemática: suma de `cantidad_victimas` == 1,501,809 y suma de `numero_registros` == 704,551.*
>    - `DQ-PREP-06` (Warning): Validación de áreas no municipalizadas."*

### ❓ Pregunta 5: "¿Cómo garantizan que la reconciliación dio delta cero si las filas cambiaron de 704k a 701k?"
* **Respuesta técnica exacta (Manrique):**
> *"Hay que distinguir entre número de filas de hechos y cantidad de personas víctimas:*
> *- En el dataset crudo había 704,551 filas de denuncias policiales, pero **2,837 compartían exactamente el mismo grano** (misma fecha, municipio, arma y demografía).*
> *- Al consolidar el grano atómico, colapsamos esas filas agrupando y aplicando la función de agregación `SUM(cantidad_victimas)`.*
> *- 704,551 filas crudas menos 2,837 redundantes da exactamente **701,714 filas atómicas en la tabla de hechos**.*
> *- Y al sumar la columna `cantidad_victimas` de las 701,714 filas cargadas en PostgreSQL, el resultado es exactamente **1,501,809 víctimas**, idéntico al total del archivo fuente de la Policía. Delta de víctimas = 0."*

---

## 🏛️ SECCIÓN C: MODELO DIMENSIONAL & CARGA ATÓMICA (Para Manrique y David)

### ❓ Pregunta 6: "¿Cómo implementaron la carga atómica e idempotente en PostgreSQL (Test C)?"
* **Respuesta técnica exacta (David):**
> *"La tarea `load_dimensional_dw` ejecuta un script transaccional en PostgreSQL con el patrón `BEGIN; ... COMMIT;`.*
> *1. Las tablas de hechos y dimensiones temporales se cargan utilizando tablas de staging intermedias.*
> *2. La carga de hechos se realiza con inserción atómica validada por claves sustitutas enteras.*
> *3. Si ocurre cualquier error durante la carga o la verificación, el bloque `EXCEPTION` ejecuta `ROLLBACK` y la base de datos queda en el estado exacto anterior.*
> *4. En el Test C (Idempotencia), re-ejecutamos el pipeline completo sobre el mismo lote. Al consultar los conteos antes y después con `SELECT COUNT(*)`, los deltas fueron exactamente 0 en las 6 tablas y no se duplicó una sola fila."*

### ❓ Pregunta 7: "¿Por qué usaron claves sustitutas (Surrogate Keys) y no el código DANE como clave primaria?"
* **Respuesta técnica exacta (Manrique):**
> *"Porque seguir las mejores prácticas de modelado de Ralph Kimball exige independizar el Data Warehouse de las claves naturales de los sistemas operacionales. Un código DANE es un string alfanumérico que puede cambiar ante reestructuraciones territoriales o divisiones político-administrativas.*
> *Una clave sustituta entera (`BIGSERIAL` o `INT`) indexada con B-Tree ocupa menos espacio en disco, acelera enormemente los `JOIN` en PostgreSQL y optimiza el almacenamiento columnar en el motor VertiPaq de Power BI."*

---

## 📊 SECCIÓN D: POWER BI & PREGUNTAS DE NEGOCIO R1 A R7 (Para Torres y Michael)

### ❓ Pregunta 8: "¿Cómo se calculó la sobrecarga de comisarías (R6) y qué hallazgos arrojó?"
* **Respuesta técnica exacta (Torres):**
> *"En PostgreSQL creamos la vista analítica `vw_r6_sobrecarga_comisarias`, que calcula:*
> `Ratio Sobrecarga = SUM(f.numero_registros) / g.comisarias_instaladas`
>
> *Descubrimos que municipios como Soacha, Cali y localidades densas de Bogotá superan los **1,200 casos al año por cada comisaría disponible**.*
> *La Ley 2126 de 2021 establece que las comisarías deben contar con equipos interdisciplinarios (abogado, psicólogo y trabajador social) para dar seguimiento a cada caso. Un ratio de más de 1,200 denuncias al año significa más de 4 casos diarios nuevos por comisaría, lo que hace humanamente imposible hacer seguimiento efectivo y explica el colapso del sistema."*

### ❓ Pregunta 9: "¿Cómo determinaron los 29 municipios sin comisaría (R7) y qué criterio se usó?"
* **Respuesta técnica exacta (Torres):**
> *"Cruzamos la dimensión geográfica integrada contra la tabla de hechos con la condición:*
> `WHERE g.comisarias_instaladas = 0 AND f.cantidad_victimas > 0`
>
> *Identificamos **29 municipios** que reportan denuncias formales de violencia intrafamiliar ante la Policía pero registran 0 comisarías de familia en el directorio oficial del Ministerio de Justicia.*
> *Este resultado es de alto valor social porque demuestra una vulnerabilidad institucional directa: las víctimas en esos 29 municipios no cuentan con un despacho local para solicitar medidas de protección inmediatas o desalojo del agresor."*

### ❓ Pregunta 10: "¿Power BI se conectó en modo Import o DirectQuery, y por qué?"
* **Respuesta técnica exacta (Torres o Michael):**
> *"Se conectó en modo Importación directa desde PostgreSQL hacia el motor en memoria VertiPaq de Power BI. Con 701,714 filas y claves foráneas enteras indexadas, el modelo pesa menos de 35 MB en el archivo `.pbix` y ofrece interactividad instantánea al filtrar por año, departamento, género o mecanismo sin depender de una conexión activa permanente a la base de datos durante la exposición."*
