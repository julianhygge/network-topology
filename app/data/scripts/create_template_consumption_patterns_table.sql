-- Create template_consumption_patterns table to store 15-minute interval consumption patterns
-- for predefined templates

-- Drop the table if it already exists to ensure idempotency
DROP TABLE IF EXISTS load.template_consumption_patterns CASCADE;

-- Create the table
CREATE TABLE load.template_consumption_patterns (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    consumption_kwh DOUBLE PRECISION NOT NULL,
    created_on TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    modified_on TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    
    -- Add foreign key constraint to predefined_templates table
    CONSTRAINT fk_template_consumption_patterns_template
        FOREIGN KEY (template_id) 
        REFERENCES master.predefined_templates(id)
        ON DELETE CASCADE,
        
    -- Add unique constraint to prevent duplicate entries for the same template and timestamp
    CONSTRAINT uq_template_consumption_patterns_template_timestamp
        UNIQUE (template_id, timestamp)
);

-- Create index on template_id for faster lookups
CREATE INDEX idx_template_consumption_patterns_template_id 
    ON load.template_consumption_patterns(template_id);

-- Create index on timestamp for time-based queries
CREATE INDEX idx_template_consumption_patterns_timestamp 
    ON load.template_consumption_patterns(timestamp);

-- Add comment to the table
COMMENT ON TABLE load.template_consumption_patterns IS 
    'Stores 15-minute interval consumption patterns for predefined templates. ' 
    'Each template has a single day of 15-minute intervals that can be repeated ' 
    'to generate longer time periods.';

-- Add comments to columns
COMMENT ON COLUMN load.template_consumption_patterns.id IS 'Primary key';
COMMENT ON COLUMN load.template_consumption_patterns.template_id IS 'Foreign key to master.predefined_templates';
COMMENT ON COLUMN load.template_consumption_patterns.timestamp IS 'Timestamp for the consumption data point (time within a day)';
COMMENT ON COLUMN load.template_consumption_patterns.consumption_kwh IS 'Energy consumption in kilowatt-hours for this time interval';
COMMENT ON COLUMN load.template_consumption_patterns.created_on IS 'Timestamp when the record was created';
COMMENT ON COLUMN load.template_consumption_patterns.modified_on IS 'Timestamp when the record was last modified';

-- Create a trigger function to update modified_on timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_on = NOW() AT TIME ZONE 'utc';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update modified_on timestamp
CREATE TRIGGER update_template_consumption_patterns_modified
BEFORE UPDATE ON load.template_consumption_patterns
FOR EACH ROW EXECUTE FUNCTION update_modified_column();
