import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# =====================================================================
# SYSTEM ABSOLUTE PATH SETUP
# =====================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

DB_PATH = os.path.join(PROJECT_ROOT, 'database', 'market_core.db')
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, 'outputs')

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# =====================================================================
# STEP 1: GENERATE SYNTHETIC ENTERPRISE RELATIONAL DATA
# =====================================================================
def generate_mock_data():
    """Generates synthetic normalized enterprise database tables."""
    print("⏳ Fabricating transactional data tables...")
    np.random.seed(42)
    
    # Create Customer Profile Vector
    num_customers = 500
    customer_ids = [f"CUST-{i:04d}" for i in range(1, num_customers + 1)]
    countries = ['United States', 'United Kingdom', 'Germany', 'Bangladesh', 'Canada']
    
    df_customers = pd.DataFrame({
        'CustomerID': customer_ids,
        'JoinDate': [datetime(2025, 1, 1) + timedelta(days=int(np.random.randint(0, 365))) for _ in range(num_customers)],
        'Country': np.random.choice(countries, size=num_customers, p=[0.4, 0.2, 0.15, 0.15, 0.1])
    })
    
    # Create Transaction Ledger Vector
    num_transactions = 4000
    tx_dates = [datetime(2025, 1, 1) + timedelta(days=int(np.random.randint(0, 540))) for _ in range(num_transactions)]
    
    df_transactions = pd.DataFrame({
        'TransactionID': [f"TX-{i:06d}" for i in range(1, num_transactions + 1)],
        'CustomerID': np.random.choice(customer_ids, size=num_transactions),
        'TransactionDate': tx_dates,
        'OrderValue': np.round(np.random.exponential(scale=75.0, size=num_transactions) + 10.0, 2)
    })
    
    return df_customers, df_transactions

# =====================================================================
# STEP 2: BUILD RELATIONAL DATABASE ENGINE
# =====================================================================
def build_relational_database(df_cust, df_tx):
    """Establishes an active SQL connection and writes normalized database schemas."""
    print(f"📦 Connecting to local database stream at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create Tables explicitly enforcing Primary, Foreign Keys and Referential Integrity
    cursor.execute("DROP TABLE IF EXISTS transactions;")
    cursor.execute("DROP TABLE IF EXISTS customers;")
    
    cursor.execute("""
        CREATE TABLE customers (
            CustomerID TEXT PRIMARY KEY,
            JoinDate TEXT,
            Country TEXT
        );
    """)
    
    cursor.execute("""
        CREATE TABLE transactions (
            TransactionID TEXT PRIMARY KEY,
            CustomerID TEXT,
            TransactionDate TEXT,
            OrderValue REAL,
            FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID)
        );
    """)
    
    # Cast timestamp vectors to strings for standard SQLite compatibility
    df_cust['JoinDate'] = df_cust['JoinDate'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df_tx['TransactionDate'] = df_tx['TransactionDate'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Write dataframe buffers into clean relational database tables
    df_cust.to_sql('customers', conn, if_exists='append', index=False)
    df_tx.to_sql('transactions', conn, if_exists='append', index=False)
    
    conn.commit()
    print("✅ Database tables created, constraints compiled, and transactions indexed.")
    return conn

# =====================================================================
# STEP 3: EXECUTE RFM STATISTICAL CUSTOMER SEGMENTATION
# =====================================================================
ddef execute_segmentation_pipeline(conn):
    """Executes a multi-join SQL query to perform RFM scoring and profiling."""
    print("🧮 Injecting raw pipeline SQL instructions to compute RFM distributions...")
    
    # Set the current baseline snapshot evaluation target date
    SNAPSHOT_DATE = "2026-07-01 00:00:00"
    
sql_query = f"""
    WITH RFM_Raw AS (
        SELECT 
            c.CustomerID,
            c.Country,
            ROUND(JULIANDAY('{SNAPSHOT_DATE}') - JULIANDAY(MAX(t.TransactionDate))) AS Recency,
            COUNT(t.TransactionID) AS Frequency,
            SUM(t.OrderValue) AS Monetary
        FROM customers c
        JOIN transactions t ON c.CustomerID = t.CustomerID
        GROUP BY c.CustomerID
    ),
    RFM_Scores AS (
        SELECT *,
            NTILE(5) OVER (ORDER BY Recency DESC) AS R_Score,
            NTILE(5) OVER (ORDER BY Frequency ASC) AS F_Score,
            NTILE(5) OVER (ORDER BY Monetary ASC) AS M_Score
        FROM RFM_Raw
    )
    SELECT *,
        (R_Score + F_Score + M_Score) AS Total_RFM_Value,
        CASE 
            WHEN R_Score >= 4 AND F_Score >= 4 AND M_Score >= 4 THEN 'Core VIP'
            WHEN R_Score <= 2 AND F_Score >= 3 THEN 'At Churn Risk'
            WHEN R_Score >= 4 AND F_Score <= 2 THEN 'New Leads'
            ELSE 'Regular Accounts'
        END AS Customer_Segment
    FROM RFM_Scores;
    """
    
df_rfm = pd.read_sql_query(sql_query, conn)
    
    # --- THE FIXED LINE: Ensure the data directory exists before writing ---
    TARGET_DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
    os.makedirs(TARGET_DATA_DIR, exist_ok=True)
    
    # Export calculated data matrix sheet
    output_csv_path = os.path.join(TARGET_DATA_DIR, 'customer_rfm_segments.csv')
    df_rfm.to_csv(output_csv_path, index=False)
    print(f"✅ Segmented customer metrics sheet exported safely to: {output_csv_path}")
    return df_rfm
# =====================================================================
# STEP 4: PRESENTATION VISUAL GRAPHICS
# =====================================================================
def export_analytics_graphics(df_rfm):
    """Generates high-resolution production charts visualizing customer segment values."""
    print("⏳ Rendering customer segments graphics panels...")
    sns.set_theme(style="whitegrid")
    
    # --- Chart 1: Visualizing Volume Distribution of Customer Cohorts ---
    plt.figure(figsize=(10, 6))
    order = df_rfm['Customer_Segment'].value_counts().index
    sns.countplot(data=df_rfm, y='Customer_Segment', order=order, palette='viridis')
    plt.title('Enterprise Distribution Portfolio Across Strategic Customer Segments', fontweight='bold', fontsize=14)
    plt.xlabel('Customer Account Volumes')
    plt.ylabel('Strategic Segment Categorization')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUTS_DIR, "customer_segment_distribution.png"), dpi=300)
    plt.close()

    # --- Chart 2: Scatter Plot of Recency vs. Monetary Metrics ---
    plt.figure(figsize=(12, 7))
    sns.scatterplot(
        data=df_rfm, x='Recency', y='Monetary', 
        hue='Customer_Segment', size='Frequency', 
        sizes=(20, 200), palette='Set1', alpha=0.8
    )
    plt.title('RFM Clustering Analysis: Recency Value vs Cumulative Monetary Values', fontweight='bold', fontsize=14)
    plt.xlabel('Recency Scale Interval (Days Since Last Order)')
    plt.ylabel('Lifetime Gross Monetary Contributions (USD)')
    plt.yscale('log') # Log scale accommodates outlier spending distributions smoothly
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Customer Cohorts')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUTS_DIR, "rfm_value_clusters.png"), dpi=300)
    plt.close()

# =====================================================================
# SYSTEM EXECUTION CONTROLLER
# =====================================================================
if __name__ == "__main__":
    df_cust, df_tx = generate_mock_data()
    db_connection = build_relational_database(df_cust, df_tx)
    rfm_segmented_df = execute_segmentation_pipeline(db_connection)
    export_analytics_graphics(rfm_segmented_df)
    db_connection.close()
    print("🎉 Relational E-Commerce SQL-RFM Pipeline completed successfully!")
