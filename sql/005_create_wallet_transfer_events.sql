CREATE VIEW wallet_transfer_events AS
SELECT source, source_transfer_id,
from_iban AS wallet_iban,
'OUTGOING'::text AS direction,
category,
amount,
created_at
FROM transfers

UNION ALL

SELECT source,
source_transfer_id,
to_iban AS wallet_iban,
'INCOMING'::text AS direction,
category,
amount,
created_at
FROM transfers;

GRANT SELECT ON public.wallet_transfer_events TO wallet_pipeline;