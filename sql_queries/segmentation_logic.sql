-- STEP 1: Compute raw metrics by processing transaction records
WITH RFM_Raw AS (
    SELECT 
        c.CustomerID,
        c.Country,
        -- Calculate date intervals by subtracting transaction dates from snapshot date
        ROUND(JULIANDAY('2026-07-01 00:00:00') - JULIANDAY(MAX(t.TransactionDate))) AS Recency,
        COUNT(t.TransactionID) AS Frequency,
        SUM(t.OrderValue) AS Monetary
    FROM customers c
    JOIN transactions t ON c.CustomerID = t.CustomerID
    GROUP BY c.CustomerID
),
