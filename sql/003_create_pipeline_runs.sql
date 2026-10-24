CREATE TABLE pipeline_runs(
    run_id UUID PRIMARY KEY,
    source VARCHAR(255) NOT NULL,
    wallet_iban VARCHAR(255),
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMPTZ,
    status VARCHAR(16) NOT NULL CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED')),
    from_date TIMESTAMP WITHOUT TIME ZONE,
    to_date TIMESTAMP WITHOUT TIME ZONE,
    fetched BIGINT NOT NULL DEFAULT 0 CHECK (fetched >= 0),
    valid BIGINT NOT NULL DEFAULT 0 CHECK (valid >= 0),
    rejected BIGINT NOT NULL DEFAULT 0 CHECK (rejected >= 0),
    inserted BIGINT NOT NULL DEFAULT 0 CHECK (inserted >= 0),
    skipped BIGINT NOT NULL DEFAULT 0 CHECK (skipped >= 0),
    error_message TEXT
);


CREATE TABLE rejected_transfers(
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES pipeline_runs(run_id),
    record JSONB NOT NULL,
    reason TEXT NOT NULL,
    rejected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


