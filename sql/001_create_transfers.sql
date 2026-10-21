CREATE TABLE transfers(
    source_transfer_id BIGINT PRIMARY KEY,
    from_iban VARCHAR(255) NOT NULL,
    to_iban VARCHAR(255) NOT NULL,
    amount NUMERIC(38,2) NOT NULL CHECK (amount > 0),
    category VARCHAR(32) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    loaded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

