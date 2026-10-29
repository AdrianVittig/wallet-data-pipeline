WITH monthly AS (
    SELECT
    e.source,
    e.wallet_iban,
    date_trunc('month', e.created_at)::date AS month,
    COUNT(*) FILTER (WHERE e.direction = 'INCOMING') AS incoming_count,
    COUNT(*) FILTER (WHERE e.direction = 'OUTGOING') AS outgoing_count,
    COALESCE (
        SUM(e.amount) FILTER (WHERE e.direction = 'INCOMING'), 0
    ) AS incoming_amount,
    COALESCE (
        SUM(e.amount) FILTER (WHERE e.direction = 'OUTGOING'), 0
    ) AS outgoing_amount
    FROM wallet_transfer_events AS e
    JOIN pipeline_checkpoints AS p
        ON p.source = e.source
        AND p.wallet_iban = e.wallet_iban
        GROUP BY e.source, e.wallet_iban, date_trunc('month', e.created_at)::date
)
SELECT source,
wallet_iban,
month,
incoming_count,
outgoing_count,
incoming_amount,
outgoing_amount,
incoming_amount - outgoing_amount AS net_amount
FROM monthly
ORDER BY source, wallet_iban, month;