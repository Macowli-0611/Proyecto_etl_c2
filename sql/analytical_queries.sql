-- ============================================================================
-- Analytical SQL Queries Supporting Requirements R1 through R7
-- Data Warehouse: PostgreSQL (etl_dw)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- R1: Temporal dynamics, annual growth and pandemic inflection point
-- ----------------------------------------------------------------------------
WITH serie_anual AS (
    SELECT
        t.anio,
        SUM(f.cantidad_victimas) AS total_victimas,
        SUM(f.numero_registros)  AS total_denuncias,
        t.es_periodo_completo
    FROM fact_violencia_intrafamiliar f
    JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
    GROUP BY t.anio, t.es_periodo_completo
)
SELECT
    anio,
    total_victimas,
    total_denuncias,
    LAG(total_victimas) OVER (ORDER BY anio) AS victimas_anio_anterior,
    ROUND(
        (total_victimas - LAG(total_victimas) OVER (ORDER BY anio))::NUMERIC /
        NULLIF(LAG(total_victimas) OVER (ORDER BY anio), 0) * 100, 2
    ) AS crecimiento_yoy_pct,
    es_periodo_completo
FROM serie_anual
ORDER BY anio;

-- ----------------------------------------------------------------------------
-- R2: Territorial concentration and capital-city asymmetry
-- ----------------------------------------------------------------------------
WITH depto_totales AS (
    SELECT
        g.departamento,
        SUM(f.cantidad_victimas) AS victimas_depto,
        SUM(CASE WHEN g.es_capital THEN f.cantidad_victimas ELSE 0 END) AS victimas_capital
    FROM fact_violencia_intrafamiliar f
    JOIN dim_geografia g ON f.id_geografia = g.id_geografia
    GROUP BY g.departamento
),
nacional AS (
    SELECT SUM(cantidad_victimas) AS victimas_nacional FROM fact_violencia_intrafamiliar
)
SELECT
    d.departamento,
    d.victimas_depto,
    ROUND((d.victimas_depto::NUMERIC / n.victimas_nacional) * 100, 2) AS participacion_nacional_pct,
    d.victimas_capital,
    ROUND((d.victimas_capital::NUMERIC / NULLIF(d.victimas_depto, 0)) * 100, 2) AS participacion_capital_pct
FROM depto_totales d, nacional n
ORDER BY d.victimas_depto DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- R3: Socio-demographic disparity and gender intersectionality
-- ----------------------------------------------------------------------------
WITH cohorte_totales AS (
    SELECT
        v.genero,
        v.grupo_etario,
        v.perfil_demografico,
        v.es_menor_de_edad,
        SUM(f.cantidad_victimas) AS victimas_cohorte
    FROM fact_violencia_intrafamiliar f
    JOIN dim_victima v ON f.id_victima = v.id_victima
    GROUP BY v.genero, v.grupo_etario, v.perfil_demografico, v.es_menor_de_edad
),
nacional AS (
    SELECT SUM(cantidad_victimas) AS victimas_nacional FROM fact_violencia_intrafamiliar
)
SELECT
    c.perfil_demografico,
    c.genero,
    c.grupo_etario,
    c.es_menor_de_edad,
    c.victimas_cohorte,
    ROUND((c.victimas_cohorte::NUMERIC / n.victimas_nacional) * 100, 2) AS participacion_nacional_pct
FROM cohorte_totales c, nacional n
ORDER BY c.victimas_cohorte DESC;

-- ----------------------------------------------------------------------------
-- R4: Means of aggression, lethality, and victims per report
-- ----------------------------------------------------------------------------
WITH mecanismo_totales AS (
    SELECT
        m.categoria_mecanismo,
        m.es_arma_letal,
        SUM(f.cantidad_victimas) AS total_victimas,
        SUM(f.numero_registros)  AS total_denuncias
    FROM fact_violencia_intrafamiliar f
    JOIN dim_medio m ON f.id_medio = m.id_medio
    GROUP BY m.categoria_mecanismo, m.es_arma_letal
),
nacional AS (
    SELECT SUM(cantidad_victimas) AS victimas_nacional FROM fact_violencia_intrafamiliar
)
SELECT
    mt.categoria_mecanismo,
    mt.es_arma_letal,
    mt.total_victimas,
    ROUND((mt.total_victimas::NUMERIC / n.victimas_nacional) * 100, 2) AS participacion_nacional_pct,
    mt.total_denuncias,
    ROUND(mt.total_victimas::NUMERIC / NULLIF(mt.total_denuncias, 0), 2) AS victimas_por_denuncia
FROM mecanismo_totales mt, nacional n
ORDER BY mt.total_victimas DESC;

-- ----------------------------------------------------------------------------
-- R5: Priority hotspot matrix for minors attacked with lethal weapons
-- ----------------------------------------------------------------------------
WITH menores_letales AS (
    SELECT
        g.codigo_dane_municipio,
        g.municipio,
        g.departamento,
        SUM(f.cantidad_victimas) AS menores_arma_letal
    FROM fact_violencia_intrafamiliar f
    JOIN dim_geografia g ON f.id_geografia = g.id_geografia
    JOIN dim_victima v ON f.id_victima = v.id_victima
    JOIN dim_medio m ON f.id_medio = m.id_medio
    WHERE v.es_menor_de_edad = TRUE AND m.es_arma_letal = TRUE
    GROUP BY g.codigo_dane_municipio, g.municipio, g.departamento
),
menores_totales_muni AS (
    SELECT
        g.codigo_dane_municipio,
        SUM(f.cantidad_victimas) AS total_menores_municipio
    FROM fact_violencia_intrafamiliar f
    JOIN dim_geografia g ON f.id_geografia = g.id_geografia
    JOIN dim_victima v ON f.id_victima = v.id_victima
    WHERE v.es_menor_de_edad = TRUE
    GROUP BY g.codigo_dane_municipio
)
SELECT
    ml.codigo_dane_municipio,
    ml.municipio,
    ml.departamento,
    ml.menores_arma_letal,
    mtm.total_menores_municipio,
    ROUND((ml.menores_arma_letal::NUMERIC / NULLIF(mtm.total_menores_municipio, 0)) * 100, 2) AS tasa_letalidad_menores_pct
FROM menores_letales ml
JOIN menores_totales_muni mtm ON ml.codigo_dane_municipio = mtm.codigo_dane_municipio
ORDER BY ml.menores_arma_letal DESC
LIMIT 15;

-- ============================================================================
-- R6: INSTITUTIONAL WORKLOAD & PRESSURE PER COMISARÍA DE FAMILIA (API INTEGRATED)
-- Question: Which municipalities face critical institutional overload in their Comisarías?
-- Metric: Tasa de carga de víctimas por comisaría instalada
-- ============================================================================
SELECT
    g.codigo_dane_municipio,
    g.municipio,
    g.departamento,
    g.categoria_municipio,
    g.comisarias_instaladas,
    SUM(f.cantidad_victimas) AS total_victimas,
    ROUND(
        SUM(f.cantidad_victimas)::NUMERIC / NULLIF(g.comisarias_instaladas, 0), 1
    ) AS victimas_por_comisaria,
    CASE
        WHEN g.comisarias_instaladas = 0 THEN 'SIN COMISARÍA (DESPROTEGIDO)'
        WHEN (SUM(f.cantidad_victimas)::NUMERIC / g.comisarias_instaladas) >= 2000 THEN 'SOBRECARGA CRÍTICA (>2,000)'
        WHEN (SUM(f.cantidad_victimas)::NUMERIC / g.comisarias_instaladas) >= 1000 THEN 'SOBRECARGA ALTA (1,000-2,000)'
        ELSE 'CARGA MODERADA (<1,000)'
    END AS nivel_presion_institucional
FROM fact_violencia_intrafamiliar f
JOIN dim_geografia g ON f.id_geografia = g.id_geografia
GROUP BY
    g.codigo_dane_municipio, g.municipio, g.departamento,
    g.categoria_municipio, g.comisarias_instaladas
ORDER BY victimas_por_comisaria DESC NULLS FIRST
LIMIT 20;

-- ============================================================================
-- R7: INSTITUTIONAL DEFICIT (LEY 2126) VS CHILD & GENDER SEVERITY (API INTEGRATED)
-- Question: Where does legal deficit coincide with high lethal violence against children or women?
-- Metrics: Brecha de comisarías, Índice de Prioridad de Intervención
-- ============================================================================
WITH metricas_riesgo AS (
    SELECT
        g.codigo_dane_municipio,
        g.municipio,
        g.departamento,
        g.categoria_municipio,
        g.comisarias_instaladas,
        g.comisarias_requeridas_ley,
        g.brecha_comisarias,
        SUM(f.cantidad_victimas) AS total_victimas,
        SUM(CASE WHEN v.es_menor_de_edad AND m.es_arma_letal THEN f.cantidad_victimas ELSE 0 END) AS victimas_menores_arma_letal,
        SUM(CASE WHEN v.genero = 'FEMENINO' THEN f.cantidad_victimas ELSE 0 END) AS victimas_mujeres
    FROM fact_violencia_intrafamiliar f
    JOIN dim_geografia g ON f.id_geografia = g.id_geografia
    JOIN dim_victima v ON f.id_victima = v.id_victima
    JOIN dim_medio m ON f.id_medio = m.id_medio
    GROUP BY
        g.codigo_dane_municipio, g.municipio, g.departamento,
        g.categoria_municipio, g.comisarias_instaladas,
        g.comisarias_requeridas_ley, g.brecha_comisarias
)
SELECT
    codigo_dane_municipio,
    municipio,
    departamento,
    categoria_municipio,
    comisarias_instaladas,
    comisarias_requeridas_ley,
    brecha_comisarias,
    victimas_menores_arma_letal,
    victimas_mujeres,
    total_victimas,
    CASE
        WHEN brecha_comisarias > 0 AND victimas_menores_arma_letal >= 20 THEN 'PRIORIDAD URGENTE 1 (Déficit + Letalidad Menores)'
        WHEN brecha_comisarias > 0 AND victimas_mujeres >= 5000 THEN 'PRIORIDAD ALTA 2 (Déficit + Alta Violencia Mujeres)'
        WHEN brecha_comisarias > 0 THEN 'PRIORIDAD MEDIA (Déficit Legal Ley 2126)'
        ELSE 'COBERTURA NORMATIVA CUMPLIDA'
    END AS indice_prioridad_intervencion
FROM metricas_riesgo
WHERE brecha_comisarias > 0
ORDER BY brecha_comisarias DESC, victimas_menores_arma_letal DESC
LIMIT 20;

-- ----------------------------------------------------------------------------
-- R7 Sub-analysis: Distribution of institutional gap by municipal category (Ley 617)
-- ----------------------------------------------------------------------------
SELECT
    categoria_municipio,
    COUNT(*) AS total_municipios,
    SUM(comisarias_instaladas) AS total_comisarias_instaladas,
    SUM(comisarias_requeridas_ley) AS total_comisarias_requeridas,
    SUM(brecha_comisarias) AS brecha_total_comisarias,
    ROUND(AVG(brecha_comisarias), 2) AS brecha_promedio_por_municipio
FROM dim_geografia
GROUP BY categoria_municipio
ORDER BY brecha_total_comisarias DESC;
