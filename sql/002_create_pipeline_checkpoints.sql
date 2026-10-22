CREATE TABLE pipeline_checkpoints(
    source VARCHAR(255) NOT NULL,
    wallet_iban VARCHAR(255) NOT NULL,
    processed_until TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source, wallet_iban)
);

