-- ============================================================================
-- Star Schema DDL for Refined Domestic Violence Data Warehouse (PostgreSQL)
-- Second Delivery: Integrated Primary Source (DIJIN) + API (MinJusticia Comisarías)
-- Declared Fact Grain: One row per (date, municipality, victim cohort, mechanism)
-- Enforced strictly by CONSTRAINT uq_fact_grano
-- ============================================================================

DROP TABLE IF EXISTS fact_violencia_intrafamiliar CASCADE;
DROP TABLE IF EXISTS dim_comisaria CASCADE;
DROP TABLE IF EXISTS dim_geografia CASCADE;
DROP TABLE IF EXISTS dim_tiempo CASCADE;
DROP TABLE IF EXISTS dim_victima CASCADE;
DROP TABLE IF EXISTS dim_medio CASCADE;

-- 1. dim_tiempo: Dense daily calendar from 2010 to 2026
CREATE TABLE dim_tiempo (
    id_tiempo            INT         PRIMARY KEY,
    fecha                DATE        NOT NULL,
    anio                 INT         NOT NULL,
    mes                  INT         NOT NULL CHECK (mes BETWEEN 1 AND 12),
    nombre_mes           VARCHAR(20) NOT NULL,
    trimestre            INT         NOT NULL CHECK (trimestre BETWEEN 1 AND 4),
    semestre             INT         NOT NULL CHECK (semestre IN (1, 2)),
    dia_semana           INT         NOT NULL CHECK (dia_semana BETWEEN 1 AND 7),
    nombre_dia           VARCHAR(20) NOT NULL,
    es_fin_semana        BOOLEAN     NOT NULL,
    es_periodo_completo  BOOLEAN     NOT NULL,
    CONSTRAINT uq_dim_tiempo_fecha UNIQUE (fecha)
);

-- 2. dim_geografia: Enriched with Comisarías de Familia institutional capacity & legal gap (Ley 2126 / Ley 617)
CREATE TABLE dim_geografia (
    id_geografia             INT          PRIMARY KEY,
    codigo_dane_municipio    CHAR(5)      NOT NULL,
    municipio                VARCHAR(150) NOT NULL,
    codigo_dane_departamento CHAR(2)      NOT NULL,
    departamento             VARCHAR(100) NOT NULL,
    es_capital               BOOLEAN      NOT NULL,
    categoria_municipio      VARCHAR(50)  NOT NULL,
    comisarias_instaladas    INT          NOT NULL CHECK (comisarias_instaladas >= 0),
    comisarias_requeridas_ley INT         NOT NULL CHECK (comisarias_requeridas_ley >= 0),
    brecha_comisarias        INT          NOT NULL CHECK (brecha_comisarias >= 0),
    tiene_comisaria          BOOLEAN      NOT NULL,
    CONSTRAINT uq_dim_geografia_dane UNIQUE (codigo_dane_municipio),
    CONSTRAINT ck_dim_geografia_prefijo
        CHECK (LEFT(codigo_dane_municipio, 2) = codigo_dane_departamento)
);

-- 3. dim_victima: Socio-demographic cohorts and child vulnerability indicator (SDG 5.2 & 16.1)
CREATE TABLE dim_victima (
    id_victima         INT          PRIMARY KEY,
    genero             VARCHAR(50)  NOT NULL,
    grupo_etario       VARCHAR(50)  NOT NULL,
    perfil_demografico VARCHAR(100) NOT NULL,
    es_menor_de_edad   BOOLEAN      NOT NULL,
    CONSTRAINT uq_dim_victima_cohorte UNIQUE (genero, grupo_etario)
);

-- 4. dim_medio: Means of aggression, harmonized mechanism categories, and lethality flag
CREATE TABLE dim_medio (
    id_medio            INT          PRIMARY KEY,
    medio_agresion      VARCHAR(100) NOT NULL,
    categoria_mecanismo VARCHAR(100) NOT NULL,
    es_arma_letal       BOOLEAN      NOT NULL,
    CONSTRAINT uq_dim_medio_natural UNIQUE (medio_agresion, categoria_mecanismo)
);

-- 5. dim_comisaria: Outrigger directory of physical comisarías for operational/geospatial analytics
CREATE TABLE dim_comisaria (
    id_comisaria          INT          PRIMARY KEY,
    codigo_dane_municipio CHAR(5)      NOT NULL,
    nombre_comisaria      TEXT         NOT NULL,
    direccion             TEXT         NOT NULL,
    telefono              TEXT         NOT NULL,
    horario_atencion      TEXT         NOT NULL,
    categoria_municipio   TEXT         NOT NULL,
    CONSTRAINT fk_comisaria_geografia
        FOREIGN KEY (codigo_dane_municipio) REFERENCES dim_geografia(codigo_dane_municipio)
);

-- 6. fact_violencia_intrafamiliar: Transaction fact table aggregated to the declared municipal grain
CREATE TABLE fact_violencia_intrafamiliar (
    id_hecho          BIGINT    PRIMARY KEY,
    id_tiempo         INT       NOT NULL,
    id_geografia      INT       NOT NULL,
    id_victima        INT       NOT NULL,
    id_medio          INT       NOT NULL,
    cantidad_victimas INT       NOT NULL CHECK (cantidad_victimas > 0),
    numero_registros  INT       NOT NULL CHECK (numero_registros > 0),
    fecha_carga       TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_fact_grano
        UNIQUE (id_tiempo, id_geografia, id_victima, id_medio),
    CONSTRAINT ck_fact_medida
        CHECK (cantidad_victimas >= numero_registros),

    CONSTRAINT fk_fact_tiempo    FOREIGN KEY (id_tiempo)    REFERENCES dim_tiempo(id_tiempo),
    CONSTRAINT fk_fact_geografia FOREIGN KEY (id_geografia) REFERENCES dim_geografia(id_geografia),
    CONSTRAINT fk_fact_victima   FOREIGN KEY (id_victima)   REFERENCES dim_victima(id_victima),
    CONSTRAINT fk_fact_medio     FOREIGN KEY (id_medio)     REFERENCES dim_medio(id_medio)
);

-- Indexes for star joins and common analytical filters
CREATE INDEX idx_fact_tiempo        ON fact_violencia_intrafamiliar(id_tiempo);
CREATE INDEX idx_fact_geografia     ON fact_violencia_intrafamiliar(id_geografia);
CREATE INDEX idx_fact_victima       ON fact_violencia_intrafamiliar(id_victima);
CREATE INDEX idx_fact_medio         ON fact_violencia_intrafamiliar(id_medio);
CREATE INDEX idx_fact_composite     ON fact_violencia_intrafamiliar(id_tiempo, id_geografia);

CREATE INDEX idx_dim_tiempo_anio    ON dim_tiempo(anio);
CREATE INDEX idx_dim_geo_depto      ON dim_geografia(codigo_dane_departamento);
CREATE INDEX idx_dim_geo_categoria  ON dim_geografia(categoria_municipio);
CREATE INDEX idx_dim_geo_brecha     ON dim_geografia(brecha_comisarias);
