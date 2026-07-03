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

