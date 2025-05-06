-- This script creates the solar_item_profile table.

CREATE TABLE solar.solar_item_profile (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    solar_profile_id UUID NOT NULL,
    production_kwh DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    voltage_v DOUBLE PRECISION,
    current_amps DOUBLE PRECISION,
    FOREIGN KEY (solar_profile_id) REFERENCES solar.solar_profile (id) ON DELETE CASCADE
);
