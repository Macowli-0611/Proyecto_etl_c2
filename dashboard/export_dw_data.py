"""Exports Data Warehouse Analytical Data for BI Dashboard.

Queries PostgreSQL Data Warehouse for R1 through R7 KPIs and dimensions,
saving a consolidated data payload in dashboard/data_dw.json.
"""

import json
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_JSON = os.path.join(DASHBOARD_DIR, "data_dw.json")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "etl_dw")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres123")


def export_dashboard_data():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()

    # Overall KPIs
    cur.execute("""
        SELECT
            COUNT(*) AS total_hechos,
            SUM(cantidad_victimas) AS total_victimas,
            SUM(numero_registros) AS total_denuncias
        FROM fact_violencia_intrafamiliar;
    """)
    totals = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM dim_geografia WHERE tiene_comisaria = TRUE;")
    muni_con_comisaria = cur.fetchone()[0]

    cur.execute("SELECT SUM(comisarias_instaladas), SUM(brecha_comisarias) FROM dim_geografia;")
    comis_stats = cur.fetchone()

    # R1: Temporal
    cur.execute("""
        SELECT
            t.anio,
            SUM(f.cantidad_victimas) AS victimas,
            SUM(f.numero_registros) AS denuncias,
            t.es_periodo_completo
        FROM fact_violencia_intrafamiliar f
        JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
        GROUP BY t.anio, t.es_periodo_completo
        ORDER BY t.anio;
    """)
    r1_data = [
        {"anio": r[0], "victimas": int(r[1]), "denuncias": int(r[2]), "es_periodo_completo": r[3]}
        for r in cur.fetchall()
    ]

    # R2: Territorial
    cur.execute("""
        SELECT
            g.departamento,
            SUM(f.cantidad_victimas) AS total_victimas,
            SUM(CASE WHEN g.es_capital THEN f.cantidad_victimas ELSE 0 END) AS victimas_capital
        FROM fact_violencia_intrafamiliar f
        JOIN dim_geografia g ON f.id_geografia = g.id_geografia
        GROUP BY g.departamento
        ORDER BY total_victimas DESC
        LIMIT 10;
    """)
    r2_data = [
        {"departamento": r[0], "total_victimas": int(r[1]), "victimas_capital": int(r[2])}
        for r in cur.fetchall()
    ]

    # R3: Demographics
    cur.execute("""
        SELECT
            v.perfil_demografico,
            v.genero,
            v.grupo_etario,
            v.es_menor_de_edad,
            SUM(f.cantidad_victimas) AS victimas
        FROM fact_violencia_intrafamiliar f
        JOIN dim_victima v ON f.id_victima = v.id_victima
        GROUP BY v.perfil_demografico, v.genero, v.grupo_etario, v.es_menor_de_edad
        ORDER BY victimas DESC;
    """)
    r3_data = [
        {"perfil": r[0], "genero": r[1], "grupo_etario": r[2], "es_menor_de_edad": r[3], "victimas": int(r[4])}
        for r in cur.fetchall()
    ]

    # R4: Mechanisms
    cur.execute("""
        SELECT
            m.categoria_mecanismo,
            m.es_arma_letal,
            SUM(f.cantidad_victimas) AS victimas,
            SUM(f.numero_registros) AS denuncias,
            ROUND(SUM(f.cantidad_victimas)::NUMERIC / NULLIF(SUM(f.numero_registros), 0), 2) AS ratio
        FROM fact_violencia_intrafamiliar f
        JOIN dim_medio m ON f.id_medio = m.id_medio
        GROUP BY m.categoria_mecanismo, m.es_arma_letal
        ORDER BY victimas DESC;
    """)
    r4_data = [
        {"categoria": r[0], "es_arma_letal": r[1], "victimas": int(r[2]), "denuncias": int(r[3]), "ratio": float(r[4])}
        for r in cur.fetchall()
    ]

    # R5: Lethal weapon hotspots for minors
    cur.execute("""
        SELECT
            g.municipio,
            g.departamento,
            SUM(f.cantidad_victimas) AS menores_arma_letal
        FROM fact_violencia_intrafamiliar f
        JOIN dim_geografia g ON f.id_geografia = g.id_geografia
        JOIN dim_victima v ON f.id_victima = v.id_victima
        JOIN dim_medio m ON f.id_medio = m.id_medio
        WHERE v.es_menor_de_edad = TRUE AND m.es_arma_letal = TRUE
        GROUP BY g.municipio, g.departamento
        ORDER BY menores_arma_letal DESC
        LIMIT 10;
    """)
    r5_data = [
        {"municipio": r[0], "departamento": r[1], "menores_letal": int(r[2])}
        for r in cur.fetchall()
    ]

    # R6: Institutional Workload per Comisaría (API INTEGRATION)
    cur.execute("""
        SELECT
            g.codigo_dane_municipio,
            g.municipio,
            g.departamento,
            g.categoria_municipio,
            g.comisarias_instaladas,
            SUM(f.cantidad_victimas) AS total_victimas,
            ROUND(SUM(f.cantidad_victimas)::NUMERIC / NULLIF(g.comisarias_instaladas, 0), 1) AS victimas_por_comisaria,
            CASE
                WHEN g.comisarias_instaladas = 0 THEN 'SIN COMISARÍA'
                WHEN (SUM(f.cantidad_victimas)::NUMERIC / g.comisarias_instaladas) >= 2000 THEN 'SOBRECARGA CRÍTICA (>2,000)'
                WHEN (SUM(f.cantidad_victimas)::NUMERIC / g.comisarias_instaladas) >= 1000 THEN 'SOBRECARGA ALTA (1,000-2,000)'
                ELSE 'CARGA MODERADA (<1,000)'
            END AS nivel_presion
        FROM fact_violencia_intrafamiliar f
        JOIN dim_geografia g ON f.id_geografia = g.id_geografia
        WHERE g.comisarias_instaladas > 0
        GROUP BY g.codigo_dane_municipio, g.municipio, g.departamento, g.categoria_municipio, g.comisarias_instaladas
        ORDER BY victimas_por_comisaria DESC
        LIMIT 15;
    """)
    r6_data = [
        {
            "codigo": r[0], "municipio": r[1], "departamento": r[2], "categoria": r[3],
            "comisarias": int(r[4]), "victimas": int(r[5]), "victimas_por_comisaria": float(r[6]),
            "nivel_presion": r[7]
        }
        for r in cur.fetchall()
    ]

    # R7: Legal Deficit (Ley 2126) vs Severity (API INTEGRATION)
    cur.execute("""
        SELECT
            g.codigo_dane_municipio,
            g.municipio,
            g.departamento,
            g.categoria_municipio,
            g.comisarias_instaladas,
            g.comisarias_requeridas_ley,
            g.brecha_comisarias,
            SUM(CASE WHEN v.es_menor_de_edad AND m.es_arma_letal THEN f.cantidad_victimas ELSE 0 END) AS victimas_menores_arma_letal,
            SUM(CASE WHEN v.genero = 'FEMENINO' THEN f.cantidad_victimas ELSE 0 END) AS victimas_mujeres,
            SUM(f.cantidad_victimas) AS total_victimas,
            CASE
                WHEN g.brecha_comisarias > 0 AND SUM(CASE WHEN v.es_menor_de_edad AND m.es_arma_letal THEN f.cantidad_victimas ELSE 0 END) >= 20
                    THEN 'PRIORIDAD 1 (Déficit + Letalidad Menores)'
                WHEN g.brecha_comisarias > 0 AND SUM(CASE WHEN v.genero = 'FEMENINO' THEN f.cantidad_victimas ELSE 0 END) >= 5000
                    THEN 'PRIORIDAD 2 (Déficit + Alta Violencia Mujeres)'
                ELSE 'PRIORIDAD 3 (Déficit Normativo Ley 2126)'
            END AS prioridad
        FROM fact_violencia_intrafamiliar f
        JOIN dim_geografia g ON f.id_geografia = g.id_geografia
        JOIN dim_victima v ON f.id_victima = v.id_victima
        JOIN dim_medio m ON f.id_medio = m.id_medio
        WHERE g.brecha_comisarias > 0
        GROUP BY g.codigo_dane_municipio, g.municipio, g.departamento, g.categoria_municipio, g.comisarias_instaladas, g.comisarias_requeridas_ley, g.brecha_comisarias
        ORDER BY g.brecha_comisarias DESC, victimas_menores_arma_letal DESC
        LIMIT 15;
    """)
    r7_data = [
        {
            "codigo": r[0], "municipio": r[1], "departamento": r[2], "categoria": r[3],
            "comisarias_instaladas": int(r[4]), "comisarias_requeridas": int(r[5]), "brecha": int(r[6]),
            "menores_letal": int(r[7]), "mujeres": int(r[8]), "total_victimas": int(r[9]),
            "prioridad": r[10]
        }
        for r in cur.fetchall()
    ]

    # R7 Category Summary
    cur.execute("""
        SELECT
            categoria_municipio,
            COUNT(*) AS total_municipios,
            SUM(comisarias_instaladas) AS instaladas,
            SUM(comisarias_requeridas_ley) AS requeridas,
            SUM(brecha_comisarias) AS brecha_total
        FROM dim_geografia
        GROUP BY categoria_municipio
        ORDER BY brecha_total DESC;
    """)
    r7_cat_summary = [
        {"categoria": r[0], "municipios": int(r[1]), "instaladas": int(r[2]), "requeridas": int(r[3]), "brecha": int(r[4])}
        for r in cur.fetchall()
    ]

    payload = {
        "kpis": {
            "total_victimas": int(totals[1]),
            "total_denuncias": int(totals[2]),
            "total_fact_rows": int(totals[0]),
            "total_municipios": 1113,
            "municipios_con_comisaria": int(muni_con_comisaria),
            "total_comisarias_instaladas": int(comis_stats[0]),
            "total_brecha_comisarias": int(comis_stats[1])
        },
        "r1_temporal": r1_data,
        "r2_territorial": r2_data,
        "r3_demographics": r3_data,
        "r4_mechanisms": r4_data,
        "r5_minor_hotspots": r5_data,
        "r6_institutional_pressure": r6_data,
        "r7_legal_gap_priorities": r7_data,
        "r7_category_summary": r7_cat_summary
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Exported dashboard data payload to {OUTPUT_JSON}")
    conn.close()


if __name__ == "__main__":
    export_dashboard_data()
