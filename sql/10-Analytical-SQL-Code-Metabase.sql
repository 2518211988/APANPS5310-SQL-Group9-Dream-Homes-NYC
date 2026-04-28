--- Section 1 - Executive Summary:

-- Net Profit By Office
SELECT 
	o.office_name,
	transactions.transaction_type,
	COALESCE(SUM(transactions.commission), 0) AS total_revenue,
	COALESCE(SUM(oe.amount), 0) AS total_expenses,
	COALESCE(SUM(transactions.commission), 0) - COALESCE(SUM(oe.amount), 0) AS net_profit,
	(
  	(COALESCE(SUM(transactions.commission), 0) - COALESCE(SUM(oe.amount), 0)) / 
  	NULLIF(SUM(transactions.commission), 0) * 100
	) AS profit_margin
FROM offices o
LEFT JOIN employees e 
	USING (officeid)
LEFT JOIN transactions 
	USING (emplid)
LEFT JOIN office_expenses oe
	USING (officeid)
	WHERE 1=1
[[AND transactions.transaction_type = {{transaction_type}}]]
GROUP BY 
	o.office_name,
	transactions.transaction_type
ORDER BY
	profit_margin DESC;

-- Number of Transactions by Month
SELECT
	DATE_TRUNC('month', transaction_date) AS month,
	transaction_type,
	COUNT(*) AS deals
FROM transactions
GROUP BY	
	DATE_TRUNC('month', transaction_date),
	transaction_type
ORDER BY
	month;

-- Transactions by Property Type
SELECT 
	o.office_name,
	pt.name,
	t.transaction_type,
	COUNT(t.transactionid) AS number_of_transactions
FROM offices o
JOIN employees e ON o.officeid = e.officeid
JOIN transactions t ON e.emplid = t.emplid
JOIN listings l ON t.listingid = l.listingid
JOIN properties p ON l.unitid = p.unitid
JOIN property_type pt ON p.propertytypeid = pt.propertytypeid
GROUP BY
	o.office_name,
	pt.name,
	t.transaction_type;

--- Section 2 - Office Analytics:

-- Agent Licenses Expiring By Office
SELECT 
    o.office_name,
    COUNT(al.licenseid) AS expiring_licenses
FROM offices o
JOIN employees e ON o.officeid = e.officeid
JOIN agent_licenses al ON e.emplid = al.emplid
WHERE al.expdate >= CURRENT_DATE 
  [[ AND al.expdate <= CURRENT_DATE + (INTERVAL '1 month' * {{months_to_expire}}) ]]
GROUP BY 
    o.office_name
ORDER BY 
    expiring_licenses DESC;

-- Agent Performance By Office
SELECT
    o.office_name,
    SUM(transactions.commission) AS total_commission,
    {{office_goal}} AS goal
FROM transactions 
JOIN employees e ON transactions.emplid = e.emplid
JOIN offices o ON e.officeid = o.officeid
WHERE 1=1
  [[AND {{date_range}}]]
  [[AND o.office_name = {{office_name}}]]
GROUP BY o.office_name
ORDER BY total_commission DESC;

--- Section 3 - Operational Analytics:

-- Neighborhood Demand Intelligence
SELECT 
    n.neighborhood,
    n.zip_code,
    COUNT(t.transactionid) AS transaction_volume,
    ROUND(AVG(t.amount), 2) AS avg_transaction_value,
    SUM(t.amount) AS total_market_value
FROM transactions t
JOIN listings l USING (listingid)
JOIN properties p USING (unitid)
JOIN neighborhood n USING (zip_code)
WHERE t.transaction_type = 'sale'
GROUP BY n.neighborhood, n.zip_code
ORDER BY avg_transaction_value DESC;

-- Listing Health
SELECT 
    l.listingid,
    p.street,
    MIN(a.date) AS estimated_list_date,
    COALESCE(t.transaction_date, CURRENT_DATE) AS end_date,
    GREATEST(COALESCE(t.transaction_date, CURRENT_DATE) - MIN(a.date),0) AS days_on_market
FROM listings l
JOIN properties p ON l.unitid = p.unitid
LEFT JOIN appointments a ON l.listingid = a.listingid
LEFT JOIN transactions t ON l.listingid = t.listingid AND t.transaction_type = 'sale'
GROUP BY l.listingid, p.street, t.transaction_date
HAVING MIN(a.date) IS NOT NULL
	AND GREATEST(COALESCE(t.transaction_date, CURRENT_DATE) - MIN(a.date),0) > 0
ORDER BY days_on_market DESC;

-- Client Preference Matching
SELECT 
    cr.clientid,
    n.neighborhood AS preferred_neighborhood,
    pt.name AS preferred_property_type,
    COUNT(l.listingid) AS matching_listings,
    COALESCE(MIN(l.price), 0) AS starting_at_price
FROM client_requirements cr
JOIN neighborhood n 
    ON cr.zip_code = n.zip_code
JOIN property_type pt 
    ON cr.propertytypeid = pt.propertytypeid
LEFT JOIN properties p 
    ON n.zip_code = p.zip_code 
    AND cr.propertytypeid = p.propertytypeid
LEFT JOIN listings l 
    ON p.unitid = l.unitid
WHERE 1=1
[[AND cr.clientid = {{clientid_filter}}:: integer]]
GROUP BY 
    cr.clientid, 
    n.neighborhood, 
    pt.name
ORDER BY 
    matching_listings ASC;

-- Appointment Effectiveness
WITH agent_appointments AS (
    SELECT 
        emplid, 
        COUNT(appointmentid) AS total_appointments,
        COUNT(DISTINCT listingid) AS unique_listings_shown
    FROM appointments
    GROUP BY emplid
),
agent_sales AS (
    SELECT 
        emplid, 
        COUNT(transactionid) AS closed_deals,
        SUM(amount) AS total_sales_volume
    FROM transactions
    WHERE transaction_type = 'sale'
    GROUP BY emplid
)
SELECT 
    e.firstname || ' ' || e.lastname AS agent,
    aa.total_appointments,
    COALESCE(asales.closed_deals, 0) AS closed_deals
FROM employees e
JOIN agent_appointments aa USING (emplid)
LEFT JOIN agent_sales asales USING (emplid);

-- Open House Effectiveness
SELECT 
    l.listingid,
    p.street,
    COUNT(oh.openhouseid) AS open_houses_held,
    t.amount AS final_sale_price,
    l.price,
    GREATEST(0,(t.amount - l.price)) AS price_premium
FROM listings l
JOIN properties p USING (unitid)
LEFT JOIN open_houses oh USING (listingid)
JOIN transactions t USING (listingid)
WHERE t.transaction_type = 'sale'
GROUP BY l.listingid, p.street, t.amount, l.price
ORDER BY open_houses_held DESC;

