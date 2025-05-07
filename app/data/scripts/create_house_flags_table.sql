CREATE TABLE transactional.house_flags (
    id SERIAL PRIMARY KEY,  
    house_id UUID NOT NULL,
    flag_type VARCHAR(50) NULL,
    flag_value VARCHAR(50) NULL,

    CONSTRAINT fk_house
        FOREIGN KEY(house_id)
        REFERENCES transactional.houses(id)
        ON DELETE CASCADE
);

-- Optional: Add indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_house_flags_house_id ON transactional.house_flags(house_id);
CREATE INDEX IF NOT EXISTS idx_house_flags_flag_type ON transactional.house_flags(flag_type);