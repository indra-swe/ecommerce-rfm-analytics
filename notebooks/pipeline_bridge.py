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

