-- Seeds the time-series data required by the billing engine, which was lost
-- with the previous database:
--   * solar.solar_installations row for the hardcoded reference site 2609522
--     (see DataPreparationService._get_solar_by_house_id)
--   * solar.site_reference_year_production: full year 2023 at 15-min
--     intervals, bell-shaped daylight curve (06:00-18:00), per-kW generation.
--   * load.template_consumption_patterns: full year 2023 at 15-min intervals
--     for the 3 predefined templates (Type 1/2/3), residential profile with
--     morning and evening peaks, scaled per template.
--
-- The billing engine hardcodes year 2023, so all timestamps use 2023.
-- Re-runnable: deletes previously seeded rows first.

BEGIN;

-- ============ Solar reference site ============
INSERT INTO solar.solar_installations (site_id, name, status, peak_power, type, country, state, city)
VALUES (2609522, 'Reference Site (synthetic)', 'Active', '1', 'Residential', 'India', 'Karnataka', 'Bangalore')
ON CONFLICT (site_id) DO NOTHING;

DELETE FROM solar.site_reference_year_production WHERE site_id = 2609522;

-- Bell curve between 06:00 and 18:00, peak 0.15 kWh per kW per 15-min at noon,
-- with a mild seasonal factor (lower in monsoon/winter months).
INSERT INTO solar.site_reference_year_production (site_id, "timestamp", per_kw_generation)
SELECT
    2609522,
    ts,
    ROUND(
        (CASE
            WHEN (EXTRACT(hour FROM ts) + EXTRACT(minute FROM ts) / 60.0) BETWEEN 6 AND 18
            THEN 0.15
                 * sin(pi() * ((EXTRACT(hour FROM ts) + EXTRACT(minute FROM ts) / 60.0) - 6) / 12)
                 * (0.85 + 0.15 * cos(2 * pi() * (EXTRACT(doy FROM ts) - 100) / 365))
            ELSE 0
        END)::numeric, 6
    )
FROM generate_series(
    '2023-01-01 00:00'::timestamp,
    '2023-12-31 23:45'::timestamp,
    '15 minutes'
) AS ts;

-- ============ Load templates ============
DELETE FROM load.template_consumption_patterns WHERE template_id IN (1, 2, 3);

-- Residential daily shape (kWh per 15-min):
--   00:00-05:45 base 0.04 | 06:00-09:45 morning 0.12 | 10:00-16:45 day 0.07
--   17:00-21:45 evening 0.20 | 22:00-23:45 night 0.06
-- Scaled: Type 1 x0.8, Type 2 x1.0, Type 3 x1.3  (~7.5 / 9.3 / 12.1 kWh/day)
INSERT INTO load.template_consumption_patterns (template_id, "timestamp", consumption_kwh)
SELECT
    tpl.id,
    ts,
    ROUND(
        (tpl.scale * CASE
            WHEN EXTRACT(hour FROM ts) BETWEEN 0 AND 5 THEN 0.04
            WHEN EXTRACT(hour FROM ts) BETWEEN 6 AND 9 THEN 0.12
            WHEN EXTRACT(hour FROM ts) BETWEEN 10 AND 16 THEN 0.07
            WHEN EXTRACT(hour FROM ts) BETWEEN 17 AND 21 THEN 0.20
            ELSE 0.06
        END
        -- small smooth variation so days are not perfectly flat
        * (1 + 0.05 * sin(2 * pi() * EXTRACT(doy FROM ts) / 30)))::numeric, 6
    )
FROM generate_series(
    '2023-01-01 00:00'::timestamp,
    '2023-12-31 23:45'::timestamp,
    '15 minutes'
) AS ts
CROSS JOIN (VALUES (1, 0.8), (2, 1.0), (3, 1.3)) AS tpl(id, scale);

COMMIT;
