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

