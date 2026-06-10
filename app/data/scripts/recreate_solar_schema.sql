-- Recreates the missing "solar" schema (tables, sequences, indexes, FKs, functions)
-- for network-topology-int, based on app/simulation_engine_schema.txt (reference pg_dump).

CREATE SCHEMA IF NOT EXISTS solar;
ALTER SCHEMA solar OWNER TO "p2p-simulator-user";

-- =========================
-- Tables
-- =========================

CREATE TABLE solar.solar_profile (
    id uuid NOT NULL,
    active boolean DEFAULT true NOT NULL,
    created_by uuid NOT NULL,
    created_on timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified_by uuid NOT NULL,
    modified_on timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    solar_available boolean NOT NULL,
    installed_capacity_kw numeric,
    tilt_type character varying(12) NOT NULL,
    years_since_installation real,
    available_space_sqft numeric,
    simulate_using_different_capacity boolean,
    capacity_for_simulation_kw numeric,
    house_id uuid NOT NULL,
    simulated_available_space_sqft numeric
);
ALTER TABLE solar.solar_profile OWNER TO "p2p-simulator-user";
ALTER TABLE ONLY solar.solar_profile ADD CONSTRAINT solar_profile_pkey PRIMARY KEY (id);

CREATE TABLE solar.solar_item_profile (
    id integer NOT NULL,
    solar_profile_id uuid NOT NULL,
    production_kwh double precision NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    voltage_v double precision,
    current_amps double precision
);
ALTER TABLE solar.solar_item_profile OWNER TO "p2p-simulator-user";

CREATE SEQUENCE solar.solar_item_profile_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE solar.solar_item_profile_id_seq OWNER TO "p2p-simulator-user";
ALTER SEQUENCE solar.solar_item_profile_id_seq OWNED BY solar.solar_item_profile.id;
ALTER TABLE ONLY solar.solar_item_profile ALTER COLUMN id SET DEFAULT nextval('solar.solar_item_profile_id_seq'::regclass);
ALTER TABLE ONLY solar.solar_item_profile ADD CONSTRAINT solar_item_profile_pkey PRIMARY KEY (id);
ALTER TABLE ONLY solar.solar_item_profile
    ADD CONSTRAINT solar_item_profile_solar_profile_id_fkey
    FOREIGN KEY (solar_profile_id) REFERENCES solar.solar_profile(id) ON DELETE CASCADE;

CREATE TABLE solar.solar_installations (
    site_id integer NOT NULL,
    name character varying(255),
    status character varying(255),
    peak_power character varying(255),
    type character varying(255),
    zip_code character varying(255),
    address character varying(255),
    country character varying(255),
    state character varying(255),
    city character varying(255),
    installation_date character varying(255),
    last_reporting_time character varying(255),
    location character varying(255),
    secondary_address character varying(255),
    updated_on timestamp without time zone,
    has_csv boolean DEFAULT false NOT NULL,
    uploaded_on timestamp without time zone,
    profile_updated_on timestamp without time zone
);
ALTER TABLE solar.solar_installations OWNER TO "p2p-simulator-user";
ALTER TABLE ONLY solar.solar_installations ADD CONSTRAINT solar_installations_pkey PRIMARY KEY (site_id);

CREATE TABLE solar.site_production_data (
    id integer NOT NULL,
    site_id integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    production double precision NOT NULL
);
ALTER TABLE solar.site_production_data OWNER TO "p2p-simulator-user";

CREATE SEQUENCE solar.site_production_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE solar.site_production_data_id_seq OWNER TO "p2p-simulator-user";
ALTER SEQUENCE solar.site_production_data_id_seq OWNED BY solar.site_production_data.id;
ALTER TABLE ONLY solar.site_production_data ALTER COLUMN id SET DEFAULT nextval('solar.site_production_data_id_seq'::regclass);
ALTER TABLE ONLY solar.site_production_data ADD CONSTRAINT site_production_data_pkey PRIMARY KEY (id);
ALTER TABLE ONLY solar.site_production_data
    ADD CONSTRAINT site_production_data_site_id_fkey
    FOREIGN KEY (site_id) REFERENCES solar.solar_installations(site_id);

CREATE INDEX siteproductiondata_site_id ON solar.site_production_data USING btree (site_id);
CREATE UNIQUE INDEX siteproductiondata_site_id_timestamp ON solar.site_production_data USING btree (site_id, "timestamp");

CREATE TABLE solar.site_reference_year_production (
    id integer NOT NULL,
    site_id integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    per_kw_generation double precision NOT NULL
);
ALTER TABLE solar.site_reference_year_production OWNER TO "p2p-simulator-user";

CREATE SEQUENCE solar.site_reference_year_production_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE solar.site_reference_year_production_id_seq OWNER TO "p2p-simulator-user";
ALTER SEQUENCE solar.site_reference_year_production_id_seq OWNED BY solar.site_reference_year_production.id;
ALTER TABLE ONLY solar.site_reference_year_production ALTER COLUMN id SET DEFAULT nextval('solar.site_reference_year_production_id_seq'::regclass);
ALTER TABLE ONLY solar.site_reference_year_production ADD CONSTRAINT site_reference_year_production_pkey PRIMARY KEY (id);
ALTER TABLE ONLY solar.site_reference_year_production
    ADD CONSTRAINT unique_site_timestamp UNIQUE (site_id, "timestamp");
ALTER TABLE ONLY solar.site_reference_year_production
    ADD CONSTRAINT site_reference_year_production_site_id_fkey
    FOREIGN KEY (site_id) REFERENCES solar.solar_installations(site_id);

CREATE INDEX sitereferenceyearproduction_site_id ON solar.site_reference_year_production USING btree (site_id);
CREATE UNIQUE INDEX sitereferenceyearproduction_site_id_reference_timestamp ON solar.site_reference_year_production USING btree (site_id, "timestamp");

-- =========================
-- Functions (as defined in reference dump)
-- Note: get_yearly_profile() references solar.daily_generation_profile,
-- which does not exist in the reference dump either (pre-existing gap,
-- not something this script introduces).
-- =========================

CREATE FUNCTION solar.is_complete_day(site_id_param integer, day_date date) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    expected_count INTEGER;
    actual_count INTEGER;
    zero_count INTEGER;
BEGIN
    expected_count := 96;

    SELECT COUNT(*) INTO actual_count
    FROM solar.site_production_data
    WHERE site_id = site_id_param
    AND timestamp::date = day_date;

    SELECT COUNT(*) INTO zero_count
    FROM solar.site_production_data
    WHERE site_id = site_id_param
    AND timestamp::date = day_date
    AND production = 0;

    RETURN actual_count >= (expected_count * 0.9) AND zero_count < expected_count;
END;
$$;
ALTER FUNCTION solar.is_complete_day(site_id_param integer, day_date date) OWNER TO postgres;

CREATE FUNCTION solar.get_yearly_profile(site_id_param integer) RETURNS TABLE(month integer, day integer, hour integer, minute integer, avg_generation_per_kw numeric)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    WITH valid_days AS (
        SELECT DISTINCT
            gp.site_id,
            gp.day_date
        FROM
            solar.daily_generation_profile gp
        WHERE
            gp.site_id = site_id_param
            AND solar.is_complete_day(site_id_param, gp.day_date)
    ),
    day_coverage AS (
        SELECT
            EXTRACT(MONTH FROM day_date) AS month,
            EXTRACT(DAY FROM day_date) AS day,
            COUNT(DISTINCT EXTRACT(YEAR FROM day_date)) AS year_count
        FROM
            valid_days
        GROUP BY
            EXTRACT(MONTH FROM day_date), EXTRACT(DAY FROM day_date)
    )
    SELECT
        EXTRACT(MONTH FROM gp.day_date)::INTEGER AS month,
        EXTRACT(DAY FROM gp.day_date)::INTEGER AS day,
        gp.hour::INTEGER,
        gp.minute::INTEGER,
        AVG(gp.avg_generation_per_kw)::NUMERIC AS avg_generation_per_kw
    FROM
        solar.daily_generation_profile gp
    JOIN
        valid_days vd ON gp.site_id = vd.site_id AND gp.day_date = vd.day_date
    JOIN
        day_coverage dc ON dc.month = EXTRACT(MONTH FROM gp.day_date) AND dc.day = EXTRACT(DAY FROM gp.day_date)
    GROUP BY
        EXTRACT(MONTH FROM gp.day_date), EXTRACT(DAY FROM gp.day_date), gp.hour, gp.minute
    ORDER BY
        month, day, hour, minute;
END;
$$;
ALTER FUNCTION solar.get_yearly_profile(site_id_param integer) OWNER TO postgres;
