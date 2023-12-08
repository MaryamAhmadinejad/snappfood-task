WITH vendor_requests_per_month AS (
    SELECT DATE_FORMAT(created_at,'%Y-%m') AS created_date, COUNT(id) AS sum_requests
		FROM vendorinformation
		GROUP BY created_date
),
contracts_per_month AS (
    SELECT DATE_FORMAT(created_at,'%Y-%m') AS created_date, COUNT(id) AS sum_contracts
		FROM contract
		GROUP BY created_date
)

SELECT contracts_per_month.created_date,
(contracts_per_month.sum_contracts/vendor_requests_per_month.sum_requests)*100 AS percent
FROM contracts_per_month
INNER JOIN vendor_requests_per_month
ON vendor_requests_per_month.created_date = contracts_per_month.created_date
ORDER BY created_date;
