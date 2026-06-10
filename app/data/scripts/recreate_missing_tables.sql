-- Recreates 4 tables missing from network-topology-int vs the reference
-- pg_dump (app/simulation_engine_schema.txt):
--   load.template_consumption_patterns
--   transactional.house_flags
--   simulation_engine.tou_rate_policy_params
--   simulation_engine.simulation_selected_policies

-- =========================
-- public.update_modified_column() trigger function (used by template_consumption_patterns)
-- =========================
CREATE OR REPLACE FUNCTION public.update_modified_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.modified_on = NOW() AT TIME ZONE 'utc';
    RETURN NEW;
END;
$$;
ALTER FUNCTION public.update_modified_column() OWNER TO postgres;

-- =========================
-- load.template_consumption_patterns
-- =========================
CREATE TABLE load.template_consumption_patterns (
    id integer NOT NULL,
    template_id integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    consumption_kwh double precision NOT NULL,
    created_on timestamp without time zone DEFAULT (now() AT TIME ZONE 'utc'::text),
    modified_on timestamp without time zone DEFAULT (now() AT TIME ZONE 'utc'::text)
);
ALTER TABLE load.template_consumption_patterns OWNER TO "p2p-simulator-user";

COMMENT ON TABLE load.template_consumption_patterns IS 'Stores 15-minute interval consumption patterns for predefined templates. Each template has a single day of 15-minute intervals that can be repeated to generate longer time periods.';
COMMENT ON COLUMN load.template_consumption_patterns.id IS 'Primary key';
COMMENT ON COLUMN load.template_consumption_patterns.template_id IS 'Foreign key to master.predefined_templates';
COMMENT ON COLUMN load.template_consumption_patterns."timestamp" IS 'Timestamp for the consumption data point (time within a day)';
COMMENT ON COLUMN load.template_consumption_patterns.consumption_kwh IS 'Energy consumption in kilowatt-hours for this time interval';
COMMENT ON COLUMN load.template_consumption_patterns.created_on IS 'Timestamp when the record was created';
COMMENT ON COLUMN load.template_consumption_patterns.modified_on IS 'Timestamp when the record was last modified';

CREATE SEQUENCE load.template_consumption_patterns_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE load.template_consumption_patterns_id_seq OWNER TO "p2p-simulator-user";
ALTER SEQUENCE load.template_consumption_patterns_id_seq OWNED BY load.template_consumption_patterns.id;
ALTER TABLE ONLY load.template_consumption_patterns ALTER COLUMN id SET DEFAULT nextval('load.template_consumption_patterns_id_seq'::regclass);

ALTER TABLE ONLY load.template_consumption_patterns
    ADD CONSTRAINT template_consumption_patterns_pkey PRIMARY KEY (id);
ALTER TABLE ONLY load.template_consumption_patterns
    ADD CONSTRAINT uq_template_consumption_patterns_template_timestamp UNIQUE (template_id, "timestamp");
ALTER TABLE ONLY load.template_consumption_patterns
    ADD CONSTRAINT fk_template_consumption_patterns_template FOREIGN KEY (template_id) REFERENCES master.predefined_templates(id) ON DELETE CASCADE;

CREATE INDEX idx_template_consumption_patterns_template_id ON load.template_consumption_patterns USING btree (template_id);
CREATE INDEX idx_template_consumption_patterns_timestamp ON load.template_consumption_patterns USING btree ("timestamp");

CREATE TRIGGER update_template_consumption_patterns_modified BEFORE UPDATE ON load.template_consumption_patterns FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();

-- =========================
-- transactional.house_flags
-- =========================
CREATE TABLE transactional.house_flags (
    id integer NOT NULL,
    house_id uuid NOT NULL,
    flag_type character varying(50),
    flag_value character varying(50) NOT NULL,
    created_by uuid,
    created_on timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    modified_on timestamp without time zone NOT NULL,
    modified_by uuid,
    active boolean NOT NULL
);
ALTER TABLE transactional.house_flags OWNER TO "p2p-simulator-user";

ALTER TABLE transactional.house_flags ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME transactional.house_flags_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

ALTER TABLE ONLY transactional.house_flags
    ADD CONSTRAINT house_flags_pkey PRIMARY KEY (id);
ALTER TABLE ONLY transactional.house_flags
    ADD CONSTRAINT fk_house FOREIGN KEY (house_id) REFERENCES transactional.houses(id) ON DELETE CASCADE;

CREATE INDEX idx_house_flags_flag_type ON transactional.house_flags USING btree (flag_type);
CREATE INDEX idx_house_flags_house_id ON transactional.house_flags USING btree (house_id);

-- =========================
-- simulation_engine.tou_rate_policy_params
-- =========================
CREATE TABLE simulation_engine.tou_rate_policy_params (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    simulation_run_id uuid NOT NULL,
    time_period_label character varying(100),
    start_time time without time zone,
    end_time time without time zone,
    import_retail_rate_per_kwh numeric(10,4) NOT NULL,
    export_wholesale_rate_per_kwh numeric(10,4) NOT NULL
);
ALTER TABLE simulation_engine.tou_rate_policy_params OWNER TO postgres;

ALTER TABLE ONLY simulation_engine.tou_rate_policy_params
    ADD CONSTRAINT tou_rate_policy_params_pkey PRIMARY KEY (id);
ALTER TABLE ONLY simulation_engine.tou_rate_policy_params
    ADD CONSTRAINT fk_simulation_run FOREIGN KEY (simulation_run_id) REFERENCES simulation_engine.simulation_runs(id) ON DELETE CASCADE;

CREATE INDEX idx_tou_rate_policy_params_simulation_run_id ON simulation_engine.tou_rate_policy_params USING btree (simulation_run_id);

-- =========================
-- simulation_engine.simulation_selected_policies
-- =========================
CREATE TABLE simulation_engine.simulation_selected_policies (
    simulation_run_id uuid NOT NULL,
    net_metering_policy_type_id uuid NOT NULL,
    fixed_charge_tariff_rate_per_kw numeric(10,4) DEFAULT 210.0,
    fac_charge_per_kwh_imported numeric(10,4) DEFAULT 0.0,
    tax_rate_on_energy_charges numeric(5,4) DEFAULT 0.09
);
ALTER TABLE simulation_engine.simulation_selected_policies OWNER TO postgres;

ALTER TABLE ONLY simulation_engine.simulation_selected_policies
    ADD CONSTRAINT simulation_selected_policies_pkey PRIMARY KEY (simulation_run_id);
ALTER TABLE ONLY simulation_engine.simulation_selected_policies
    ADD CONSTRAINT fk_net_metering_policy_type FOREIGN KEY (net_metering_policy_type_id) REFERENCES master.net_metering_policy_types(id);
ALTER TABLE ONLY simulation_engine.simulation_selected_policies
    ADD CONSTRAINT fk_simulation_run FOREIGN KEY (simulation_run_id) REFERENCES simulation_engine.simulation_runs(id) ON DELETE CASCADE;

CREATE INDEX idx_simulation_selected_policies_policy_type_id ON simulation_engine.simulation_selected_policies USING btree (net_metering_policy_type_id);
