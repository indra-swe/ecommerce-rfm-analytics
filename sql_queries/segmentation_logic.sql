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
-- STEP 2: Apply SQL Window functions to segment metrics into equal performance quintiles
RFM_Scores AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY Recency DESC) AS R_Score,  -- Low recency numbers indicate highly active accounts
        NTILE(5) OVER (ORDER BY Frequency ASC) AS F_Score, -- High counts equal top loyalty tier
        NTILE(5) OVER (ORDER BY Monetary ASC) AS M_Score   -- High revenue equals premium tier
    FROM RFM_Raw
)
-- STEP 3: Assign strategic groupings based on calculated window score balances
SELECT *,
    (R_Score + F_Score + M_Score) AS Total_RFM_Value,
    CASE 
        WHEN R_Score >= 4 AND F_Score >= 4 AND M_Score >= 4 THEN 'Core VIP'
        WHEN R_Score <= 2 AND F_Score >= 3 THEN 'At Churn Risk'
        WHEN R_Score >= 4 AND F_Score <= 2 THEN 'New Leads'
        ELSE 'Regular Accounts'
    END AS Customer_Segment
FROM RFM_Scores
ORDER BY Total_RFM_Value DESC;
