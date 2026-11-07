-- QUERY 1: Portfolio value, unrealized P&L, and position count by client.
-- Only the 2026-10-31 valuation snapshot is used (no duplicate valuation across months).
SELECT c.client_id, c.segment, c.city,
       ROUND(SUM(h.units * p.price_inr), 2) AS portfolio_value_inr,
       ROUND(SUM(h.units * (p.price_inr - h.average_cost_inr)), 2) AS unrealized_pnl_inr,
       COUNT(*) AS holdings_count
FROM holdings h
JOIN clients c ON c.client_id = h.client_id
JOIN prices p ON p.instrument_id = h.instrument_id
WHERE p.as_of_date = '2026-10-31'
GROUP BY c.client_id, c.segment, c.city
ORDER BY portfolio_value_inr DESC;

-- QUERY 2: Asset allocation using latest portfolio value.
SELECT i.asset_class,
       ROUND(SUM(h.units * p.price_inr), 2) AS total_value_inr,
       ROUND(100.0 * SUM(h.units * p.price_inr) /
             (SELECT SUM(h2.units * p2.price_inr)
              FROM holdings h2 JOIN prices p2 ON p2.instrument_id = h2.instrument_id
              WHERE p2.as_of_date = '2026-10-31'), 2) AS allocation_pct
FROM holdings h
JOIN instruments i ON i.instrument_id = h.instrument_id
JOIN prices p ON p.instrument_id = h.instrument_id
WHERE p.as_of_date = '2026-10-31'
GROUP BY i.asset_class ORDER BY total_value_inr DESC;

-- QUERY 3: Clients with a single position exceeding 50% of total holdings value.
WITH positions AS (
 SELECT h.client_id, i.instrument_name,
        h.units * p.price_inr AS market_value_inr
 FROM holdings h JOIN instruments i ON i.instrument_id = h.instrument_id
 JOIN prices p ON p.instrument_id = h.instrument_id
 WHERE p.as_of_date = '2026-10-31'
), ranked AS (
 SELECT client_id, instrument_name, market_value_inr,
        ROUND(100.0 * market_value_inr /
              SUM(market_value_inr) OVER (PARTITION BY client_id), 2) AS position_weight_pct
 FROM positions
)
SELECT * FROM ranked WHERE position_weight_pct > 50
ORDER BY position_weight_pct DESC;

-- QUERY 4: AUM by fictional client segment.
SELECT c.segment,
       COUNT(DISTINCT c.client_id) AS clients,
       ROUND(SUM(h.units * p.price_inr), 2) AS aum_inr
FROM clients c JOIN holdings h ON h.client_id = c.client_id
JOIN prices p ON p.instrument_id = h.instrument_id
WHERE p.as_of_date = '2026-10-31'
GROUP BY c.segment ORDER BY aum_inr DESC;
