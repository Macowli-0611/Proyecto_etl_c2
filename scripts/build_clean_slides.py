"""Script to build the modern academic light-theme HTML presentation.
Features:
- Crisp, professional academic light design (with theme toggle support)
- Perfectly balanced cards with zero empty vertical voids
- 100% embedded Base64 images (Workflow, Dimensional Model, Power BI R1-R7)
- Natural, human, non-robotic engineering explanations
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
<html lang="es" data-theme="medium">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sustentación: Pipeline ETL y Data Warehouse de Violencia Intrafamiliar</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root, [data-theme="medium"] {{
      --bg: #222a36;
      --bg-alt: #1a222d;
      --surface: #2d3747;
      --surface-hover: #364254;
      --border: #3f4e64;
      --border-focus: #38bdf8;
      --text: #ffffff;
      --text-muted: #cbd5e1;
      --text-dim: #94a3b8;
      --primary: #38bdf8;
      --primary-bg: rgba(56, 189, 248, 0.15);
      --primary-border: rgba(56, 189, 248, 0.4);
      --success: #34d399;
      --success-bg: rgba(52, 211, 153, 0.15);
      --success-border: rgba(52, 211, 153, 0.4);
      --warning: #fbbf24;
      --warning-bg: rgba(251, 191, 36, 0.15);
      --warning-border: rgba(251, 191, 36, 0.4);
      --danger: #f87171;
      --danger-bg: rgba(248, 113, 113, 0.15);
      --danger-border: rgba(248, 113, 113, 0.4);
      --font-main: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.25);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.35);
      --radius: 10px;
    }}

    [data-theme="slate-light"] {{
      --bg: #dbe2ea;
      --bg-alt: #cfd8e3;
      --surface: #edf2f7;
      --surface-hover: #e2e8f0;
      --border: #b8c4d4;
      --border-focus: #2563eb;
      --text: #0f172a;
      --text-muted: #334155;
      --text-dim: #64748b;
      --primary: #1d4ed8;
      --primary-bg: rgba(37, 99, 235, 0.12);
      --primary-border: rgba(37, 99, 235, 0.3);
      --success: #059669;
      --success-bg: rgba(5, 150, 105, 0.12);
      --success-border: rgba(5, 150, 105, 0.3);
      --warning: #b45309;
      --warning-bg: rgba(180, 83, 9, 0.12);
      --warning-border: rgba(180, 83, 9, 0.3);
      --danger: #b91c1c;
      --danger-bg: rgba(185, 28, 28, 0.12);
      --danger-border: rgba(185, 28, 28, 0.3);
      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.15);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }}

    [data-theme="light"] {{
      --bg: #f8fafc;
      --bg-alt: #f1f5f9;
      --surface: #ffffff;
      --surface-hover: #f8fafc;
      --border: #e2e8f0;
      --border-focus: #3b82f6;
      --text: #0f172a;
      --text-muted: #475569;
      --text-dim: #64748b;
      --primary: #2563eb;
      --primary-bg: #eff6ff;
      --primary-border: #bfdbfe;
      --success: #059669;
      --success-bg: #ecfdf5;
      --success-border: #a7f3d0;
      --warning: #d97706;
      --warning-bg: #fffbeb;
      --warning-border: #fde68a;
      --danger: #dc2626;
      --danger-bg: #fef2f2;
      --danger-border: #fecaca;
      --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }}

    [data-theme="dark"] {{
      --bg: #0b0f19;
      --bg-alt: #131926;
      --surface: #182030;
      --surface-hover: #202b3f;
      --border: #243046;
      --border-focus: #60a5fa;
      --text: #f8fafc;
      --text-muted: #cbd5e1;
      --text-dim: #94a3b8;
      --primary: #3b82f6;
      --primary-bg: #172554;
      --primary-border: #1e40af;
      --success: #10b981;
      --success-bg: #064e3b;
      --success-border: #047857;
      --warning: #f59e0b;
      --warning-bg: #451a03;
      --warning-border: #b45309;
      --danger: #ef4444;
      --danger-bg: #450a0a;
      --danger-border: #b91c1c;
      --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
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
      transition: background-color 0.2s ease, color 0.2s ease;
    }}

    /* Barra Superior */
    header {{
      height: 56px;
      padding: 0 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border);
      background: var(--surface);
      box-shadow: var(--shadow-sm);
      z-index: 50;
    }}

    .header-brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--text);
    }}

    .course-tag {{
      background: var(--primary-bg);
      color: var(--primary);
      border: 1px solid var(--primary-border);
      font-family: var(--font-mono);
      font-size: 0.75rem;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 6px;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .slide-badge {{
      font-family: var(--font-mono);
      font-size: 0.85rem;
      color: var(--text-muted);
      background: var(--bg-alt);
      border: 1px solid var(--border);
      padding: 4px 12px;
      border-radius: 6px;
      font-weight: 500;
    }}

    .btn-top {{
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-muted);
      height: 34px;
      padding: 0 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.82rem;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }}

    .btn-top:hover {{
      color: var(--primary);
      border-color: var(--primary-border);
      background: var(--primary-bg);
    }}

    /* Contenedor Principal del Deck */
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
      transform: translateX(30px);
      transition: opacity 0.25s ease, transform 0.25s ease;
      overflow-y: auto;
    }}

    .slide.active {{
      opacity: 1;
      pointer-events: auto;
      transform: translateX(0);
    }}

    .slide.prev {{
      transform: translateX(-30px);
      opacity: 0;
    }}

    /* Encabezados de Slide */
    .slide-header {{
      margin-bottom: 24px;
    }}

    .slide-title {{
      font-size: 1.85rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: var(--text);
      line-height: 1.2;
      margin-bottom: 6px;
    }}

    .slide-subtitle {{
      font-size: 1rem;
      color: var(--text-muted);
      line-height: 1.5;
      max-width: 950px;
    }}

    /* Cuadrículas y Layouts sin huecos vacíos */
    .slide-body {{
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}

    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      align-items: stretch;
    }}

    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      align-items: stretch;
    }}

    .grid-4 {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 18px;
    }}

    .grid-diagram-text {{
      display: grid;
      grid-template-columns: 1.35fr 1fr;
      gap: 24px;
      align-items: stretch;
    }}

    /* Tarjetas y Paneles */
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 22px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 16px;
      transition: box-shadow 0.2s ease, border-color 0.2s ease;
    }}

    .card:hover {{
      box-shadow: var(--shadow-md);
      border-color: var(--border-focus);
    }}

    .card-title {{
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--text);
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
    }}

    .card-desc {{
      font-size: 0.88rem;
      color: var(--text-muted);
      line-height: 1.45;
    }}

    /* Cajas de métricas para la portada */
    .metric-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px;
      text-align: center;
      box-shadow: var(--shadow-sm);
    }}

    .metric-val {{
      font-family: var(--font-mono);
      font-size: 2.1rem;
      font-weight: 800;
      color: var(--primary);
      margin-bottom: 4px;
      line-height: 1.1;
    }}

    .metric-sub {{
      font-size: 0.85rem;
      color: var(--text-muted);
      font-weight: 500;
    }}

    /* Listas con viñetas limpias */
    .clean-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 12px;
      font-size: 0.92rem;
      color: var(--text);
      line-height: 1.5;
    }}

    .clean-list li {{
      position: relative;
      padding-left: 20px;
    }}

    .clean-list li::before {{
      content: "•";
      position: absolute;
      left: 0;
      color: var(--primary);
      font-size: 1.3rem;
      line-height: 1;
      top: 0;
    }}

    .clean-list strong {{
      color: var(--text);
      font-weight: 600;
    }}

    /* Cajas informativas / Callouts dentro de tarjetas */
    .callout {{
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 0.85rem;
      line-height: 1.45;
    }}

    .callout-primary {{
      background: var(--primary-bg);
      color: var(--text);
      border: 1px solid var(--primary-border);
    }}

    .callout-success {{
      background: var(--success-bg);
      color: var(--text);
      border: 1px solid var(--success-border);
    }}

    .callout-warning {{
      background: var(--warning-bg);
      color: var(--text);
      border: 1px solid var(--warning-border);
    }}

    .callout-danger {{
      background: var(--danger-bg);
      color: var(--text);
      border: 1px solid var(--danger-border);
    }}

    /* Tablas elegantes y claras */
    .table-box {{
      width: 100%;
      border-radius: 8px;
      border: 1px solid var(--border);
      overflow: hidden;
      background: var(--surface);
    }}

    table.styled-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
      text-align: left;
    }}

    table.styled-table th {{
      background: var(--bg-alt);
      color: var(--text-dim);
      font-family: var(--font-mono);
      font-size: 0.78rem;
      font-weight: 600;
      text-transform: uppercase;
      padding: 10px 14px;
      border-bottom: 1px solid var(--border);
    }}

    table.styled-table td {{
      padding: 10px 14px;
      border-bottom: 1px solid var(--border);
      color: var(--text);
    }}

    table.styled-table tr:last-child td {{
      border-bottom: none;
    }}

    table.styled-table tr:hover td {{
      background: var(--surface-hover);
    }}

    /* Visor de Imágenes en Tarjeta */
    .chart-container {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      cursor: zoom-in;
      transition: all 0.2s ease;
      height: 220px;
    }}

    .chart-container:hover {{
      border-color: var(--primary);
      box-shadow: var(--shadow-md);
    }}

    .chart-container img {{
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      display: block;
    }}

    .zoom-hint {{
      position: absolute;
      bottom: 8px;
      right: 8px;
      background: rgba(15, 23, 42, 0.8);
      color: #ffffff;
      font-size: 0.72rem;
      padding: 3px 8px;
      border-radius: 4px;
      font-weight: 500;
      pointer-events: none;
    }}

    /* Barra Inferior */
    footer {{
      height: 52px;
      padding: 0 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-top: 1px solid var(--border);
      background: var(--surface);
      z-index: 50;
      box-shadow: 0 -1px 2px rgba(0, 0, 0, 0.03);
    }}

    .footer-help {{
      font-size: 0.82rem;
      color: var(--text-dim);
      display: flex;
      gap: 16px;
    }}

    .footer-help kbd {{
      background: var(--bg-alt);
      border: 1px solid var(--border);
      padding: 2px 6px;
      border-radius: 4px;
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--text-muted);
    }}

    .footer-nav {{
      display: flex;
      gap: 10px;
    }}

    .btn-nav {{
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text);
      font-size: 0.85rem;
      font-weight: 600;
      padding: 6px 16px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }}

    .btn-nav:hover {{
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
    }}

    .btn-nav:disabled {{
      opacity: 0.35;
      pointer-events: none;
    }}

    /* Lightbox Modal */
    #lightbox {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(15, 23, 42, 0.92);
      backdrop-filter: blur(8px);
      z-index: 100;
      display: none;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      padding: 30px;
    }}

    #lightbox.active {{
      display: flex;
    }}

    #lightbox img {{
      max-width: 92vw;
      max-height: 85vh;
      object-fit: contain;
      border-radius: var(--radius);
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
      background: #ffffff;
      padding: 6px;
    }}

    #lightbox-caption {{
      margin-top: 14px;
      font-size: 0.95rem;
      font-weight: 500;
      color: #f8fafc;
    }}

    #lightbox-close {{
      position: absolute;
      top: 20px;
      right: 24px;
      background: rgba(255, 255, 255, 0.15);
      border: none;
      color: #ffffff;
      font-size: 1.5rem;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    #lightbox-close:hover {{
      background: var(--danger);
    }}

    /* Drawer de Contenidos */
    #drawer {{
      position: fixed;
      top: 56px;
      right: -360px;
      width: 360px;
      height: calc(100vh - 56px);
      background: var(--surface);
      border-left: 1px solid var(--border);
      z-index: 80;
      padding: 24px;
      box-shadow: -4px 0 16px rgba(0, 0, 0, 0.08);
      transition: right 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      overflow-y: auto;
    }}

    #drawer.open {{
      right: 0;
    }}

    .drawer-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }}

    .drawer-header h3 {{
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--text);
    }}

    .drawer-item {{
      padding: 10px 12px;
      border-radius: 6px;
      font-size: 0.88rem;
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      gap: 12px;
      margin-bottom: 4px;
      transition: all 0.15s ease;
      border: 1px solid transparent;
    }}

    .drawer-item:hover {{
      background: var(--bg-alt);
      color: var(--text);
    }}

    .drawer-item.active {{
      background: var(--primary-bg);
      color: var(--primary);
      border-color: var(--primary-border);
      font-weight: 600;
    }}

    .drawer-idx {{
      font-family: var(--font-mono);
      font-size: 0.78rem;
      color: var(--text-dim);
    }}

    /* Bloque de código */
    .terminal-box {{
      background: #0f172a;
      color: #38bdf8;
      font-family: var(--font-mono);
      font-size: 0.82rem;
      padding: 14px 16px;
      border-radius: 8px;
      line-height: 1.5;
    }}
  </style>
</head>
<body>

  <!-- Barra Superior -->
  <header>
    <div class="header-brand">
      <span class="course-tag">Taller ETL</span>
      <span>Violencia Intrafamiliar & Comisarías de Familia en Colombia</span>
    </div>
    <div class="header-actions">
      <div class="slide-badge" id="slide-num">01 / 12</div>
      <button class="btn-top" id="btn-theme" title="Cambiar Tema">🌓 Tema</button>
      <button class="btn-top" id="btn-drawer">☰ Índice</button>
      <button class="btn-top" id="btn-fs">⛶ Pantalla Completa</button>
    </div>
  </header>

  <!-- Contenedor del Slide Deck -->
  <main id="deck">

    <!-- SLIDE 1: PORTADA -->
    <section class="slide active" data-slide="1">
      <div style="height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; max-width: 940px; margin: 0 auto;">
        <span class="course-tag" style="margin-bottom: 16px; font-size: 0.85rem; padding: 4px 14px;">Ingeniería de Datos • Segunda Entrega</span>
        <h1 style="font-size: 2.85rem; font-weight: 800; line-height: 1.15; margin-bottom: 16px; color: var(--text);">
          Pipeline ETL y Data Warehouse de Violencia Intrafamiliar
        </h1>
        <p style="font-size: 1.15rem; color: var(--text-muted); line-height: 1.55; margin-bottom: 36px; max-width: 820px;">
          Integración del registro histórico de la Policía Nacional con la capacidad de respuesta institucional del Directorio de Comisarías de Familia (API SODA - Ministerio de Justicia).
        </p>

        <div class="grid-4" style="width: 100%; margin-bottom: 32px;">
          <div class="metric-card">
            <div class="metric-val">704,551</div>
            <div class="metric-sub">Denuncias Policiales</div>
          </div>
          <div class="metric-card">
            <div class="metric-val" style="color: var(--success);">1,501,809</div>
            <div class="metric-sub">Víctimas Reconciliadas</div>
          </div>
          <div class="metric-card">
            <div class="metric-val" style="color: var(--warning);">1,249</div>
            <div class="metric-sub">Comisarías (API SODA)</div>
          </div>
          <div class="metric-card">
            <div class="metric-val" style="color: #8b5cf6;">0</div>
            <div class="metric-sub">Pérdida en la Carga (Delta)</div>
          </div>
        </div>

        <div class="callout callout-primary" style="font-size: 0.9rem; font-weight: 500;">
          <strong>Stack de Tecnologías:</strong> Apache Airflow 3 Task SDK • Great Expectations 1.X • PostgreSQL 16 • Power BI
        </div>
      </div>
    </section>

    <!-- SLIDE 2: EL PROBLEMA Y EL ALCANCE -->
    <section class="slide" data-slide="2">
      <div class="slide-header">
        <h2 class="slide-title">El Problema de Negocio y el Aporte de la API</h2>
        <p class="slide-subtitle">¿Por qué conectar las denuncias de violencia con el directorio de comisarías de familia?</p>
      </div>
      <div class="slide-body">
        <div class="grid-2">
          <!-- Columna 1 -->
          <div class="card">
            <div>
              <div class="card-title">1. Lo que teníamos (Primera Entrega)</div>
              <p class="card-desc" style="margin-bottom: 14px;">Análisis descriptivo basado únicamente en reportes de la Policía Nacional (2010 a 2026).</p>
              <ul class="clean-list">
                <li><strong>704,551 denuncias policiales:</strong> Registros con fecha, municipio, edad, género y tipo de arma.</li>
                <li><strong>Preguntas resueltas (R1–R5):</strong> Cuándo ocurre más violencia, en qué departamentos se concentra, la brecha de género y la afectación a menores de edad.</li>
                <li><strong>La gran limitación:</strong> Sabíamos con certeza <em>dónde y cuánto</em> ocurría la violencia, pero no sabíamos si el Estado tenía capacidad instalada para atender a las víctimas en ese municipio.</li>
              </ul>
            </div>
            <div class="callout callout-warning">
              <strong>El vacío analítico:</strong> Tener muchos casos en un municipio no decía si la justicia familiar estaba desbordada o si directamente no existía.
            </div>
          </div>

          <!-- Columna 2 -->
          <div class="card">
            <div>
              <div class="card-title" style="color: var(--primary);">2. Lo que logramos al integrar la API SODA</div>
              <p class="card-desc" style="margin-bottom: 14px;">Cruce directo con las 1,249 sedes activas de comisarías del Ministerio de Justicia.</p>
              <ul class="clean-list">
                <li><strong>Pregunta R6 (Sobrecarga de Comisarías):</strong> Dividimos las denuncias anuales entre el número de comisarías habilitadas. Descubrimos municipios con más de 1,200 casos al año por sede.</li>
                <li><strong>Pregunta R7 (Vacíos de Cobertura Institucional):</strong> Cruzamos los municipios con alta violencia contra aquellos que no tienen comisaría. Identificamos <strong>29 municipios prioritarios</strong> sin presencia estatal de auxilio familiar.</li>
                <li><strong>Decisiones para política pública:</strong> Permite focalizar recursos en los lugares exactos donde las víctimas no tienen a dónde acudir.</li>
              </ul>
            </div>
            <div class="callout callout-success">
              <strong>El valor real de la API:</strong> Pasamos de un análisis policial a un diagnóstico de capacidad de respuesta del Estado.
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 3: ARQUITECTURA DEL SISTEMA -->
    <section class="slide" data-slide="3">
      <div class="slide-header">
        <h2 class="slide-title">Arquitectura del Sistema y Flujo de Datos</h2>
        <p class="slide-subtitle">Diseño modular con dos ramas de ingesta, compuertas de calidad y carga atómica en PostgreSQL.</p>
      </div>
      <div class="slide-body">
        <div class="grid-diagram-text">
          <!-- Imagen -->
          <div class="chart-container" style="height: 100%; min-height: 380px;" onclick="openLightbox('{b64['workflow']}', 'Diagrama de Arquitectura y Flujo del Pipeline ETL')">
            <img src="{b64['workflow']}" alt="Arquitectura del Pipeline">
            <div class="zoom-hint">🔍 Clic para ampliar diagrama</div>
          </div>

          <!-- Explicación -->
          <div class="card">
            <div>
              <div class="card-title">Paso a Paso del Flujo de Datos</div>
              <ul class="clean-list" style="margin-top: 10px;">
                <li><strong>1. Extracción Dual:</strong> Se descarga la data histórica policial y se consulta en paralelo la API REST de comisarías. Si la red falla, se activa automáticamente una copia local versionada.</li>
                <li><strong>2. Control de Calidad Separado:</strong> No mezclamos limpieza con validación. Primero auditamos la estructura cruda (Gates 1 y 2). Si algo viene corrupto, el pipeline frena de inmediato.</li>
                <li><strong>3. Integración por Contrato DANE:</strong> Estandarizamos los códigos municipales a 5 dígitos para unir ambas fuentes sin errores de coincidencia.</li>
                <li><strong>4. Carga Atómica en Base de Datos:</strong> Se cargan 6 tablas en PostgreSQL en una sola transacción ACID; si una falla, se hace rollback y no se ensucia nada.</li>
              </ul>
            </div>
            <div class="callout callout-primary">
              <strong>Resultado de Ingeniería:</strong> Flujo desacoplado, observable y protegido ante fallos imprevistos.
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 4: CONTROL DE CALIDAD AUTOMÁTICO (GX) -->
    <section class="slide" data-slide="4">
      <div class="slide-header">
        <h2 class="slide-title">Control de Calidad Automático con Great Expectations</h2>
        <p class="slide-subtitle">16 reglas de calidad divididas en 3 compuertas automáticas para garantizar datos limpios y confiables.</p>
      </div>
      <div class="slide-body">
        <div class="grid-3">
          <!-- Gate 1 -->
          <div class="card">
            <div>
              <div class="card-title">Compuerta 1: Datos de Policía</div>
              <p class="card-desc" style="margin-bottom: 12px;">Auditoría de 704,551 filas policiales crudas antes de transformar.</p>
              <ul class="clean-list" style="font-size: 0.88rem; gap: 8px;">
                <li><strong>Completitud:</strong> Deben venir las 9 columnas obligatorias.</li>
                <li><strong>Fechas lógicas:</strong> Cero fechas futuras y posteriores a 2010.</li>
                <li><strong>Víctimas válidas:</strong> Cantidad de personas siempre mayor a cero.</li>
                <li><strong>Códigos DANE:</strong> Formatos numéricos válidos.</li>
              </ul>
            </div>
            <div class="callout callout-success">
              <strong>Resultado:</strong> 6 de 6 reglas superadas (0 fallas).
            </div>
          </div>

          <!-- Gate 2 -->
          <div class="card">
            <div>
              <div class="card-title">Compuerta 2: Datos de la API</div>
              <p class="card-desc" style="margin-bottom: 12px;">Auditoría de 1,249 registros del directorio judicial de comisarías.</p>
              <ul class="clean-list" style="font-size: 0.88rem; gap: 8px;">
                <li><strong>Columna obligatoria:</strong> Presencia de <code>existencia_de_comisarias</code>.</li>
                <li><strong>Ubicación clara:</strong> Cero departamentos nulos o vacíos.</li>
                <li><strong>Valores válidos:</strong> Indicador de presencia estrictamente (SI / NO).</li>
                <li><strong>Volumen esperado:</strong> Alerta si la API devuelve menos de 1,000 sedes.</li>
              </ul>
            </div>
            <div class="callout callout-success">
              <strong>Resultado:</strong> 5 de 5 reglas superadas (0 fallas).
            </div>
          </div>

          <!-- Gate 3 -->
          <div class="card">
            <div>
              <div class="card-title">Compuerta 3: Datos Integrados</div>
              <p class="card-desc" style="margin-bottom: 12px;">Verificación de integridad previa a la carga al Data Warehouse.</p>
              <ul class="clean-list" style="font-size: 0.88rem; gap: 8px;">
                <li><strong>Unicidad del grano:</strong> Cero duplicados en la tabla de hechos.</li>
                <li><strong>Integridad referencial:</strong> Cero claves foráneas huérfanas en dimensiones.</li>
                <li><strong>Reconciliación matemática:</strong> El total de víctimas en destino debe ser idéntico al de origen (1,501,809).</li>
              </ul>
            </div>
            <div class="callout callout-success">
              <strong>Resultado:</strong> Reconciliación exacta al 100% (0 delta).
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 5: CONTRATO DE INTEGRACIÓN Y LIMPIEZA -->
    <section class="slide" data-slide="5">
      <div class="slide-header">
        <h2 class="slide-title">El Contrato de Integración y la Limpieza</h2>
        <p class="slide-subtitle">Cómo resolvimos las diferencias entre fuentes y deduplicamos datos sin perder una sola víctima.</p>
      </div>
      <div class="slide-body">
        <div class="grid-2">
          <!-- Columna 1 -->
          <div class="card">
            <div>
              <div class="card-title">Resolución de Discrepancias</div>
              <p class="card-desc" style="margin-bottom: 12px;">El código DANE municipal fue el puente de unión entre la Policía y la API.</p>
              <ul class="clean-list">
                <li><strong>Estandarización DANE:</strong> Rellenamos los códigos con ceros a la izquierda (por ejemplo, <code>"05001"</code> para Medellín en lugar de <code>"5001"</code>). Esto corrigió el 100% de los cruces erróneos.</li>
                <li><strong>Normalización de Nombres:</strong> Corregimos mayúsculas, minúsculas y tildes para evitar que un municipio apareciera dos veces por variaciones tipográficas.</li>
                <li><strong>Los 2 Municipios Especiales:</strong> La API registraba 2 municipios con comisarías pero donde la Policía no tenía denuncias. En lugar de borrarlos, los conservamos en la dimensión geográfica para no perder la información del Estado.</li>
              </ul>
            </div>
            <div class="callout callout-primary">
              <strong>Decisión de diseño:</strong> Priorizar la consistencia territorial sin alterar los hechos de violencia.
            </div>
          </div>

          <!-- Columna 2 -->
          <div class="card">
            <div>
              <div class="card-title">Deduplicación al Grano Declarado</div>
              <p class="card-desc" style="margin-bottom: 12px;">En el dataset crudo existían registros repetidos para una misma fecha, lugar y perfil.</p>
              <ul class="clean-list">
                <li><strong>El Grano Atómico:</strong> Una fila por cada combinación de <em>(Fecha, Municipio, Perfil de Víctima, Arma)</em>.</li>
                <li><strong>Cómo deduplicamos:</strong> En lugar de eliminar filas al azar, agrupamos los registros repetidos y sumamos el número de víctimas.</li>
                <li><strong>Resultado matemático:</strong> Se colapsaron 2,837 registros redundantes y se mantuvieron intactas las 1,501,809 víctimas.</li>
              </ul>
            </div>
            <div class="grid-2" style="margin-top: 10px;">
              <div class="metric-card" style="padding: 12px;">
                <div class="metric-val" style="font-size: 1.6rem; color: var(--warning);">2,837</div>
                <div class="metric-sub">Filas Redundantes Colapsadas</div>
              </div>
              <div class="metric-card" style="padding: 12px;">
                <div class="metric-val" style="font-size: 1.6rem; color: var(--success);">1,501,809</div>
                <div class="metric-sub">Víctimas Conservadas (100%)</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 6: MODELO DIMENSIONAL EN ESTRELLA -->
    <section class="slide" data-slide="6">
      <div class="slide-header">
        <h2 class="slide-title">Modelo Dimensional en Estrella (Star Schema)</h2>
        <p class="slide-subtitle">Estructura optimizada en PostgreSQL para soportar las consultas analíticas de Power BI.</p>
      </div>
      <div class="slide-body">
        <div class="grid-diagram-text">
          <!-- Imagen -->
          <div class="chart-container" style="height: 100%; min-height: 380px;" onclick="openLightbox('{b64['dimensional']}', 'Modelo Dimensional en Estrella - Data Warehouse')">
            <img src="{b64['dimensional']}" alt="Modelo Dimensional">
            <div class="zoom-hint">🔍 Clic para ampliar esquema</div>
          </div>

          <!-- Tabla de Dimensiones -->
          <div class="card">
            <div>
              <div class="card-title">Estructura del Data Warehouse</div>
              <div class="table-box" style="margin-top: 10px;">
                <table class="styled-table">
                  <tr><th>Tabla</th><th>Filas</th><th>Función</th></tr>
                  <tr><td><strong>fact_violencia</strong></td><td>701,714</td><td>Métricas de víctimas y denuncias</td></tr>
                  <tr><td><strong>dim_tiempo</strong></td><td>6,056</td><td>Calendario diario (2010 a 2026)</td></tr>
                  <tr><td><strong>dim_geografia</strong></td><td>1,113</td><td>Municipios con número de comisarías</td></tr>
                  <tr><td><strong>dim_victima</strong></td><td>11</td><td>Perfiles demográficos (género y edad)</td></tr>
                  <tr><td><strong>dim_medio</strong></td><td>6</td><td>Armas y mecanismos agresores</td></tr>
                  <tr><td><strong>dim_comisaria</strong></td><td>1,247</td><td>Directorio físico de sedes del MinJusticia</td></tr>
                </table>
              </div>
            </div>
            <div class="callout callout-primary">
              <strong>Optimización Técnica:</strong> Claves sustitutas enteras (Surrogate Keys) con índices B-Tree para que los filtros de Power BI respondan de manera instantánea.
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 7: ORQUESTACIÓN CON AIRFLOW 3 -->
    <section class="slide" data-slide="7">
      <div class="slide-header">
        <h2 class="slide-title">Orquestación en Airflow 3 Task SDK</h2>
        <p class="slide-subtitle">Coordinación moderna con decoradores (@dag, @task) y política inteligente de reintentos.</p>
      </div>
      <div class="slide-body">
        <div class="grid-2">
          <!-- Columna 1 -->
          <div class="card">
            <div>
              <div class="card-title">Diseño de Tareas y XCom Ligero</div>
              <p class="card-desc" style="margin-bottom: 12px;">Cumplimiento de las mejores prácticas de ingeniería en Airflow 3.</p>
              <ul class="clean-list">
                <li><strong>Código Limpio y Moderno:</strong> Construido con Task SDK de Airflow 3, con cero advertencias de funciones obsoletas.</li>
                <li><strong>No saturar la memoria de Airflow:</strong> Los 700k registros viajan por disco en formato Parquet; XCom únicamente transporta metadatos ligeros (el <code>batch_id</code> y las rutas de los archivos).</li>
                <li><strong>Trazabilidad completa:</strong> Cada ejecución registra tiempos de respuesta, volúmenes de datos y hashes de verificación criptográfica.</li>
              </ul>
            </div>
            <div class="callout callout-primary">
              <strong>Principio clave:</strong> Airflow es el orquestador del tráfico, no el camión de carga pesada.
            </div>
          </div>

          <!-- Columna 2 -->
          <div class="card">
            <div>
              <div class="card-title">Política Justificada de Reintentos</div>
              <p class="card-desc" style="margin-bottom: 12px;">Diferenciamos entre problemas temporales y problemas de fondo.</p>
              <div class="table-box" style="margin-bottom: 12px;">
                <table class="styled-table">
                  <tr><th>Tipo de Fallo</th><th>Ejemplo</th><th>Estrategia</th></tr>
                  <tr>
                    <td><strong>Fallo de Red (Transitorio)</strong></td>
                    <td>API SODA caída o lenta.</td>
                    <td><strong style="color: var(--primary);">3 reintentos con espera</strong>. Se resuelve solo.</td>
                  </tr>
                  <tr>
                    <td><strong>Fallo de Datos (Determinístico)</strong></td>
                    <td>Archivo corrupto o columnas faltantes.</td>
                    <td><strong style="color: var(--danger);">0 reintentos</strong>. Se detiene de inmediato.</td>
                  </tr>
                </table>
              </div>
            </div>
            <div class="callout callout-danger">
              <strong>Freno de emergencia:</strong> Si se viola una regla crítica, la tarea lanza <code>AirflowFailException</code>, bloqueando la carga y protegiendo el Data Warehouse.
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 8: PRUEBAS REALES DE CONFIABILIDAD (A, B, C) -->
    <section class="slide" data-slide="8">
      <div class="slide-header">
        <h2 class="slide-title">Pruebas Reales de Confiabilidad (A, B y C)</h2>
        <p class="slide-subtitle">Demostración práctica de comportamiento en caso de éxito, falla controlada y re-ejecución.</p>
      </div>
      <div class="slide-body">
        <div class="grid-3">
          <!-- Test A -->
          <div class="card">
            <div>
              <div class="card-title" style="color: var(--success);">Prueba A: Ejecución Exitosa</div>
              <p class="card-desc" style="margin-bottom: 12px;">El pipeline completo corriendo con datos válidos.</p>
              <ul class="clean-list" style="font-size: 0.88rem; gap: 8px;">
                <li>Tiempo total de ejecución: <strong>22.20 segundos</strong>.</li>
                <li>Compuertas 1, 2 y 3 aprobadas al 100%.</li>
                <li>701,714 filas cargadas en PostgreSQL.</li>
                <li>Diferencia de víctimas entre origen y destino: <strong>0</strong>.</li>
                <li>Claves huérfanas en dimensiones: <strong>0</strong>.</li>
              </ul>
            </div>
            <div class="callout callout-success">
              <strong>Estado:</strong> APROBADO (100% de reconciliación).
            </div>
          </div>

          <!-- Test B -->
          <div class="card">
            <div>
              <div class="card-title" style="color: var(--danger);">Prueba B: Falla Controlada</div>
              <p class="card-desc" style="margin-bottom: 12px;">Inyección de error para probar el freno de emergencia.</p>
              <ul class="clean-list" style="font-size: 0.88rem; gap: 8px;">
                <li><strong>Condición inyectada:</strong> Eliminamos a propósito la columna obligatoria de comisarías.</li>
                <li>La compuerta 2 detectó la falta y frenó la ejecución.</li>
                <li>Las tareas de transformación y carga quedaron <strong>bloqueadas</strong>.</li>
                <li>La base de datos quedó <strong>100% protegida e intacta</strong>.</li>
              </ul>
            </div>
            <div class="callout callout-danger">
              <strong>Estado:</strong> APROBADO (Bloqueo exitoso verificado).
            </div>
          </div>

          <!-- Test C -->
          <div class="card">
            <div>
              <div class="card-title" style="color: var(--primary);">Prueba C: Re-ejecución Segura</div>
              <p class="card-desc" style="margin-bottom: 12px;">Ejecución del mismo lote dos veces seguidas (Idempotencia).</p>
              <div class="table-box" style="margin: 8px 0;">
                <table class="styled-table" style="font-size: 0.8rem;">
                  <tr><th>Métrica</th><th>Antes</th><th>Después</th><th>Delta</th></tr>
                  <tr><td>Filas Fact</td><td>701,714</td><td>701,714</td><td><strong>0</strong></td></tr>
                  <tr><td>Víctimas</td><td>1,501,809</td><td>1,501,809</td><td><strong>0</strong></td></tr>
                  <tr><td>Municipios</td><td>1,113</td><td>1,113</td><td><strong>0</strong></td></tr>
                </table>
              </div>
            </div>
            <div class="callout callout-primary">
              <strong>Estado:</strong> APROBADO (Cero registros duplicados).
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 9: HALLAZGOS POWER BI (R1 A R4) -->
    <section class="slide" data-slide="9">
      <div class="slide-header">
        <h2 class="slide-title">Hallazgos en Power BI: Patrones de Violencia (R1 a R4)</h2>
        <p class="slide-subtitle">Visualizaciones conectadas directamente a las vistas analíticas del Data Warehouse.</p>
      </div>
      <div class="slide-body">
        <div class="grid-4">
          <!-- R1 -->
          <div class="card" style="padding: 16px;">
            <div>
              <div class="card-title" style="font-size: 0.95rem;">R1: Evolución Anual</div>
              <div class="chart-container" style="height: 170px; margin: 10px 0;" onclick="openLightbox('{b64['r1']}', 'R1: Evolución Histórica de Casos 2010 a 2026')">
                <img src="{b64['r1']}" alt="R1 Evolución">
                <div class="zoom-hint">🔍 Ampliar</div>
              </div>
              <p class="card-desc">Tendencia creciente. El año 2024 marca el récord histórico con más de 150,000 víctimas reportadas.</p>
            </div>
          </div>

          <!-- R2 -->
          <div class="card" style="padding: 16px;">
            <div>
              <div class="card-title" style="font-size: 0.95rem;">R2: Departamentos</div>
              <div class="chart-container" style="height: 170px; margin: 10px 0;" onclick="openLightbox('{b64['r2']}', 'R2: Concentración Departamental de Violencia')">
                <img src="{b64['r2']}" alt="R2 Departamentos">
                <div class="zoom-hint">🔍 Ampliar</div>
              </div>
              <p class="card-desc">Bogotá, Antioquia, Cundinamarca, Valle y Santander concentran casi el 50% de las denuncias de todo el país.</p>
            </div>
          </div>

          <!-- R3 -->
          <div class="card" style="padding: 16px;">
            <div>
              <div class="card-title" style="font-size: 0.95rem;">R3: Brecha de Género</div>
              <div class="chart-container" style="height: 170px; margin: 10px 0;" onclick="openLightbox('{b64['r3']}', 'R3: Distribución por Sexo y Grupos de Edad')">
                <img src="{b64['r3']}" alt="R3 Género">
                <div class="zoom-hint">🔍 Ampliar</div>
              </div>
              <p class="card-desc">El 76.8% de las víctimas son mujeres, con especial concentración en mujeres entre los 20 y 39 años.</p>
            </div>
          </div>

          <!-- R4 -->
          <div class="card" style="padding: 16px;">
            <div>
              <div class="card-title" style="font-size: 0.95rem;">R4: Mecanismos</div>
              <div class="chart-container" style="height: 170px; margin: 10px 0;" onclick="openLightbox('{b64['r4']}', 'R4: Armas y Mecanismos de Agresión')">
                <img src="{b64['r4']}" alt="R4 Armas">
                <div class="zoom-hint">🔍 Ampliar</div>
              </div>
              <p class="card-desc">Más del 90% de los incidentes se cometen con elementos contundentes y violencia física directa sin armas de fuego.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 10: HALLAZGOS POWER BI (R5 A R7) -->
    <section class="slide" data-slide="10">
      <div class="slide-header">
        <h2 class="slide-title">Capacidad del Estado y Vacíos de Cobertura (R5 a R7)</h2>
        <p class="slide-subtitle">Respuestas analíticas obtenidas gracias al cruce directo con la API de Comisarías.</p>
      </div>
      <div class="slide-body">
        <div class="grid-3">
          <!-- R5 -->
          <div class="card">
            <div>
              <div class="card-title">R5: Menores de Edad</div>
              <div class="chart-container" style="height: 210px; margin: 10px 0;" onclick="openLightbox('{b64['r5']}', 'R5: Vulnerabilidad Geográfica de Menores de Edad')">
                <img src="{b64['r5']}" alt="R5 Menores">
                <div class="zoom-hint">🔍 Ampliar mapa</div>
              </div>
              <p class="card-desc">Identifica los departamentos con mayor cantidad de agresiones contra niñas, niños y adolescentes, ubicando zonas de atención prioritaria.</p>
            </div>
            <div class="callout callout-primary">
              <strong>Foco:</strong> Protección prioritaria a la infancia en zonas metropolitanas y rurales.
            </div>
          </div>

          <!-- R6 -->
          <div class="card">
            <div>
              <div class="card-title" style="color: var(--warning);">R6: Sobrecarga de Comisarías</div>
              <div class="chart-container" style="height: 210px; margin: 10px 0;" onclick="openLightbox('{b64['r6']}', 'R6: Casos Anuales por Cada Comisaría de Familia')">
                <img src="{b64['r6']}" alt="R6 Sobrecarga">
                <div class="zoom-hint">🔍 Ampliar gráfica</div>
              </div>
              <p class="card-desc">Municipios como Soacha, Cali y Bogotá registran <strong>más de 1,200 casos al año por cada comisaría</strong>, evidenciando saturación extrema del personal de atención.</p>
            </div>
            <div class="callout callout-warning">
              <strong>Alerta institucional:</strong> Se requiere refuerzo inmediato de equipos psicosociales.
            </div>
          </div>

          <!-- R7 -->
          <div class="card">
            <div>
              <div class="card-title" style="color: var(--danger);">R7: Municipios sin Comisaría</div>
              <div class="chart-container" style="height: 210px; margin: 10px 0;" onclick="openLightbox('{b64['r7']}', 'R7: Municipios Críticos con Cero Comisarías')">
                <img src="{b64['r7']}" alt="R7 Prioridad">
                <div class="zoom-hint">🔍 Ampliar listado</div>
              </div>
              <p class="card-desc">El hallazgo más importante: identificamos <strong>29 municipios con violencia intrafamiliar activa que no tienen ni una sola comisaría de familia</strong>.</p>
            </div>
            <div class="callout callout-danger">
              <strong>Prioridad de Estado:</strong> Justificación técnica para abrir nuevas sedes del MinJusticia.
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 11: LIMITACIONES Y APRENDIZAJES -->
    <section class="slide" data-slide="11">
      <div class="slide-header">
        <h2 class="slide-title">Limitaciones y Aprendizajes de Ingeniería</h2>
        <p class="slide-subtitle">Entendimiento crítico de los datos reales y de la arquitectura construida.</p>
      </div>
      <div class="slide-body">
        <div class="grid-2">
          <!-- Columna 1 -->
          <div class="card">
            <div>
              <div class="card-title">Limitaciones del Dominio</div>
              <p class="card-desc" style="margin-bottom: 12px;">Aspectos del contexto que los números por sí solos no muestran.</p>
              <ul class="clean-list">
                <li><strong>La Cifra Negra:</strong> Los registros reflejan únicamente denuncias oficiales ante la Policía. Existe un subregistro significativo de víctimas que no denuncian por miedo o falta de acceso institucional.</li>
                <li><strong>Desfase de la API:</strong> El directorio de comisarías del MinJusticia se actualiza periódicamente; nuevas sedes creadas recientemente pueden tardar meses en aparecer en datos abiertos.</li>
                <li><strong>Granularidad Diaria:</strong> Aunque tenemos la fecha exacta, los registros policiales no incluyen hora del hecho, limitando el análisis de patrones por franja horaria.</li>
              </ul>
            </div>
            <div class="callout callout-warning">
              <strong>Reflexión ética:</strong> Detrás de cada fila hay una persona en situación de vulnerabilidad.
            </div>
          </div>

          <!-- Columna 2 -->
          <div class="card">
            <div>
              <div class="card-title">Aprendizajes de Ingeniería de Datos</div>
              <p class="card-desc" style="margin-bottom: 12px;">Buenas prácticas aplicadas que hicieron la diferencia en el proyecto.</p>
              <ul class="clean-list">
                <li><strong>Diseñar pensando en fallos:</strong> Un pipeline profesional debe asumir que la red se caerá o que los datos vendrán dañados. La compuerta de validación y la transacción atómica fueron lo más valioso del diseño.</li>
                <li><strong>Estabilidad del orquestador:</strong> Airflow debe coordinar procesos, no transportar 700k filas en memoria. El uso de Parquet y XCom ligero garantizó estabilidad total.</li>
                <li><strong>Idempotencia obligatoria:</strong> Si un proceso falla a la mitad, debe poder relanzarse sin duplicar datos ni alterar los tableros de BI.</li>
              </ul>
            </div>
            <div class="callout callout-success">
              <strong>Conclusión técnica:</strong> La confiabilidad y la arquitectura valen tanto como el código mismo.
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 12: CONCLUSIONES Y DEMO -->
    <section class="slide" data-slide="12">
      <div class="slide-header">
        <h2 class="slide-title">Conclusiones y Entorno de Demostración</h2>
        <p class="slide-subtitle">Resumen del cumplimiento de los entregables y comandos para ejecutar en vivo.</p>
      </div>
      <div class="slide-body">
        <div class="grid-2">
          <!-- Columna 1 -->
          <div class="card">
            <div>
              <div class="card-title">Resumen de Entregables Completados</div>
              <p class="card-desc" style="margin-bottom: 14px;">El proyecto cumple al 100% con los criterios de evaluación de la rúbrica.</p>
              <ul class="clean-list">
                <li><strong>Repositorio GitHub:</strong> Completamente independiente, versionado y libre de credenciales sensibles.</li>
                <li><strong>Data Warehouse:</strong> PostgreSQL 16 contenedorizado con 701,714 filas fact y 5 dimensiones conformadas.</li>
                <li><strong>Confiabilidad Auditada:</strong> Tests A, B y C documentados con evidencia JSON descargable en <code>docs/evidence/</code>.</li>
                <li><strong>Dashboard en Power BI:</strong> Archivo <code>.pbix</code> conectado a las vistas de la base de datos respondiendo de R1 a R7.</li>
              </ul>
            </div>
            <div class="callout callout-success">
              <strong>Estado de la Entrega:</strong> 100% Validado, probado y listo para la defensa técnica.
            </div>
          </div>

          <!-- Columna 2 -->
          <div class="card">
            <div>
              <div class="card-title">Comandos para Demostración en Vivo</div>
              <p class="card-desc" style="margin-bottom: 12px;">Comandos reproducibles para mostrar al docente en consola:</p>
              <div class="terminal-box">
                # 1. Levantar base de datos PostgreSQL en Docker<br>
                docker compose up -d postgres_dw<br><br>
                # 2. Ejecutar suite de confiabilidad (A, B y C)<br>
                python3 src/run_pipeline.py<br><br>
                # 3. Abrir la interfaz web de Airflow (Puerto 8080)<br>
                docker compose up -d airflow
              </div>
            </div>
            <div style="font-size: 0.88rem; color: var(--text-muted);">
              <strong>Repositorio Oficial:</strong> <a href="https://github.com/Macowli-0611/Proyecto_etl_c2" target="_blank" style="color: var(--primary); text-decoration: none; font-weight: 600;">github.com/Macowli-0611/Proyecto_etl_c2</a>
            </div>
          </div>
        </div>
      </div>
    </section>

  </main>

  <!-- Barra Inferior -->
  <footer>
    <div class="footer-help">
      <span>Navegar con <kbd>←</kbd> y <kbd>→</kbd></span>
      <span>•</span>
      <span><kbd>F</kbd> Pantalla completa</span>
      <span>•</span>
      <span><kbd>T</kbd> Índice</span>
      <span>•</span>
      <span>Clic en cualquier imagen para ampliar</span>
    </div>
    <div class="footer-nav">
      <button class="btn-nav" id="btn-prev">← Anterior</button>
      <button class="btn-nav" id="btn-next">Siguiente →</button>
    </div>
  </footer>

  <!-- Drawer de Índice -->
  <aside id="drawer">
    <div class="drawer-header">
      <h3>Tabla de Contenidos</h3>
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
    const btnTheme = document.getElementById('btn-theme');
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxCaption = document.getElementById('lightbox-caption');

    const titles = [
      "Portada: Pipeline ETL y Data Warehouse",
      "El Problema de Negocio y el Aporte de la API",
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
      div.innerHTML = `<span class="drawer-idx">${{String(i + 1).padStart(2, '0')}}</span> <span>${{t}}</span>`;
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

    const themeList = ['medium', 'slate-light', 'light', 'dark'];
    const themeLabels = {{
      'medium': 'Tono Medio (Slate)',
      'slate-light': 'Medio Claro (Platino)',
      'light': 'Modo Claro',
      'dark': 'Modo Oscuro'
    }};

    function toggleTheme() {{
      const current = document.documentElement.getAttribute('data-theme') || 'medium';
      const nextIdx = (themeList.indexOf(current) + 1) % themeList.length;
      const target = themeList[nextIdx];
      document.documentElement.setAttribute('data-theme', target);
      btnTheme.textContent = '🎨 ' + themeLabels[target];
      localStorage.setItem('presentation-theme', target);
    }}

    // Load saved theme if any
    const savedTheme = localStorage.getItem('presentation-theme') || 'medium';
    document.documentElement.setAttribute('data-theme', savedTheme);
    btnTheme.textContent = '🎨 ' + (themeLabels[savedTheme] || 'Tono Medio');

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
    btnTheme.onclick = toggleTheme;

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
