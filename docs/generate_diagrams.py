"""Generates Architecture and Refined Star Schema Diagrams using Matplotlib.

Produces:
  - docs/architecture.png
  - docs/star_schema.png
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_architecture_diagram():
    """Generates the system architecture diagram."""
    fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
    ax.axis("off")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)

    # Background color
    fig.patch.set_facecolor("#0F172A")
    ax.set_facecolor("#0F172A")

    # Title
    ax.text(7, 7.5, "ETL Pipeline Architecture — Phase 2: Automation, API & Validation",
            ha="center", va="center", color="#F8FAFC", fontsize=15, weight="bold")
    ax.text(7, 7.15, "Policía Nacional (DIJIN) + MinJusticia Comisarías de Familia API | Apache Airflow 3.X | PostgreSQL DW",
            ha="center", va="center", color="#94A3B8", fontsize=10)

    # 1. Sources Box
    box_style_source = dict(boxstyle="round,pad=0.5", facecolor="#1E293B", edgecolor="#38BDF8", linewidth=1.5)
    ax.text(2, 5.8, "Primary Source (DIJIN)\nPolice Violence Reports\n704,551 records | datos.gov.co",
            ha="center", va="center", color="#F8FAFC", fontsize=9, bbox=box_style_source)
    ax.text(2, 3.2, "API Source (MinJusticia)\nComisarías de Familia\nSODA REST API | 1,249 entries",
            ha="center", va="center", color="#F8FAFC", fontsize=9, bbox=box_style_source)

    # 2. Gate 1 & 2 (Raw Validation)
    box_style_gx = dict(boxstyle="round,pad=0.5", facecolor="#1E293B", edgecolor="#F59E0B", linewidth=1.5)
    ax.text(5, 5.8, "Gate 1: GX Validation\nvalidate_primary_raw\nDQ-RAW1 (Critical: 0 error)",
            ha="center", va="center", color="#FDE68A", fontsize=9, bbox=box_style_gx)
    ax.text(5, 3.2, "Gate 2: GX Validation\nvalidate_api_raw\nDQ-RAW2 (Critical: 0 error)",
            ha="center", va="center", color="#FDE68A", fontsize=9, bbox=box_style_gx)

    # 3. Transformation & Integration
    box_style_trans = dict(boxstyle="round,pad=0.6", facecolor="#1E293B", edgecolor="#10B981", linewidth=2)
    ax.text(8, 4.5, "Transformation & Integration\nIntegration Contract (DDMMM)\nDemographic Imputation & Weapons\n701,714 Municipal Grain Rows",
            ha="center", va="center", color="#A7F3D0", fontsize=9.5, weight="bold", bbox=box_style_trans)

    # 4. Gate 3 (Prepared Validation)
    ax.text(10.8, 4.5, "Gate 3: GX Validation\nvalidate_prepared\nGrain & Ref Integrity (100%)",
            ha="center", va="center", color="#FDE68A", fontsize=9, bbox=box_style_gx)

    # 5. Data Warehouse & BI
    box_style_dw = dict(boxstyle="round,pad=0.6", facecolor="#1E293B", edgecolor="#8B5CF6", linewidth=2)
    ax.text(12.8, 4.5, "PostgreSQL 16 DW\nStar Schema\n5 Dims + Fact\nBI Views (R1–R7)",
            ha="center", va="center", color="#DDD6FE", fontsize=9, weight="bold", bbox=box_style_dw)

    # Airflow Banner
    box_style_af = dict(boxstyle="round,pad=0.4", facecolor="#0284C7", edgecolor="#38BDF8", linewidth=1)
    ax.text(7, 1.2, "Orchestrated by Apache Airflow 3.X (TaskFlow API) | Strict Dependencies | Selective Retries | Full Observability",
            ha="center", va="center", color="#FFFFFF", fontsize=10, weight="bold", bbox=box_style_af)

    # Arrows
    arrow = dict(arrowstyle="->", color="#94A3B8", lw=1.8)
    ax.annotate("", xy=(3.6, 5.8), xytext=(3.2, 5.8), arrowprops=arrow)
    ax.annotate("", xy=(3.6, 3.2), xytext=(3.2, 3.2), arrowprops=arrow)
    ax.annotate("", xy=(6.8, 4.8), xytext=(6.2, 5.8), arrowprops=arrow)
    ax.annotate("", xy=(6.8, 4.2), xytext=(6.2, 3.2), arrowprops=arrow)
    ax.annotate("", xy=(9.7, 4.5), xytext=(9.2, 4.5), arrowprops=arrow)
    ax.annotate("", xy=(12.0, 4.5), xytext=(11.6, 4.5), arrowprops=arrow)

    plt.tight_layout()
    out_path = os.path.join(DOCS_DIR, "architecture.png")
    plt.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print("Saved architecture diagram to", out_path)


def generate_star_schema_diagram():
    """Generates the refined Star Schema diagram."""
    fig, ax = plt.subplots(figsize=(14, 9), dpi=200)
    ax.axis("off")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)

    fig.patch.set_facecolor("#0F172A")
    ax.set_facecolor("#0F172A")

    # Title
    ax.text(7, 8.5, "Refined Dimensional Model — Star Schema (PostgreSQL)",
            ha="center", va="center", color="#F8FAFC", fontsize=15, weight="bold")
    ax.text(7, 8.15, "Declared Municipal Grain: (id_tiempo, id_geografia, id_victima, id_medio)",
            ha="center", va="center", color="#94A3B8", fontsize=10)

    # Fact Box (Center)
    fact_text = (
        "fact_violencia_intrafamiliar\n"
        "────────────────────────────\n"
        "PK id_hecho (BIGINT)\n"
        "FK id_tiempo (INT)\n"
        "FK id_geografia (INT)\n"
        "FK id_victima (INT)\n"
        "FK id_medio (INT)\n"
        "cantidad_victimas (INT, Additive)\n"
        "numero_registros (INT, Additive)\n"
        "fecha_carga (TIMESTAMP)\n"
        "────────────────────────────\n"
        "701,714 rows | 1,501,809 victims\n"
        "CONSTRAINT uq_fact_grano UNIQUE"
    )
    box_fact = dict(boxstyle="round,pad=0.6", facecolor="#1E293B", edgecolor="#EF4444", linewidth=2.5)
    ax.text(7, 4.5, fact_text, ha="center", va="center", color="#FCA5A5", fontsize=9, family="monospace", bbox=box_fact)

    # Dimension 1: dim_tiempo (Top Left)
    tiempo_text = (
        "dim_tiempo (6,056 rows)\n"
        "───────────────────────\n"
        "PK id_tiempo (INT)\n"
        "fecha (DATE, UNIQUE)\n"
        "anio, mes, nombre_mes\n"
        "trimestre, semestre\n"
        "dia_semana, nombre_dia\n"
        "es_fin_semana (BOOL)\n"
        "es_periodo_completo (BOOL)"
    )
    box_dim = dict(boxstyle="round,pad=0.5", facecolor="#1E293B", edgecolor="#38BDF8", linewidth=1.5)
    ax.text(2.2, 6.8, tiempo_text, ha="center", va="center", color="#BAE6FD", fontsize=8.5, family="monospace", bbox=box_dim)

    # Dimension 2: dim_geografia (Top Right - ENRICHED WITH API)
    geo_text = (
        "dim_geografia (1,113 rows)\n"
        "──────────────────────────\n"
        "PK id_geografia (INT)\n"
        "codigo_dane_municipio (CHAR 5, UQ)\n"
        "municipio, departamento\n"
        "es_capital (BOOL)\n"
        "★ categoria_municipio (Ley 617)\n"
        "★ comisarias_instaladas (API)\n"
        "★ comisarias_requeridas_ley (2126)\n"
        "★ brecha_comisarias (Deficit)\n"
        "★ tiene_comisaria (BOOL)"
    )
    box_geo = dict(boxstyle="round,pad=0.5", facecolor="#1E293B", edgecolor="#10B981", linewidth=2)
    ax.text(11.8, 6.8, geo_text, ha="center", va="center", color="#A7F3D0", fontsize=8.5, family="monospace", bbox=box_geo)

    # Dimension 3: dim_victima (Bottom Left)
    victima_text = (
        "dim_victima (11 rows)\n"
        "─────────────────────\n"
        "PK id_victima (INT)\n"
        "genero (VARCHAR)\n"
        "grupo_etario (VARCHAR)\n"
        "perfil_demografico\n"
        "es_menor_de_edad (BOOL)"
    )
    ax.text(2.2, 2.2, victima_text, ha="center", va="center", color="#BAE6FD", fontsize=8.5, family="monospace", bbox=box_dim)

    # Dimension 4: dim_medio (Bottom Right)
    medio_text = (
        "dim_medio (6 rows)\n"
        "──────────────────\n"
        "PK id_medio (INT)\n"
        "medio_agresion (VARCHAR)\n"
        "categoria_mecanismo\n"
        "es_arma_letal (BOOL)"
    )
    ax.text(11.8, 2.2, medio_text, ha="center", va="center", color="#BAE6FD", fontsize=8.5, family="monospace", bbox=box_dim)

    # Outrigger: dim_comisaria (Connected to dim_geografia)
    comisaria_text = (
        "dim_comisaria (1,247 rows)\n"
        "──────────────────────────\n"
        "PK id_comisaria (INT)\n"
        "FK codigo_dane_municipio\n"
        "nombre_comisaria, direccion\n"
        "telefono, horario_atencion"
    )
    box_com = dict(boxstyle="round,pad=0.5", facecolor="#1E293B", edgecolor="#F59E0B", linewidth=1.5)
    ax.text(11.8, 4.4, comisaria_text, ha="center", va="center", color="#FDE68A", fontsize=8, family="monospace", bbox=box_com)

    # Arrows from dimensions to fact
    arrow = dict(arrowstyle="->", color="#94A3B8", lw=1.8)
    ax.annotate("", xy=(5.2, 5.5), xytext=(3.7, 6.5), arrowprops=arrow)
    ax.annotate("", xy=(8.8, 5.5), xytext=(9.7, 6.5), arrowprops=arrow)
    ax.annotate("", xy=(5.2, 3.5), xytext=(3.7, 2.5), arrowprops=arrow)
    ax.annotate("", xy=(8.8, 3.5), xytext=(9.7, 2.5), arrowprops=arrow)
    # Outrigger connection
    arrow_out = dict(arrowstyle="->", color="#F59E0B", lw=1.5, ls="--")
    ax.annotate("", xy=(11.8, 5.6), xytext=(11.8, 5.2), arrowprops=arrow_out)

    plt.tight_layout()
    out_path = os.path.join(DOCS_DIR, "star_schema.png")
    plt.savefig(out_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print("Saved star schema diagram to", out_path)


if __name__ == "__main__":
    generate_architecture_diagram()
    generate_star_schema_diagram()
