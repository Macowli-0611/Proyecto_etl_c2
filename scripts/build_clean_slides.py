"""Script to build the clean, academic, human-written HTML presentation with embedded Base64 images.
Removes all AI badge/pill spam, restores natural engineering language, and embeds all diagrams and Power BI charts.
"""

import base64
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_ROOT = os.path.dirname(PROJECT_ROOT)

images = {
    'workflow': 'docs/Pipeline Workflow ETL-C2.png',
    'dimensional': 'docs/Dimensional Modeling ETL-C2.png',
    'r1': 'docs/powerbi/r1_evolucion_anual.png',
    'r2': 'docs/powerbi/r2_departamentos.png',
    'r3': 'docs/powerbi/r3_genero.png',
    'r4': 'docs/powerbi/r4_mecanismos.png',
    'r5': 'docs/powerbi/r5_mapa_menores.png',
    'r6': 'docs/powerbi/r6_sobrecarga.png',
    'r7': 'docs/powerbi/r7_prioridad.png',
}

b64 = {}
for k, rel in images.items():
    full_p = os.path.join(PROJECT_ROOT, rel)
    with open(full_p, 'rb') as f:
        b64[k] = 'data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')

html_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sustentación Proyecto 2: Pipeline ETL y Data Warehouse de Violencia Intrafamiliar</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #090d16;
      --surface: #111827;
      --surface-elevated: #1a2234;
      --border: #1f293d;
      --border-subtle: #2d3748;
      --primary: #3b82f6;
      --primary-light: #60a5fa;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --font-main: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
      --radius: 8px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: var(--font-main);
      background-color: var(--bg);
      color: var(--text);
      height: 100vh;
      width: 100vw;
      overflow: hidden;
      user-select: none;
      display: flex;
      flex-direction: column;
    }}

    /* Barra Superior */
    header {{
      height: 52px;
      padding: 0 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border);
      background: rgba(9, 13, 22, 0.95);
      backdrop-filter: blur(8px);
      z-index: 50;
    }}

    .header-title {{
      font-size: 0.92rem;
      font-weight: 600;
      color: var(--text);
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .course-badge {{
      font-size: 0.72rem;
      font-family: var(--font-mono);
      color: var(--primary-light);
      background: rgba(59, 130, 246, 0.12);
      border: 1px solid rgba(59, 130, 246, 0.25);
      padding: 2px 8px;
      border-radius: 4px;
    }}

    .header-nav {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .slide-num {{
      font-family: var(--font-mono);
      font-size: 0.82rem;
      color: var(--text-muted);
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 4px 10px;
      border-radius: 4px;
    }}

    .btn-top {{
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-muted);
      height: 32px;
      padding: 0 10px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.82rem;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }}

    .btn-top:hover {{
      color: var(--text);
      border-color: var(--primary);
    }}

    /* Contenedor del Slide Deck */
    #deck {{
      flex: 1;
      position: relative;
      overflow: hidden;
    }}

    .slide {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      padding: 32px 48px;
      display: flex;
      flex-direction: column;
      opacity: 0;
      pointer-events: none;
      transform: translateX(40px);
      transition: opacity 0.3s ease, transform 0.3s ease;
      overflow-y: auto;
    }}

    .slide.active {{
      opacity: 1;
      pointer-events: auto;
      transform: translateX(0);
    }}

    .slide.prev {{
      transform: translateX(-40px);
      opacity: 0;
    }}

    /* Encabezados de Diapositiva */
    .slide-intro {{
      margin-bottom: 24px;
    }}

    .slide-title {{
      font-size: 1.75rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--text);
      margin-bottom: 6px;
    }}

    .slide-desc {{
      font-size: 0.95rem;
      color: var(--text-muted);
      line-height: 1.45;
      max-width: 900px;
    }}

    .slide-content {{
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}

    /* Cuadrículas y Layouts */
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      height: 100%;
    }}

    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
      height: 100%;
    }}

    .grid-4 {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }}

    .grid-media-side {{
      display: grid;
      grid-template-columns: 1.25fr 1fr;
      gap: 24px;
      height: 100%;
    }}

    /* Tarjetas y Bloques */
    .panel {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px;
      display: flex;
      flex-direction: column;
    }}

    .panel-header {{
      font-size: 1.05rem;
      font-weight: 600;
      color: var(--text);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .stat-box {{
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px;
      text-align: center;
    }}

    .stat-number {{
      font-family: var(--font-mono);
      font-size: 1.85rem;
      font-weight: 700;
      color: var(--primary-light);
      margin-bottom: 4px;
    }}

    .stat-desc {{
      font-size: 0.82rem;
      color: var(--text-muted);
    }}

    /* Listas con viñetas limpias */
    .story-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 14px;
      font-size: 0.9rem;
      color: #cbd5e1;
      line-height: 1.5;
    }}

    .story-list li {{
      position: relative;
      padding-left: 20px;
    }}

    .story-list li::before {{
      content: "•";
      position: absolute;
      left: 0;
      color: var(--primary-light);
      font-size: 1.2rem;
      line-height: 1;
      top: 1px;
    }}

    .story-list strong {{
      color: var(--text);
    }}

    /* Tablas Limpias */
    table.clean-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      text-align: left;
    }}

    table.clean-table th {{
      border-bottom: 1px solid var(--border);
      color: var(--text-dim);
      font-weight: 600;
      padding: 8px 12px;
      font-size: 0.78rem;
      text-transform: uppercase;
      font-family: var(--font-mono);
    }}

    table.clean-table td {{
      padding: 10px 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.03);
      color: #cbd5e1;
    }}

    table.clean-table tr:hover td {{
      background: rgba(255, 255, 255, 0.02);
    }}

    /* Visualizador de Imágenes Embebidas */
    .image-card {{
      background: #000;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      position: relative;
      cursor: zoom-in;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      min-height: 220px;
      transition: border-color 0.2s;
    }}

    .image-card:hover {{
      border-color: var(--primary-light);
    }}

    .image-card img {{
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      display: block;
    }}

    .zoom-tag {{
      position: absolute;
      bottom: 8px;
      right: 8px;
      background: rgba(17, 24, 39, 0.85);
      border: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 0.72rem;
      padding: 3px 8px;
      border-radius: 4px;
      pointer-events: none;
    }}

    /* Barra Inferior */
    footer {{
      height: 48px;
      padding: 0 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-top: 1px solid var(--border);
      background: rgba(9, 13, 22, 0.95);
      z-index: 50;
    }}

    .footer-hints {{
      font-size: 0.78rem;
      color: var(--text-dim);
      display: flex;
      gap: 16px;
    }}

    .nav-buttons {{
      display: flex;
      gap: 10px;
    }}

    .btn-nav {{
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text);
      font-size: 0.82rem;
      font-weight: 500;
      padding: 6px 14px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .btn-nav:hover {{
      background: var(--primary);
      border-color: var(--primary);
    }}

    .btn-nav:disabled {{
      opacity: 0.3;
      pointer-events: none;
    }}

    /* Modal Lightbox */
    #lightbox {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(5, 8, 15, 0.95);
      backdrop-filter: blur(8px);
      z-index: 100;
      display: none;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      padding: 24px;
    }}

    #lightbox.active {{
      display: flex;
    }}

    #lightbox img {{
      max-width: 95vw;
      max-height: 88vh;
      object-fit: contain;
      border-radius: var(--radius);
      border: 1px solid var(--border-subtle);
    }}

    #lightbox-caption {{
      margin-top: 12px;
      font-size: 0.9rem;
      color: var(--text-muted);
    }}

    #lightbox-close {{
      position: absolute;
      top: 16px;
      right: 20px;
      background: rgba(255, 255, 255, 0.08);
      border: none;
      color: #fff;
      font-size: 1.4rem;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      cursor: pointer;
    }}

    /* Drawer de Contenidos */
    #drawer {{
      position: fixed;
      top: 52px;
      right: -340px;
      width: 340px;
      height: calc(100vh - 52px);
      background: var(--surface);
      border-left: 1px solid var(--border);
      z-index: 80;
      padding: 20px;
      transition: right 0.25s ease;
      overflow-y: auto;
    }}

    #drawer.open {{
      right: 0;
    }}

    .drawer-title {{
      font-size: 1rem;
      font-weight: 600;
      margin-bottom: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .drawer-item {{
      padding: 8px 10px;
      font-size: 0.85rem;
      color: var(--text-muted);
      border-radius: 4px;
      cursor: pointer;
      display: flex;
      gap: 10px;
      margin-bottom: 4px;
      transition: background 0.15s;
    }}

    .drawer-item:hover {{
      background: rgba(255, 255, 255, 0.04);
      color: var(--text);
    }}

    .drawer-item.active {{
      background: rgba(59, 130, 246, 0.15);
      color: var(--primary-light);
      font-weight: 600;
    }}

    .drawer-num {{
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--text-dim);
    }}
  </style>
</head>
<body>

  <!-- Barra Superior -->
  <header>
    <div class="header-title">
      <span class="course-badge">Taller ETL</span>
      <span>Violencia Intrafamiliar & Comisarías de Familia en Colombia</span>
    </div>
    <div class="header-nav">
      <div class="slide-num" id="slide-num">01 / 12</div>
      <button class="btn-top" id="btn-drawer">☰ Índice</button>
      <button class="btn-top" id="btn-fs">⛶ Pantalla Completa</button>
    </div>
  </header>

  <!-- Contenedor del Slide Deck -->
  <main id="deck">

    <!-- SLIDE 1: PORTADA -->
    <section class="slide active" data-slide="1">
      <div style="height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; max-width: 900px; margin: 0 auto;">
        <span class="course-badge" style="margin-bottom: 16px; font-size: 0.82rem; padding: 4px 12px;">Segunda Entrega • Proyecto de Curso</span>
        <h1 style="font-size: 2.75rem; font-weight: 700; line-height: 1.2; margin-bottom: 16px; color: #fff;">
          Pipeline ETL y Data Warehouse de Violencia Intrafamiliar
        </h1>
        <p style="font-size: 1.15rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 36px; max-width: 800px;">
          Integración entre las denuncias históricas de la Policía Nacional y la capacidad de atención de las Comisarías de Familia del Ministerio de Justicia (API SODA).
        </p>

        <div class="grid-4" style="width: 100%; margin-bottom: 36px;">
          <div class="stat-box">
            <div class="stat-number">704,551</div>
            <div class="stat-desc">Registros de Origen</div>
          </div>
          <div class="stat-box">
            <div class="stat-number" style="color: var(--success);">1,501,809</div>
            <div class="stat-desc">Víctimas Reconciliadas</div>
          </div>
          <div class="stat-box">
            <div class="stat-number" style="color: var(--warning);">1,249</div>
            <div class="stat-desc">Comisarías (API SODA)</div>
          </div>
          <div class="stat-box">
            <div class="stat-number" style="color: #a855f7;">0</div>
            <div class="stat-desc">Pérdida en la Carga (Delta)</div>
          </div>
        </div>

        <div style="font-size: 0.88rem; color: var(--text-dim); display: flex; gap: 20px;">
          <span><strong>Arquitectura:</strong> Airflow 3 • Great Expectations 1.X • PostgreSQL 16 • Power BI</span>
        </div>
      </div>
    </section>

    <!-- SLIDE 2: EL PROBLEMA Y EL ALCANCE -->
    <section class="slide" data-slide="2">
      <div class="slide-intro">
        <h2 class="slide-title">El Problema de Negocio y el Valor de la API</h2>
        <p class="slide-desc">¿Por qué conectar las denuncias de violencia con el directorio de comisarías?</p>
      </div>
      <div class="slide-content">
        <div class="grid-2">
          <div class="panel">
            <div class="panel-header">1. Lo que teníamos (Primera Entrega)</div>
            <ul class="story-list">
              <li><strong>Datos de la Policía Nacional:</strong> 704,551 denuncias entre 2010 y 2026.</li>
              <li><strong>Información disponible:</strong> Fecha del hecho, municipio, edad, sexo de la víctima y tipo de arma utilizada.</li>
              <li><strong>El límite:</strong> Sabíamos con exactitud <em>dónde y cuánto</em> ocurría la violencia, pero no sabíamos si el Estado tenía capacidad instalada para atender a las víctimas en ese territorio.</li>
            </ul>
          </div>

          <div class="panel" style="border-color: rgba(59, 130, 246, 0.4);">
            <div class="panel-header" style="color: var(--primary-light);">2. Lo que logramos al integrar la API SODA</div>
            <ul class="story-list">
              <li><strong>Directorio MinJusticia en tiempo real:</strong> 1,249 sedes de comisarías con su código DANE municipal y modalidad de atención.</li>
              <li><strong>Pregunta R6 (Sobrecarga de Comisarías):</strong> Cruzamos denuncias contra número de sedes. Identificamos municipios desbordados con más de 1,200 casos al año por comisaría.</li>
              <li><strong>Pregunta R7 (Vacíos de Cobertura Institucional):</strong> Cruzamos municipios con violencia activa contra municipios con cero comisarías. Identificamos <strong>29 municipios prioritarios</strong> sin presencia estatal de justicia familiar.</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 3: ARQUITECTURA DEL SISTEMA -->
    <section class="slide" data-slide="3">
      <div class="slide-intro">
        <h2 class="slide-title">Arquitectura del Sistema y Flujo de Datos</h2>
        <p class="slide-desc">Diseño modular con dos ramas de ingesta, compuertas de calidad automáticas y carga atómica en PostgreSQL.</p>
      </div>
      <div class="slide-content">
        <div class="grid-media-side">
          <!-- Imagen -->
          <div class="image-card" onclick="openLightbox('{b64['workflow']}', 'Diagrama de Arquitectura y Pipeline ETL')">
            <img src="{b64['workflow']}" alt="Arquitectura del Pipeline">
            <div class="zoom-tag">🔍 Clic para ampliar diagrama</div>
          </div>

          <!-- Puntos Clave -->
          <div class="panel">
            <div class="panel-header">Flujo de los Datos</div>
            <ul class="story-list">
              <li><strong>Extracción Dual y Resiliente:</strong> Se descarga la data histórica policial y se consulta la API REST de comisarías en vivo. Si no hay internet, se activa un respaldo local sin detener el pipeline.</li>
              <li><strong>Control de Calidad Separado:</strong> No mezclamos limpieza con validación. Primero auditamos la estructura cruda (Gates 1 y 2); si algo viene roto, frena de inmediato.</li>
              <li><strong>Integración por Contrato DANE:</strong> Se cruzan ambas fuentes por el código de 5 dígitos del municipio, manejando discrepancias de nombres y tildes.</li>
              <li><strong>Carga Atómica en Base de Datos:</strong> Se cargan 6 tablas en PostgreSQL en una sola transacción protegida; si algo falla, no se modifica la base de datos.</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 4: CONTROL DE CALIDAD AUTOMÁTICO (GX) -->
    <section class="slide" data-slide="4">
      <div class="slide-intro">
        <h2 class="slide-title">Control de Calidad Automático con Great Expectations</h2>
        <p class="slide-desc">16 reglas formales divididas en 3 compuertas para asegurar que ningún dato corrupto contamine el Data Warehouse.</p>
      </div>
      <div class="slide-content">
        <div class="grid-3">
          <!-- Gate 1 -->
          <div class="panel">
            <div class="panel-header">Compuerta 1: Datos de Policía</div>
            <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 12px;">Auditoría de 704,551 filas crudas antes de transformar.</p>
            <ul class="story-list" style="font-size: 0.84rem; gap: 10px;">
              <li><strong>Completitud de columnas:</strong> Deben venir las 9 variables requeridas.</li>
              <li><strong>Rango de fechas:</strong> Cero fechas futuras y fechas posteriores a 2010.</li>
              <li><strong>Consistencia de víctimas:</strong> Cantidad de personas siempre mayor a cero.</li>
              <li><strong>Formato DANE:</strong> Códigos numéricos de 4 a 5 caracteres.</li>
            </ul>
            <div style="margin-top: auto; padding-top: 10px; font-family: var(--font-mono); font-size: 0.8rem; color: var(--success);">
              ✓ 6 de 6 reglas superadas
            </div>
          </div>

          <!-- Gate 2 -->
          <div class="panel">
            <div class="panel-header">Compuerta 2: Datos de la API</div>
            <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 12px;">Auditoría de 1,249 registros del directorio judicial.</p>
            <ul class="story-list" style="font-size: 0.84rem; gap: 10px;">
              <li><strong>Columna obligatoria:</strong> Presencia de <code>existencia_de_comisarias</code>.</li>
              <li><strong>Sin departamentos nulos:</strong> Cada comisaría debe tener ubicación clara.</li>
              <li><strong>Valores válidos:</strong> Indicador de presencia estrictamente en (SI / NO).</li>
              <li><strong>Volumen mínimo:</strong> Alertar si la API devuelve menos de 1,000 sedes.</li>
            </ul>
            <div style="margin-top: auto; padding-top: 10px; font-family: var(--font-mono); font-size: 0.8rem; color: var(--success);">
              ✓ 5 de 5 reglas superadas
            </div>
          </div>

          <!-- Gate 3 -->
          <div class="panel">
            <div class="panel-header">Compuerta 3: Datos Integrados</div>
            <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 12px;">Verificación previa a la carga al almacén.</p>
            <ul class="story-list" style="font-size: 0.84rem; gap: 10px;">
              <li><strong>Unicidad del grano:</strong> Cero duplicados en la tabla de hechos.</li>
              <li><strong>Integridad referencial:</strong> Cero claves foráneas sin padre en dimensiones.</li>
              <li><strong>Reconciliación matemática:</strong> El total de víctimas en destino debe ser idéntico al de origen (1,501,809).</li>
            </ul>
            <div style="margin-top: auto; padding-top: 10px; font-family: var(--font-mono); font-size: 0.8rem; color: var(--success);">
              ✓ Reconciliación exacta al 100%
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 5: CONTRATO DE INTEGRACIÓN Y LIMPIEZA -->
    <section class="slide" data-slide="5">
      <div class="slide-intro">
        <h2 class="slide-title">El Contrato de Integración y la Limpieza</h2>
        <p class="slide-desc">Cómo resolvimos discrepancias entre fuentes y deduplicamos sin perder información.</p>
      </div>
      <div class="slide-content">
        <div class="grid-2">
          <div class="panel">
            <div class="panel-header">Resolución de Discrepancias</div>
            <ul class="story-list">
              <li><strong>Estandarización DANE:</strong> Se rellenaron los códigos con ceros a la izquierda (<code>05001</code> para Medellín en lugar de <code>5001</code>). Esto resolvió el 100% de los problemas de cruce.</li>
              <li><strong>Tratamiento de Nombres:</strong> Se normalizaron mayúsculas, minúsculas y tildes para evitar duplicados tipográficos entre departamentos.</li>
              <li><strong>Los 2 Municipios Especiales:</strong> La API registraba 2 municipios con comisarías pero donde la Policía no tenía denuncias reportadas. En lugar de descartarlos, los preservamos en la dimensión geográfica para no perder la información institucional del Estado.</li>
            </ul>
          </div>

          <div class="panel">
            <div class="panel-header">Deduplicación al Grano Declarado</div>
            <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 14px; line-height: 1.45;">
              En el dataset crudo existían 2,837 registros redundantes (mismo día, mismo municipio, misma arma y mismo perfil). En lugar de borrarlos a ciegas, se colapsaron sumando el número de personas afectadas.
            </p>
            
            <div class="grid-2" style="margin-top: auto;">
              <div class="stat-box">
                <div class="stat-number" style="color: var(--warning);">2,837</div>
                <div class="stat-desc">Filas Redundantes Colapsadas</div>
              </div>
              <div class="stat-box">
                <div class="stat-number" style="color: var(--success);">1,501,809</div>
                <div class="stat-desc">Víctimas Totales Conservadas (0 pérdida)</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 6: MODELO DIMENSIONAL EN ESTRELLA -->
    <section class="slide" data-slide="6">
      <div class="slide-intro">
        <h2 class="slide-title">Modelo Dimensional en Estrella (Star Schema)</h2>
        <p class="slide-desc">Organización en PostgreSQL con una tabla de hechos central y 5 dimensiones conformadas.</p>
      </div>
      <div class="slide-content">
        <div class="grid-media-side">
          <!-- Imagen -->
          <div class="image-card" onclick="openLightbox('{b64['dimensional']}', 'Modelo Dimensional en Estrella - Data Warehouse')">
            <img src="{b64['dimensional']}" alt="Modelo Dimensional">
            <div class="zoom-tag">🔍 Clic para ampliar esquema</div>
          </div>

          <!-- Detalle de Tablas -->
          <div class="panel">
            <div class="panel-header">Estructura en PostgreSQL</div>
            <table class="clean-table">
              <tr><th>Tabla</th><th>Filas</th><th>Función</th></tr>
              <tr><td><strong>fact_violencia</strong></td><td>701,714</td><td>Métricas aditivas de víctimas y denuncias</td></tr>
              <tr><td><strong>dim_tiempo</strong></td><td>6,056</td><td>Calendario completo de 2010 a 2026</td></tr>
              <tr><td><strong>dim_geografia</strong></td><td>1,113</td><td>Municipios con indicadores de comisarías</td></tr>
              <tr><td><strong>dim_victima</strong></td><td>11</td><td>Perfiles demográficos por sexo y edad</td></tr>
              <tr><td><strong>dim_medio</strong></td><td>6</td><td>Armas y mecanismos agresores</td></tr>
              <tr><td><strong>dim_comisaria</strong></td><td>1,247</td><td>Directorio físico de sedes institucionales</td></tr>
            </table>

            <p style="font-size: 0.82rem; color: var(--text-dim); margin-top: 14px; line-height: 1.4;">
              <strong>Decisión de Ingeniería:</strong> Usamos claves sustitutas enteras (Surrogate Keys) con índices B-Tree para optimizar las consultas analíticas en Power BI.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 7: ORQUESTACIÓN CON AIRFLOW 3 -->
    <section class="slide" data-slide="7">
      <div class="slide-intro">
        <h2 class="slide-title">Orquestación en Airflow 3 Task SDK</h2>
        <p class="slide-desc">Flujo de trabajo declarativo, paso de metadatos ligeros y reintentos selectivos justificados.</p>
      </div>
      <div class="slide-content">
        <div class="grid-2">
          <div class="panel">
            <div class="panel-header">Diseño de Tareas y XCom</div>
            <ul class="story-list">
              <li><strong>Airflow 3 Task SDK:</strong> Se construyó con decoradores <code>@dag</code> y <code>@task</code> sin advertencias de deprecación.</li>
              <li><strong>Transferencia de Datos Limpia:</strong> No usamos XCom para mover tablas completas de 700k registros (lo cual tumbaría el servidor de Airflow). XCom solo transfiere el identificador del lote (<code>batch_id</code>) y rutas de archivos Parquet en disco.</li>
              <li><strong>Visibilidad Operacional:</strong> Cada tarea registra tiempos, volúmenes de entrada y salida, y hashes de control.</li>
            </ul>
          </div>

          <div class="panel">
            <div class="panel-header">Política de Reintentos Basada en el Fallo</div>
            <table class="clean-table" style="margin-bottom: 12px;">
              <tr><th>Tipo de Problema</th><th>Ejemplo</th><th>Estrategia</th></tr>
              <tr>
                <td><strong>Fallo Transitorio</strong></td>
                <td>API SODA ocupada, corte temporal de red.</td>
                <td><strong style="color: var(--primary-light);">3 reintentos con espera exponencial</strong>. Se resuelve solo.</td>
              </tr>
              <tr>
                <td><strong>Fallo Determinístico</strong></td>
                <td>Archivo con columnas faltantes, regla crítica de GX violada.</td>
                <td><strong style="color: var(--danger);">0 reintentos</strong>. Reintentar volverá a fallar; se detiene inmediatamente.</td>
              </tr>
            </table>

            <p style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.4;">
              Ante cualquier violación crítica, la tarea lanza <code>AirflowFailException</code>, bloqueando la carga y manteniendo la base de datos intacta.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 8: PRUEBAS REALES DE CONFIABILIDAD (A, B, C) -->
    <section class="slide" data-slide="8">
      <div class="slide-intro">
        <h2 class="slide-title">Pruebas Reales de Confiabilidad (A, B y C)</h2>
        <p class="slide-desc">Verificación obligatoria de comportamiento ante casos de éxito, fallas y re-ejecuciones.</p>
      </div>
      <div class="slide-content">
        <div class="grid-3">
          <div class="panel">
            <div class="panel-header" style="color: var(--success);">Prueba A: Ejecución Exitosa</div>
            <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 12px;">El pipeline de extremo a extremo con datos correctos.</p>
            <ul class="story-list" style="font-size: 0.84rem; gap: 8px;">
              <li>Tiempo total: <strong>22.20 segundos</strong>.</li>
              <li>Compuertas 1, 2 y 3 superadas al 100%.</li>
              <li>701,714 filas cargadas en PostgreSQL.</li>
              <li>Reconciliación: <strong>0 diferencia de víctimas</strong>.</li>
              <li>Claves huérfanas en dimensiones: <strong>0</strong>.</li>
            </ul>
          </div>

          <div class="panel">
            <div class="panel-header" style="color: var(--danger);">Prueba B: Falla Controlada</div>
            <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 12px;">Inyección de error para probar el freno de emergencia.</p>
            <ul class="story-list" style="font-size: 0.84rem; gap: 8px;">
              <li><strong>Condición:</strong> Eliminamos a propósito la columna obligatoria de comisarías.</li>
              <li>La compuerta 2 detectó la falta y frenó la ejecución.</li>
              <li>Las tareas de transformación y carga quedaron <strong>bloqueadas</strong>.</li>
              <li>La base de datos quedó <strong>100% protegida e intacta</strong>.</li>
            </ul>
          </div>

          <div class="panel">
            <div class="panel-header" style="color: var(--primary-light);">Prueba C: Re-ejecución Segura</div>
            <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 12px;">Ejecución del mismo lote dos veces seguidas (Idempotencia).</p>
            <table class="clean-table" style="font-size: 0.78rem; margin: 8px 0;">
              <tr><th>Métrica</th><th>Antes</th><th>Después</th><th>Delta</th></tr>
              <tr><td>Filas Fact</td><td>701,714</td><td>701,714</td><td><strong>0</strong></td></tr>
              <tr><td>Víctimas</td><td>1,501,809</td><td>1,501,809</td><td><strong>0</strong></td></tr>
              <tr><td>Municipios</td><td>1,113</td><td>1,113</td><td><strong>0</strong></td></tr>
            </table>
            <div style="font-size: 0.8rem; color: var(--success); margin-top: auto;">
              ✓ Cero registros duplicados
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 9: HALLAZGOS POWER BI (R1 A R4) -->
    <section class="slide" data-slide="9">
      <div class="slide-intro">
        <h2 class="slide-title">Hallazgos en Power BI: Patrones de Violencia (R1 a R4)</h2>
        <p class="slide-desc">Visualizaciones construidas a partir de las vistas analíticas del Data Warehouse.</p>
      </div>
      <div class="slide-content">
        <div class="grid-4" style="height: 100%;">
          <!-- R1 -->
          <div class="panel" style="padding: 12px;">
            <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 8px;">R1: Evolución Anual</div>
            <div class="image-card" style="height: 160px; margin-bottom: 8px;" onclick="openLightbox('{b64['r1']}', 'R1: Evolución Histórica de Casos 2010 a 2026')">
              <img src="{b64['r1']}" alt="R1 Evolución">
              <div class="zoom-tag">🔍 Ampliar</div>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.35;">
              Tendencia creciente. El año 2024 marca el récord histórico con más de 150,000 víctimas reportadas.
            </p>
          </div>

          <!-- R2 -->
          <div class="panel" style="padding: 12px;">
            <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 8px;">R2: Departamentos</div>
            <div class="image-card" style="height: 160px; margin-bottom: 8px;" onclick="openLightbox('{b64['r2']}', 'R2: Concentración Departamental de Violencia')">
              <img src="{b64['r2']}" alt="R2 Departamentos">
              <div class="zoom-tag">🔍 Ampliar</div>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.35;">
              Bogotá, Antioquia, Cundinamarca, Valle y Santander concentran casi el 50% de las denuncias de todo el país.
            </p>
          </div>

          <!-- R3 -->
          <div class="panel" style="padding: 12px;">
            <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 8px;">R3: Brecha de Género</div>
            <div class="image-card" style="height: 160px; margin-bottom: 8px;" onclick="openLightbox('{b64['r3']}', 'R3: Distribución por Sexo y Grupos de Edad')">
              <img src="{b64['r3']}" alt="R3 Género">
              <div class="zoom-tag">🔍 Ampliar</div>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.35;">
              El 76.8% de las víctimas son mujeres, con especial concentración en mujeres entre los 20 y 39 años.
            </p>
          </div>

          <!-- R4 -->
          <div class="panel" style="padding: 12px;">
            <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 8px;">R4: Mecanismos</div>
            <div class="image-card" style="height: 160px; margin-bottom: 8px;" onclick="openLightbox('{b64['r4']}', 'R4: Armas y Mecanismos de Agresión')">
              <img src="{b64['r4']}" alt="R4 Armas">
              <div class="zoom-tag">🔍 Ampliar</div>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.35;">
              Más del 90% de los incidentes se cometen con elementos contundentes y violencia física directa sin armas de fuego.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 10: HALLAZGOS POWER BI (R5 A R7) -->
    <section class="slide" data-slide="10">
      <div class="slide-intro">
        <h2 class="slide-title">Capacidad del Estado y Vacíos de Cobertura (R5 a R7)</h2>
        <p class="slide-desc">Respuestas analíticas obtenidas gracias al cruce directo con la API de Comisarías.</p>
      </div>
      <div class="slide-content">
        <div class="grid-3" style="height: 100%;">
          <!-- R5 -->
          <div class="panel">
            <div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 8px;">R5: Menores de Edad</div>
            <div class="image-card" style="height: 220px; margin-bottom: 10px;" onclick="openLightbox('{b64['r5']}', 'R5: Vulnerabilidad Geográfica de Menores de Edad')">
              <img src="{b64['r5']}" alt="R5 Menores">
              <div class="zoom-tag">🔍 Ampliar mapa</div>
            </div>
            <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.4;">
              Identifica los departamentos con mayor cantidad de agresiones contra niñas, niños y adolescentes, ubicando zonas de atención prioritaria.
            </p>
          </div>

          <!-- R6 -->
          <div class="panel" style="border-color: rgba(245, 158, 11, 0.4);">
            <div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 8px; color: var(--warning);">R6: Sobrecarga Institucional</div>
            <div class="image-card" style="height: 220px; margin-bottom: 10px;" onclick="openLightbox('{b64['r6']}', 'R6: Casos Anuales por Cada Comisaría de Familia')">
              <img src="{b64['r6']}" alt="R6 Sobrecarga">
              <div class="zoom-tag">🔍 Ampliar gráfica</div>
            </div>
            <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.4;">
              Municipios como Soacha, Cali y Bogotá registran <strong>más de 1,200 casos al año por cada comisaría</strong>, evidenciando saturación extrema del personal de atención.
            </p>
          </div>

          <!-- R7 -->
          <div class="panel" style="border-color: rgba(239, 68, 68, 0.4);">
            <div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 8px; color: #f87171;">R7: Municipios sin Comisaría</div>
            <div class="image-card" style="height: 220px; margin-bottom: 10px;" onclick="openLightbox('{b64['r7']}', 'R7: Municipios Críticos con Cero Comisarías')">
              <img src="{b64['r7']}" alt="R7 Prioridad">
              <div class="zoom-tag">🔍 Ampliar listado</div>
            </div>
            <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.4;">
              El hallazgo más importante: identificamos <strong>29 municipios con violencia intrafamiliar activa que no tienen ni una sola comisaría de familia</strong>.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 11: LIMITACIONES Y APRENDIZAJES -->
    <section class="slide" data-slide="11">
      <div class="slide-intro">
        <h2 class="slide-title">Limitaciones y Aprendizajes de Ingeniería</h2>
        <p class="slide-desc">Entendimiento crítico de los datos reales y de la arquitectura construida.</p>
      </div>
      <div class="slide-content">
        <div class="grid-2">
          <div class="panel">
            <div class="panel-header">Limitaciones del Dominio</div>
            <ul class="story-list">
              <li><strong>La Cifra Negra:</strong> Los registros reflejan únicamente denuncias oficiales ante la Policía. Existe un subregistro significativo de víctimas que no denuncian por dependencia económica, miedo o lejanía de las autoridades.</li>
              <li><strong>Desfase de la API:</strong> El directorio de comisarías del Ministerio de Justicia se actualiza periódicamente; nuevas sedes creadas recientemente pueden tardar meses en aparecer en datos abiertos.</li>
              <li><strong>Granularidad Diaria:</strong> Aunque tenemos la fecha exacta, los registros policiales no incluyen hora del hecho, limitando el análisis de patrones por franja horaria.</li>
            </ul>
          </div>

          <div class="panel">
            <div class="panel-header">Aprendizajes de Ingeniería de Datos</div>
            <ul class="story-list">
              <li><strong>Diseñar para el fallo:</strong> Un pipeline profesional debe asumir que la red se caerá o que los datos vendrán dañados. La compuerta de validación y la transacción atómica fueron lo más valioso del diseño.</li>
              <li><strong>No saturar el orquestador:</strong> Airflow debe coordinar procesos, no transportar 700k filas en memoria. El uso de Parquet y XCom ligero garantizó estabilidad total.</li>
              <li><strong>Idempotencia obligatoria:</strong> Si un proceso falla a la mitad, debe poder relanzarse sin duplicar datos ni alterar los tableros de BI.</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 12: CONCLUSIONES Y DEMO -->
    <section class="slide" data-slide="12">
      <div class="slide-intro">
        <h2 class="slide-title">Conclusiones y Entorno de Demostración</h2>
        <p class="slide-desc">Resumen del cumplimiento de los entregables y comandos para ejecutar en vivo.</p>
      </div>
      <div class="slide-content">
        <div class="grid-2">
          <div class="panel">
            <div class="panel-header">Resumen de Entregables</div>
            <ul class="story-list">
              <li><strong>Repositorio GitHub:</strong> Completamente independiente, versionado y limpio de credenciales sensibles.</li>
              <li><strong>Data Warehouse:</strong> PostgreSQL 16 contenedorizado con 701,714 filas fact y 5 dimensiones conformadas.</li>
              <li><strong>Confiabilidad Auditada:</strong> Tests A, B y C documentados con evidencia JSON descargable en <code>docs/evidence/</code>.</li>
              <li><strong>Dashboard en Power BI:</strong> Archivo <code>.pbix</code> conectado a las vistas de la base de datos respondiendo de R1 a R7.</li>
            </ul>
          </div>

          <div class="panel" style="background: rgba(0,0,0,0.3);">
            <div class="panel-header" style="color: var(--primary-light);">Comandos para Demo en Vivo</div>
            <div style="font-family: var(--font-mono); font-size: 0.8rem; line-height: 1.6; color: #38bdf8; background: #050811; padding: 14px; border-radius: var(--radius); border: 1px solid var(--border);">
              <span style="color: var(--text-dim);"># 1. Levantar base de datos PostgreSQL</span><br>
              docker compose up -d postgres_dw<br><br>
              <span style="color: var(--text-dim);"># 2. Ejecutar suite de confiabilidad (A, B y C)</span><br>
              python3 src/run_pipeline.py<br><br>
              <span style="color: var(--text-dim);"># 3. Abrir la interfaz de Airflow (Puerto 8080)</span><br>
              docker compose up -d airflow
            </div>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 14px;">
              <strong>Repositorio:</strong> github.com/Macowli-0611/Proyecto_etl_c2 (Rama: <code>main</code>)
            </p>
          </div>
        </div>
      </div>
    </section>

  </main>

  <!-- Barra Inferior -->
  <footer>
    <div class="footer-hints">
      <span>Navegar con las teclas <strong>←</strong> y <strong>→</strong></span>
      <span>•</span>
      <span>Presiona <strong>F</strong> para pantalla completa</span>
      <span>•</span>
      <span>Clic en cualquier imagen para ampliar</span>
    </div>
    <div class="nav-buttons">
      <button class="btn-nav" id="btn-prev">← Anterior</button>
      <button class="btn-nav" id="btn-next">Siguiente →</button>
    </div>
  </footer>

  <!-- Drawer de Índice -->
  <aside id="drawer">
    <div class="drawer-title">
      <span>Tabla de Contenidos</span>
      <button class="btn-top" id="btn-close-drawer">✕</button>
    </div>
    <div id="drawer-items"></div>
  </aside>

  <!-- Lightbox Modal -->
  <div id="lightbox" onclick="closeLightbox()">
    <button id="lightbox-close" onclick="closeLightbox()">✕</button>
    <img id="lightbox-img" src="" alt="Ampliada">
    <div id="lightbox-caption"></div>
  </div>

  <script>
    let currentSlide = 1;
    const slides = document.querySelectorAll('.slide');
    const totalSlides = slides.length;

    const slideNum = document.getElementById('slide-num');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const btnDrawer = document.getElementById('btn-drawer');
    const btnCloseDrawer = document.getElementById('btn-close-drawer');
    const drawer = document.getElementById('drawer');
    const drawerItems = document.getElementById('drawer-items');
    const btnFs = document.getElementById('btn-fs');
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxCaption = document.getElementById('lightbox-caption');

    const titles = [
      "Portada: Pipeline ETL y Data Warehouse",
      "El Problema de Negocio y el Valor de la API",
      "Arquitectura del Sistema y Flujo de Datos",
      "Control de Calidad Automático con GX",
      "El Contrato de Integración y Limpieza",
      "Modelo Dimensional en Estrella (Star Schema)",
      "Orquestación en Airflow 3 Task SDK",
      "Pruebas Reales de Confiabilidad (A, B y C)",
      "Hallazgos en Power BI: Patrones (R1 a R4)",
      "Capacidad del Estado y Vacíos (R5 a R7)",
      "Limitaciones y Aprendizajes de Ingeniería",
      "Conclusiones y Entorno de Demostración"
    ];

    // Build Drawer
    titles.forEach((t, i) => {{
      const div = document.createElement('div');
      div.className = `drawer-item ${{i === 0 ? 'active' : ''}}`;
      div.innerHTML = `<span class="drawer-num">${{String(i + 1).padStart(2, '0')}}</span> <span>${{t}}</span>`;
      div.onclick = () => {{
        goToSlide(i + 1);
        closeDrawer();
      }};
      drawerItems.appendChild(div);
    }});

    function updateView() {{
      slides.forEach((s, idx) => {{
        const n = idx + 1;
        s.classList.remove('active', 'prev');
        if (n === currentSlide) s.classList.add('active');
        else if (n < currentSlide) s.classList.add('prev');
      }});

      slideNum.textContent = `${{String(currentSlide).padStart(2, '0')}} / ${{String(totalSlides).padStart(2, '0')}}`;
      btnPrev.disabled = currentSlide === 1;
      btnNext.disabled = currentSlide === totalSlides;
      btnNext.textContent = currentSlide === totalSlides ? "Fin ✓" : "Siguiente →";

      document.querySelectorAll('.drawer-item').forEach((item, idx) => {{
        item.classList.toggle('active', idx + 1 === currentSlide);
      }});
    }}

    function nextSlide() {{
      if (currentSlide < totalSlides) {{
        currentSlide++;
        updateView();
      }}
    }}

    function prevSlide() {{
      if (currentSlide > 1) {{
        currentSlide--;
        updateView();
      }}
    }}

    function goToSlide(n) {{
      if (n >= 1 && n <= totalSlides) {{
        currentSlide = n;
        updateView();
      }}
    }}

    function toggleDrawer() {{ drawer.classList.toggle('open'); }}
    function closeDrawer() {{ drawer.classList.remove('open'); }}

    function toggleFullscreen() {{
      if (!document.fullscreenElement) {{
        document.documentElement.requestFullscreen().catch(() => {{}});
      }} else {{
        if (document.exitFullscreen) document.exitFullscreen();
      }}
    }}

    function openLightbox(src, caption) {{
      lightboxImg.src = src;
      lightboxCaption.textContent = caption || "";
      lightbox.classList.add('active');
    }}

    function closeLightbox() {{
      lightbox.classList.remove('active');
    }}

    btnPrev.onclick = prevSlide;
    btnNext.onclick = nextSlide;
    btnDrawer.onclick = toggleDrawer;
    btnCloseDrawer.onclick = closeDrawer;
    btnFs.onclick = toggleFullscreen;

    window.addEventListener('keydown', (e) => {{
      if (lightbox.classList.contains('active')) {{
        if (e.key === 'Escape') closeLightbox();
        return;
      }}
      if (drawer.classList.contains('open') && e.key === 'Escape') {{
        closeDrawer();
        return;
      }}

      switch(e.key) {{
        case 'ArrowRight':
        case ' ':
        case 'PageDown':
          e.preventDefault();
          nextSlide();
          break;
        case 'ArrowLeft':
        case 'PageUp':
          e.preventDefault();
          prevSlide();
          break;
        case 'Home':
          e.preventDefault();
          goToSlide(1);
          break;
        case 'End':
          e.preventDefault();
          goToSlide(totalSlides);
          break;
        case 'f':
        case 'F':
          e.preventDefault();
          toggleFullscreen();
          break;
        case 't':
        case 'T':
          e.preventDefault();
          toggleDrawer();
          break;
        case 'Escape':
          closeDrawer();
          break;
      }}
    }});

    updateView();
  </script>
</body>
</html>
'''

# Write to all 3 target files
target_files = [
    os.path.join(PROJECT_ROOT, 'docs', 'presentation', 'index.html'),
    os.path.join(PROJECT_ROOT, 'slides.html'),
    os.path.join(WORKSPACE_ROOT, 'slides.html')
]

for target in target_files:
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f'Wrote {len(html_content)} bytes to {target}')

print('Done! Clean presentation generated in all locations.')
