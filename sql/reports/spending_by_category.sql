SELECT
    e.source,
    e.wallet_iban,
    e.category,
    COUNT(*) AS transfer_count,
    SUM(e.amount) AS spent_amount
FROM wallet_transfer_events AS e
JOIN pipeline_checkpoints AS p
    ON p.source = e.source
    AND p.wallet_iban = e.wallet_iban
WHERE e.direction = 'OUTGOING'
GROUP BY e.source, e.wallet_iban, e.category
ORDER BY e.source, e.wallet_iban, spent_amount DESC;
