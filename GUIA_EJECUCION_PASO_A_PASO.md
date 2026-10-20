# Guía de Ejecución Paso a Paso
## Pipeline ETL, Data Warehouse e Integración de API (Segunda Entrega)
### Proyecto: Violencia Intrafamiliar en Colombia e Integración con Directorio de Comisarías de Familia

Esta guía está diseñada para que cualquier evaluador, profesor o ingeniero que clone o descargue este repositorio pueda reproducir el sistema de punta a punta, verificar las compuertas de calidad, poblar el Data Warehouse en PostgreSQL, validar las pruebas de confiabilidad y explorar el Dashboard analítico.

---

## 1. Requisitos Previos del Sistema

Asegúrese de contar con las siguientes herramientas instaladas en su máquina (macOS, Linux o Windows con WSL2):

1. **Docker y Docker Compose:**
   - Docker Engine 24.0+ o Docker Desktop.
   - Debe estar en ejecución para levantar el contenedor de PostgreSQL 16.
2. **Python:**
   - Python 3.10, 3.11, 3.12 o 3.13.
   - Gestor de paquetes `pip`.
3. **Conexión a Internet:**
   - Necesaria durante la primera ejecución para descargar las dependencias de Python y consumir la API pública de Comisarías de Familia de MinJusticia en `datos.gov.co`.

---

## 2. Paso a Paso de Ejecución

### Paso 1: Clonar o Ubicarse en la Carpeta del Proyecto
Abra una terminal y navegue a la carpeta del proyecto de la Segunda Entrega:

```bash
cd /Users/usuario/Desktop/ETLproyecto2/Proyecto_etl_C2
```
*(O la ruta donde haya descargado o clonado la carpeta `Proyecto_etl_C2`)*.

---

### Paso 2: Configurar las Variables de Entorno
El repositorio incluye una plantilla `.env.example` con los parámetros de conexión por defecto del contenedor Docker. Cree el archivo `.env`:

```bash
cp .env.example .env
```

El contenido por defecto de `.env` es:
```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=etl_dw
DB_USER=postgres
DB_PASSWORD=postgres123
API_ENDPOINT=https://www.datos.gov.co/resource/7tuu-upb2.json
API_TIMEOUT_SECONDS=30
PRIMARY_DATA_PATH=data/raw/Reporte_Delito_Violencia_Intrafamiliar_Policia_Nacional.csv
PROCESSED_DATA_DIR=data/processed
LOG_LEVEL=INFO
```

---

### Paso 3: Iniciar la Base de Datos PostgreSQL con Docker
Inicie el servicio de base de datos en segundo plano mediante Docker Compose:

```bash
docker compose up -d
```

Verifique que el contenedor esté activo y saludable:
```bash
docker compose ps
```
*Salida esperada:*
```text
NAME                 IMAGE               COMMAND                  SERVICE       CREATED         STATUS
etl_c2_postgres_dw   postgres:16-alpine  "docker-entrypoint.s…"   postgres_dw   Up (healthy)    0.0.0.0:5432->5432/tcp
```

---

### Paso 4: Instalar las Dependencias de Python
Se recomienda utilizar un entorno virtual (o instalar directamente en su entorno de Python):

```bash
# Opcional: Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

Las dependencias principales instaladas son:
- `pandas>=2.2.0`
- `great-expectations>=1.2.0`
- `sqlalchemy>=2.0.0`
- `psycopg2-binary>=2.9.9`
- `requests>=2.31.0`
- `pyarrow>=15.0.0`
- `apache-airflow>=3.0.0`

---

### Paso 5: Ejecutar el Pipeline y las Pruebas de Confiabilidad (Obligatorio)
Ejecute el runner principal de ingeniería:

```bash
python3 src/run_pipeline.py
```

Este comando ejecuta de manera consecutiva y automatizada las **tres pruebas de confiabilidad obligatorias** requeridas en la Sección 20 del PDF:

1. **TEST A — Ejecución Exitosa de Punta a Punta (Success Path):**
   - Extrae la fuente primaria DIJIN (704.551 filas) y valida su hash SHA-256.
   - Extrae la API de Comisarías de MinJusticia (1.249 comisarías en 1.102 municipios).
   - Ejecuta el perfilamiento estadístico independiente.
   - Aplica la Compuerta 1 de calidad (`validate_primary_raw`) con Great Expectations 1.X.
   - Aplica la Compuerta 2 de calidad (`validate_api_raw`) con Great Expectations 1.X.
   - Transforma e integra ambas fuentes usando el código DANE de 5 dígitos (1.100 municipios cruzados, 11 áreas no municipalizadas integradas sin descartar víctimas).
   - Aplica la Compuerta 3 de calidad (`validate_prepared`) verificando invariantes dimensionales.
   - Realiza la carga masiva mediante streaming `COPY` a PostgreSQL 16.
   - Ejecuta la reconciliación matemática inmediata: **Delta = 0 víctimas**.

2. **TEST B — Falla Crítica Controlada y Bloqueo de Tareas (Controlled Failure):**
   - Inyecta un lote anómalo en la Compuerta 2 de la API eliminando la columna crítica obligatoria `existencia_de_comisarias`.
   - Verifica que Great Expectations detecte la infracción y dispare un error `CRITICAL`.
   - Demuestra que las tareas subsiguientes (`transform_and_clean_and_integrate`, `validate_prepared`, `load_dimensional_dw`) quedan **`BLOCKED (UPSTREAM_FAILED)`**.
   - Confirma que el Data Warehouse queda **completamente protegido** sin sufrir modificaciones ni corrupción.

3. **TEST C — Reejecución Segura e Idempotencia (Safe Rerun):**
   - Toma una instantánea del estado del Data Warehouse.
   - Reejecuta el pipeline completo idéntico sobre la base de datos activa.
   - Demuestra que gracias a las transacciones atómicas y el constraint `CONSTRAINT uq_fact_grano UNIQUE`, no se generan filas duplicadas:
     - Delta de filas de hechos: **0**
     - Delta de víctimas acumuladas: **0**

*Tiempo estimado de ejecución:* ~25 a 35 segundos.

---

### Paso 6: Verificar los Datos en el Data Warehouse con SQL
Puede conectarse a PostgreSQL mediante `psql` para ejecutar las consultas analíticas de R1 a R7:

```bash
docker compose exec postgres_dw psql -U postgres -d etl_dw -f /sql/analytical_queries.sql
```

O si prefiere consultar interactivamente:
```bash
docker compose exec postgres_dw psql -U postgres -d etl_dw
```

Ejemplos de consultas rápidas para verificar en la consola de PostgreSQL:
```sql
-- 1. Verificar totales y conciliación de hechos
SELECT COUNT(*) AS total_hechos, SUM(cantidad_victimas) AS total_victimas, SUM(numero_registros) AS total_reportes
FROM fact_violencia_intrafamiliar;
-- Resultado esperado: 701.714 hechos | 1.501.809 víctimas | 704.551 reportes

-- 2. Consultar R6: Top 5 municipios con mayor sobrecarga por comisaría instalada
SELECT * FROM vw_r6_sobrecarga_comisarias LIMIT 5;

-- 3. Consultar R7: Focos críticos de déficit legal (Ley 2126) y menores atacados con armas letales
SELECT * FROM vw_r7_prioridad_intervencion LIMIT 5;

-- Para salir de psql escriba: \q
```

---

### Paso 7: Lanzar y Explorar el Dashboard Analítico Interactivo
El proyecto incluye un dashboard web interactivo con diseño Glassmorphism y Dark Mode que visualiza los resultados de R1 a R7 directamente desde el Data Warehouse:

```bash
python3 dashboard/server.py
```

Abra su navegador web en:
👉 **`http://localhost:8000`**

En el dashboard podrá interactuar con:
- **KPIs Principales:** Total de víctimas (1.501.809), registros analizados, municipios cubiertos y la **Brecha Nacional de Comisarías (114 faltantes)**.
- **Gráfico R1:** Evolución temporal de víctimas 2010–2025.
- **Gráfico R3:** Distribución por género (77,3% mujeres).
- **Gráfico R4:** Armas y medios empleados (contundentes, armas blancas, de fuego).
- **Gráficos Integrados R6 y R7:**
  - Gráfico de barras de sobrecarga institucional (Cúcuta, Popayán, Bello al frente con más de 16.000 víctimas por comisaría).
  - Gráfico de dispersión cruzando el déficit de comisarías con menores atacados con armas letales (evidenciando la Prioridad 1 Urgente de Cúcuta con 8 comisarías faltantes y 51 menores agredidos).
- **Tabla interactiva de municipios prioritarios.**

*(Para detener el servidor web presione `Ctrl + C` en la terminal).*

---

### Paso 8: Inspeccionar y Probar el DAG de Apache Airflow
El flujo de datos está diseñado con el TaskFlow API de Airflow en `dags/etl_violencia_intrafamiliar_dag.py`.

Para validar que el archivo del DAG sea sintácticamente perfecto y no tenga errores de importación:
```bash
python3 -c "from dags.etl_violencia_intrafamiliar_dag import dag_instance; print('DAG importado exitosamente:', dag_instance.dag_id)"
```

Si dispone de un entorno de Airflow configurado, puede cargar la carpeta `dags/` y probar la ejecución de una tarea individual:
```bash
airflow tasks test etl_violencia_intrafamiliar extract_primary_task 2026-10-20
```

---

### Paso 9: Revisar Evidencias Generadas
Todas las evidencias de ejecución, perfilamiento y pruebas se guardan automáticamente en:
- `docs/evidence/profiling_evidence.json`: Métricas de completitud, unicidad y cobertura geográfica.
- `docs/evidence/test_a_success.json`: Resultados de la ejecución exitosa.
- `docs/evidence/test_b_controlled_failure.json`: Evidencia del bloqueo de tareas ante falla crítica.
- `docs/evidence/test_c_safe_rerun.json`: Evidencia de deltas cero (idempotencia).
- `docs/architecture.png`: Diagrama de arquitectura del sistema.
- `docs/star_schema.png`: Diagrama del modelo estrella relacional.

---

## 3. Solución de Problemas Frecuentes (Troubleshooting)

### Problema 1: El puerto 5432 ya está ocupado por otro servicio de PostgreSQL local
**Causa:** Hay una instancia de PostgreSQL corriendo nativamente en la máquina host.  
**Solución:**
1. Modifique el puerto en `docker-compose.yaml` (ejemplo: cambiar `"5432:5432"` por `"5433:5432"`).
2. Actualice la variable `DB_PORT=5433` en su archivo `.env`.
3. Reinicie el contenedor: `docker compose up -d`.

### Problema 2: Error de autenticación o base de datos en Docker
**Causa:** Existen volúmenes previos de Docker con credenciales antiguas.  
**Solución para reiniciar el contenedor limpiamente:**
```bash
docker compose down -v
docker compose up -d
```
Luego vuelva a ejecutar: `python3 src/run_pipeline.py`.

### Problema 3: Error de conexión a la API de `datos.gov.co` (Timeout o corte de red)
**Causa:** Inestabilidad transitoria del portal público de datos del gobierno.  
**Solución:**
El extractor `src/extract_api.py` implementa un mecanismo de caché local en `data/raw/comisarias_familia_api_raw.json`. Si la red falla temporalmente pero ya se descargó previamente, el sistema utiliza la copia local para garantizar la continuidad del flujo sin interrupciones.

---

## 4. Resumen de Comandos Rápidos

| Acción | Comando |
| :--- | :--- |
| **1. Entorno** | `cp .env.example .env` |
| **2. Base de Datos** | `docker compose up -d` |
| **3. Dependencias** | `pip install -r requirements.txt` |
| **4. Ejecutar Todo** | `python3 src/run_pipeline.py` |
| **5. Consultar DW** | `docker compose exec postgres_dw psql -U postgres -d etl_dw -f /sql/analytical_queries.sql` |
| **6. Dashboard Web** | `python3 dashboard/server.py` $\rightarrow$ Abrir `http://localhost:8000` |
| **7. Parar BD** | `docker compose down` |
