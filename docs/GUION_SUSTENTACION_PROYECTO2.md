# 🎙️ Guion de Sustentación Oficial — Proyecto 2 ETL & Data Warehouse
> **Pipeline Automatizado de Violencia Intrafamiliar y Capacidad Institucional de Comisarías de Familia**  
> **Ecosistema Técnico:** Apache Airflow 3 Task SDK • Great Expectations 1.X • PostgreSQL 16 • Power BI  
> **Duración total recomendada:** 12 a 15 minutos (~3 a 3.5 minutos por compañero).

---

## 👥 Tabla Rápida de Distribución (4 Integrantes)

| Integrante | Diapositivas | Eje Temático | Tiempo Sugerido |
| :--- | :---: | :--- | :---: |
| **Compañero 1** | **Diapos 1, 2 y 3** | Portada, El Problema de Negocio, Valor de la API y Arquitectura Global | ~3:30 min |
| **Compañero 2** | **Diapos 4, 5 y 6** | Calidad Automática (Great Expectations), Contrato DANE y Modelo Estrella | ~3:30 min |
| **Compañero 3** | **Diapos 7, 8 y 9** | Airflow 3 Task SDK, Pruebas de Confiabilidad (A, B, C) y Hallazgos R1 a R4 | ~4:00 min |
| **Compañero 4** | **Diapos 10, 11 y 12** | Impacto Institucional (R5 a R7), Limitaciones, Aprendizajes y Cierre / Demo | ~3:30 min |

---

## ⌨️ Atajos Útiles para la Presentación (`slides.html`)
- **Avanzar Diapositiva:** `Flecha Derecha (→)`, `Espacio` o `Clic en Siguiente`.
- **Retroceder Diapositiva:** `Flecha Izquierda (←)`.
- **Pantalla Completa:** Presionar tecla `F`.
- **Ampliar Diagramas / Gráficas:** Clic directo sobre cualquier imagen para activar el **Lightbox Zoom**.
- **Cambiar Tema de Color:** Botones en la esquina superior derecha (`1`: Tono Medio Slate, `2`: Platino, `3`: Claro, `4`: Oscuro).

---

# 🗣️ Guion Detallado Diapositiva por Diapositiva

---

## 🔵 BLOQUE 1: CONTEXTO, NEGOCIO Y ARQUITECTURA (Compañero 1)

### 📌 Diapositiva 1: Portada y Presentación del Proyecto
* **Acción en pantalla:** Mantener la portada visible. Señalar las 4 métricas numéricas centrales.
* **Lo que debes decir:**
> *"Buenos días / tardes, profesor y compañeros. Hoy les vamos a presentar la segunda entrega de nuestro proyecto de Ingeniería de Datos. Nuestro objetivo fue construir un pipeline ETL automatizado y robusto que conecta el histórico de violencia intrafamiliar en Colombia con la capacidad de respuesta institucional del Estado.*
>
> *Para poner esto en perspectiva técnica, el sistema procesa más de 704,000 denuncias policiales, reconcilia matemáticamente a más de 1.5 millones de víctimas y cruza esta información en tiempo real con las 1,249 comisarías de familia del Ministerio de Justicia a través de una API REST pública.*
>
> *Todo el flujo corre de forma automatizada sobre Docker con Apache Airflow 3, con compuertas de calidad automáticas en Great Expectations y un Data Warehouse en PostgreSQL modelado en estrella para responder a 7 preguntas analíticas clave en Power BI."*

---

### 📌 Diapositiva 2: El Problema de Negocio y el Aporte de la API SODA
* **Acción en pantalla:** Pasar a Diapositiva 2. Contrastar columna izquierda ("Lo que teníamos") con columna derecha ("Lo que logramos").
* **Lo que debes decir:**
> *"En la primera entrega analizamos únicamente los datos de la Policía Nacional. Sabíamos con exactitud dónde, cuándo y con qué frecuencia ocurrían las agresiones. Sin embargo, teníamos una limitación analítica de fondo: saber que un municipio tiene 500 denuncias al año no nos decía si el Estado tenía capacidad instalada para proteger a esas personas o si las comisarías estaban colapsadas.*
>
> *Por eso, para esta segunda entrega incorporamos la API SODA de Datos Abiertos del Ministerio de Justicia, que contiene el directorio georreferenciado de todas las comisarías de familia del país.*
>
> *Con esta integración logramos resolver dos preguntas estratégicas que antes eran imposibles de responder: primero, la sobrecarga operativa, midiendo cuántos casos de violencia le tocan al año a cada comisaría; y segundo, el vacío institucional, identificando exactamente cuáles municipios del país registran violencia activa pero no cuentan con una sola comisaría de familia. Pasamos de un análisis meramente policial a un diagnóstico de capacidad estatal."*

---

### 📌 Diapositiva 3: Arquitectura del Sistema y Flujo de Datos
* **Acción en pantalla:** Pasar a Diapositiva 3. Dar un clic sobre la imagen del diagrama de flujo para abrir el Lightbox Zoom. Explicar las 4 etapas.
* **Lo que debes decir:**
> *(Con el diagrama ampliado)*: *"Nuestra arquitectura está diseñada bajo un principio modular y desacoplado de cuatro etapas:*
>
> *1. Extracción Dual en Paralelo: Por un lado descargamos el registro histórico primario de la Policía y, al mismo tiempo, consumimos la API REST de comisarías con paginación automática. Diseñamos un mecanismo de tolerancia a fallos: si la API se cae o no hay internet, el extractor conmuta a una copia local versionada con hash SHA-256.*
>
> *2. Control de Calidad Separado: No mezclamos validación con transformación. Antes de limpiar cualquier dato, sometemos cada fuente a compuertas de calidad independientes.*
>
> *3. Armonización por Código DANE: Convertimos los códigos municipales a un estándar de 5 dígitos para hacer el cruce exacto entre ambas fuentes sin depender de nombres que vienen mal escritos.*
>
> *4. Carga Atómica Transaccional: El Data Warehouse se carga bajo una única transacción ACID en PostgreSQL. Si una sola tabla llega a fallar, el motor ejecuta un rollback total, evitando que la base quede corrupta o a medio llenar.*
>
> *Ahora mi compañero les explicará cómo garantizamos matemáticamente que los datos no lleguen corruptos a la base de datos."*
>
> *(Cerrar el Lightbox con la tecla ESC o dando clic en la X).*

---

## 🟢 BLOQUE 2: CALIDAD, INTEGRACIÓN Y MODELO DIMENSIONAL (Compañero 2)

### 📌 Diapositiva 4: Control de Calidad Automático con Great Expectations
* **Acción en pantalla:** Pasar a Diapositiva 4. Señalar las 3 compuertas (Gates 1, 2 y 3).
* **Lo que debes decir:**
> *"Para garantizar la confiabilidad del sistema implementamos Great Expectations 1.X, configurando 16 reglas de calidad organizadas en tres compuertas automáticas:*
>
> *En la Compuerta 1 auditamos el dataset crudo de la Policía: verificamos que existan las 9 columnas obligatorias, que ninguna fecha sea futura y que la cantidad de víctimas sea siempre un entero positivo.*
>
> *En la Compuerta 2 evaluamos la respuesta de la API del MinJusticia: controlamos que la columna existencia_de_comisarias esté presente, que los valores sean válidos y que el volumen devuelto supere al menos las 1,000 sedes para detectar respuestas truncadas del servidor.*
>
> *Y en la Compuerta 3, que se ejecuta justo antes de tocar el Data Warehouse, evaluamos la integridad de los datos integrados: cero claves foráneas huérfanas, unicidad del grano y reconciliación matemática. El resultado fue un 100% de reglas superadas y un delta de víctimas exactamente igual a cero."*

---

### 📌 Diapositiva 5: El Contrato de Integración y la Deduplicación al Grano
* **Acción en pantalla:** Pasar a Diapositiva 5. Señalar las dos métricas inferiores (2,837 filas colapsadas y 1,501,809 víctimas conservadas).
* **Lo que debes decir:**
> *"Integrar dos fuentes distintas siempre genera discrepancias. Aquí resolvimos dos problemas de ingeniería fundamentales:*
>
> *El primero fue la heterogeneidad territorial: la Policía y la API tenían discrepancias ortográficas en los municipios. Resolvimos esto utilizando el código DIVIPOLA del DANE rellenado a 5 dígitos con ceros a la izquierda (por ejemplo, asegurando que Medellín fuera siempre '05001' y no '5001'). Además, identificamos 2 municipios que tenían comisarías pero 0 denuncias policiales; en lugar de descartarlos, los preservamos en la dimensión geográfica.*
>
> *El segundo reto fue la deduplicación al grano declarado. En el archivo crudo existían 2,837 filas que compartían exactamente la misma fecha, municipio, arma y demografía. Si las hubiéramos eliminado con un simple drop_duplicates, habríamos destruido información de víctimas.*
>
> *Lo que hicimos fue agrupar por el grano atómico y sumarizar el conteo de personas. Así colapsamos los 2,837 registros redundantes pero conservamos el 100% de las 1,501,809 víctimas. La matemática de origen y destino quedó idéntica."*

---

### 📌 Diapositiva 6: Modelo Dimensional en Estrella (Star Schema)
* **Acción en pantalla:** Pasar a Diapositiva 6. Dar clic en la imagen del esquema dimensional para ampliarla con Lightbox Zoom.
* **Lo que debes decir:**
> *(Con el esquema dimensional ampliado)*: *"Con los datos limpios y validados, diseñamos un modelo dimensional en estrella en PostgreSQL 16 optimizado para el motor de Power BI.*
>
> *En el centro tenemos la tabla de hechos: fact_violencia_intrafamiliar, con 701,714 filas atómicas y métricas de cantidad de víctimas y cantidad de denuncias.*
>
> *Alrededor tenemos 5 dimensiones conformadas:*
> *- dim_tiempo, con un calendario continuo de 6,056 días entre 2010 y 2026.*
> *- dim_geografia, con los 1,113 municipios del país y la cantidad total de comisarías en cada uno.*
> *- dim_victima, que normaliza los perfiles demográficos por género y grupo etario.*
> *- dim_medio, con los 6 mecanismos o armas de agresión.*
> *- y dim_comisaria, con el directorio detallado de las 1,247 sedes físicas del MinJusticia.*
>
> *Todas las dimensiones utilizan claves sustitutas enteras (Surrogate Keys) con índices B-Tree, garantizando que los filtros en Power BI respondan de manera instantánea.*
>
> *A continuación, mi compañero les mostrará cómo orquestamos esto en Apache Airflow y las pruebas de falla que realizamos."*
>
> *(Cerrar el Lightbox).*

---

## 🟡 BLOQUE 3: AIRFLOW 3, PRUEBAS DE CONFIABILIDAD Y POWER BI (Compañero 3)

### 📌 Diapositiva 7: Orquestación en Airflow 3 Task SDK y Reintentos
* **Acción en pantalla:** Pasar a Diapositiva 7. Explicar el concepto de XCom ligero y la tabla de reintentos.
* **Lo que debes decir:**
> *"El pipeline completo está orquestado con Apache Airflow 3 utilizando el Task SDK moderno con decoradores @dag y @task, sin código deprecado.*
>
> *Aplicamos dos principios clave de arquitectura:*
> *Primero: XCom Ligero. En producción, un orquestador no debe saturar su memoria RAM pasando tablas de 700,000 filas entre tareas. Por eso, nuestros datos viajan almacenados en disco en formato Parquet, y XCom únicamente transporta metadatos ligeros: las rutas de los archivos y los hashes SHA-256 de auditoría.*
>
> *Segundo: Política Justificada de Reintentos. Diferenciamos las fallas transitorias de las determinísticas:*
> *- Si la API o la base de datos sufren un parpadeo de red, aplicamos de 2 a 3 reintentos automáticos con espera.*
> *- Pero si una compuerta de validación detecta datos corruptos o columnas faltantes, configuramos retries=0. ¿Por qué? Porque volver a validar el mismo archivo corrupto dará el mismo error. En ese caso, Airflow lanza de inmediato una AirflowFailException y frena todo el pipeline."*

---

### 📌 Diapositiva 8: Pruebas Reales de Confiabilidad en Airflow (A, B y C)
* **Acción en pantalla:** Pasar a Diapositiva 8. **Esta diapositiva es clave.** Señalar la tabla comparativa con los estados de las tareas. Si el profesor lo pide, dar clic en "Abrir Webserver ↗" para ir a `http://localhost:8080`.
* **Lo que debes decir:**
> *"Esta tabla que ven aquí refleja exactamente lo que se ve en la interfaz de Airflow en localhost:8080 tras ejecutar las pruebas de confiabilidad exigidas por la rúbrica:*
>
> *En la Corrida 1 (Test A - Éxito Completo), pueden ver que las 7 tareas terminaron en estado verde de success. En solo 33 segundos se procesó todo el historial nacional y se cargaron las 701,714 filas en el Data Warehouse.*
>
> *En la Corrida 2 (Test B - Falla Controlada), simulamos la llegada de un lote corrupto de la API al que le faltaba la columna obligatoria existencia_de_comisarias. Como ven en la tabla, la tarea extract_api fue exitosa, pero la tarea validate_api_raw detectó la violación crítica y pasó a estado failed en rojo.*
>
> *Lo más importante: las tres tareas downstream (transformar, validar preparados y cargar el DW) pasaron automáticamente a upstream_failed en naranja. El freno de emergencia funcionó y la base de datos no fue tocada.*
>
> *Y en el Test C (Idempotencia), re-ejecutamos el pipeline sobre el mismo lote y verificamos que los conteos de la base de datos se mantuvieran exactamente iguales: delta cero y cero filas duplicadas."*

---

### 📌 Diapositiva 9: Hallazgos en Power BI: Patrones de Violencia (R1 a R4)
* **Acción en pantalla:** Pasar a Diapositiva 9. Puedes hacer clic en cualquiera de las 4 tarjetas para abrir el gráfico en grande con Lightbox Zoom.
* **Lo que debes decir:**
> *"Con el Data Warehouse cargado, conectamos Power BI directamente a las vistas analíticas para resolver las preguntas de negocio:*
>
> *- R1 (Evolución Anual): Observamos una tendencia creciente sostenida. El año 2024 registró el récord histórico con más de 150,000 víctimas reportadas.*
> *- R2 (Concentración Departamental): Bogotá, Antioquia, Cundinamarca, Valle del Cauca y Santander concentran casi el 50% de todas las denuncias del país.*
> *- R3 (Brecha de Género): El 76.8% de las víctimas son mujeres, presentándose la mayor concentración en mujeres adultas jóvenes de entre 20 y 39 años.*
> *- R4 (Mecanismos de Agresión): Más del 90% de los ataques se cometen con elementos contundentes y agresión física directa sin armas de fuego, lo cual caracteriza la naturaleza íntima y cotidiana de este flagelo.*
>
> *Ahora mi compañero les expondrá los hallazgos institucionales logrados gracias a la API y el cierre del proyecto."*

---

## 🟣 BLOQUE 4: CAPACIDAD ESTATAL, APRENDIZAJES Y DEMO (Compañero 4)

### 📌 Diapositiva 10: Capacidad del Estado y Vacíos de Cobertura (R5 a R7)
* **Acción en pantalla:** Pasar a Diapositiva 10. Señalar con especial énfasis las tarjetas R6 (Sobrecarga) y R7 (Municipios Críticos).
* **Lo que debes decir:**
> *"Aquí es donde se hace evidente el valor de haber integrado la API de Comisarías de Familia:*
>
> *- En la pregunta R5 mapeamos la vulnerabilidad en menores de edad, identificando los municipios metropolitanos donde niñas, niños y adolescentes sufren mayor proporción de agresiones intrafamiliares.*
>
> *- En la pregunta R6 evaluamos la sobrecarga operativa: dividimos las denuncias anuales entre el número de comisarías del municipio. Encontramos que ciudades como Soacha, Cali y localidades de Bogotá superan los 1,200 casos al año por cada comisaría disponible. Esto demuestra un colapso evidente de los equipos psicosociales y jurídicos encargados de emitir medidas de protección.*
>
> *- Y en la pregunta R7 obtuvimos el hallazgo de mayor impacto: cruzamos los municipios con violencia recurrente contra aquellos donde el número de comisarías es cero. El resultado fue la identificación de 29 municipios prioritarios donde existen agresiones activas pero no existe presencia institucional de justicia familiar.*
>
> *Este tablero entrega una justificación cuantitativa directa para que el Ministerio de Justicia priorice la apertura de nuevas comisarías en esos 29 territorios."*

---

### 📌 Diapositiva 11: Limitaciones y Aprendizajes de Ingeniería
* **Acción en pantalla:** Pasar a Diapositiva 11. Contrastar las limitaciones de los datos reales con los aprendizajes técnicos.
* **Lo que debes decir:**
> *"Como ingenieros, debemos ser críticos respecto a las limitaciones y alcances de nuestro sistema:*
>
> *Del lado del dominio de negocio, reconocemos la existencia de la 'cifra negra': estos 1.5 millones de víctimas corresponden únicamente a quienes tuvieron el valor y los medios de interponer una denuncia oficial; el subregistro en zonas rurales o de conflicto sigue siendo alto. Además, la API del MinJusticia tiene un desfase de actualización frente a las sedes creadas recientemente.*
>
> *Del lado de la Ingeniería de Datos, nuestros mayores aprendizajes fueron:*
> *1. Diseñar pensando siempre en el fallo: Asumir que la API se va a caer o que el archivo vendrá incompleto nos obligó a implementar compuertas automáticas y transacciones atómicas.*
> *2. Mantener al orquestador liviano: Airflow no es una base de datos ni una herramienta de procesamiento masivo en memoria; su rol es coordinar y supervisar.*
> *3. La idempotencia no es opcional: Cualquier pipeline debe soportar re-ejecuciones múltiples sobre el mismo lote sin alterar los tableros analíticos."*

---

### 📌 Diapositiva 12: Conclusiones y Demostración en Vivo
* **Acción en pantalla:** Pasar a Diapositiva 12. Señalar el cumplimiento de la rúbrica y los servicios corriendo en Docker.
* **Lo que debes decir:**
> *"Para concluir, confirmamos el cumplimiento del 100% de los requerimientos de la segunda entrega:*
> *- Repositorio GitHub versionado, estructurado y libre de contraseñas sensibles.*
> *- Data Warehouse en estrella en PostgreSQL 16 con 701,714 hechos y 5 dimensiones conformadas.*
> *- Pruebas de confiabilidad A, B y C documentadas con evidencia JSON en el repositorio.*
> *- Y Dashboard en Power BI (.pbix) con 7 visualizaciones analíticas conectadas en vivo.*
>
> *Tanto la base de datos como Apache Airflow están corriendo actualmente en nuestros contenedores locales, listos para cualquier demostración en vivo o consulta que deseen realizar.*
>
> *Muchas gracias por su atención. Quedamos a su disposición para resolver cualquier pregunta."*

---

# 🧠 Banco de Preguntas Frecuentes del Evaluador (Para que no los corchen)

### ❓ P1: "¿Cómo garantizan que al integrar ambas fuentes no se duplicaron víctimas?"
* **Quién responde:** Compañero 2.
* **Respuesta clave:**
> *"Lo garantizamos en dos niveles: en la transformación y en la Compuerta 3 de Great Expectations. Declaramos un grano atómico (Fecha, Municipio, Perfil y Arma). Cuando existían filas repetidas en el archivo crudo, agrupamos por el grano y sumarizamos el campo de cantidad de víctimas en lugar de descartar filas. Luego, la Compuerta 3 ejecuta una prueba de reconciliación matemática estricta: suma el total de víctimas del archivo crudo (1,501,809) y lo compara contra la suma en la tabla de hechos. Si la diferencia es distinta de cero, el pipeline aborta. El delta fue exactamente cero."*

---

### ❓ P2: "¿Por qué tienen retries=0 en las compuertas de validación de Airflow?"
* **Quién responde:** Compañero 3.
* **Respuesta clave:**
> *"Porque diferenciamos fallos transitorios de fallos determinísticos. Si una API falla por un timeout de red, tiene sentido reintentar porque la red se puede recuperar sola. Pero si Great Expectations detecta que al archivo le falta una columna obligatoria o que hay tipos de datos corruptos, reintentar 3 veces sobre el mismo archivo va a arrojar exactamente el mismo error, desperdiciando recursos de cómputo y retrasando la alerta. Por eso, en validación de datos determinísticos configuramos 0 reintentos y lanzamos AirflowFailException de inmediato."*

---

### ❓ P3: "¿Qué pasa si la API del MinJusticia se cae durante la ejecución?"
* **Quién responde:** Compañero 1 o 3.
* **Respuesta clave:**
> *"El extractor de la API tiene dos mecanismos de defensa: primero, tiene 3 reintentos automáticos con espera de 2 minutos para absorber caídas momentáneas del servidor de Socrata. Y segundo, si tras los reintentos la API sigue sin responder, el pipeline cuenta con un mecanismo de fallback que lee automáticamente una copia local versionada en Parquet validada con hash SHA-256, garantizando que el pipeline nunca detenga la carga del Data Warehouse por indisponibilidad externa."*

---

### ❓ P4: "¿Cómo comprobaron la idempotencia en la base de datos (Test C)?"
* **Quién responde:** Compañero 2 o 3.
* **Respuesta clave:**
> *"Ejecutamos el pipeline completo dos veces seguidas sobre el mismo lote de datos. Antes y después de la segunda corrida, ejecutamos consultas SQL de conteo (`SELECT COUNT(*)`) sobre las 6 tablas del Data Warehouse. Comprobamos que el delta fue exactamente 0 en todas las tablas y que no se generó una sola fila duplicada ni en hechos ni en dimensiones, gracias al uso de staging intermedio y transacciones atómicas."*

---

### ❓ P5: "¿Por qué Power BI se conecta al Data Warehouse y no a los archivos Parquet directamente?"
* **Quién responde:** Compañero 4.
* **Respuesta clave:**
> *"Porque el Data Warehouse en PostgreSQL centraliza la lógica de negocio, las claves sustitutas, la integridad referencial y las vistas analíticas. Si conectáramos Power BI a archivos dispersos, la lógica de joins y agregaciones quedaría acoplada a la herramienta de visualización. Con el modelo en estrella en la base de datos, cualquier otra herramienta futura (como Tableau, Looker o Python) consume la misma versión única y confiable de la verdad."*
