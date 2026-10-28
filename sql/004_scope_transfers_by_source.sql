BEGIN;

ALTER TABLE transfers
ADD COLUMN source VARCHAR(255);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM transfers)
       AND (SELECT COUNT(DISTINCT source) FROM pipeline_checkpoints) <> 1
    THEN
        RAISE EXCEPTION
            'Cannot determine one source for existing transfers';
    END IF;

    UPDATE transfers
    SET source = (SELECT MIN(source) FROM pipeline_checkpoints);
END
$$;

ALTER TABLE transfers
ALTER COLUMN source SET NOT NULL;

ALTER TABLE transfers
DROP CONSTRAINT transfers_pkey;

ALTER TABLE transfers
ADD CONSTRAINT transfers_pkey
PRIMARY KEY (source, source_transfer_id);

COMMIT;