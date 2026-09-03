#!/usr/bin/env python3
"""Profile missingness in IEEE-CIS dataset"""
import pandas as pd
import json
import os
from pathlib import Path

def main():
    # Load data
    train_tx = pd.read_csv('data/ieee_cis/train_transaction.csv')
    train_id = pd.read_csv('data/ieee_cis/train_identity.csv')
    
    # Merge on TransactionID
    merged = pd.merge(train_tx, train_id, on='TransactionID', how='left')
    
    # Calculate missingness
    missing_counts = merged.isnull().sum()
    missing_pct = (missing_counts / len(merged)) * 100
    
    # Create missingness dataframe
    missing_df = pd.DataFrame({
        'feature': missing_counts.index,
        'missing_count': missing_counts.values,
        'missing_percentage': missing_pct.values
    })
    
    # Sort by missing percentage descending
    missing_df = missing_df.sort_values('missing_percentage', ascending=False)
    
    # Ensure reports directory exists
    os.makedirs('ml/reports', exist_ok=True)
    
    # Save missingness CSV
    missing_df.to_csv('ml/reports/missingness.csv', index=False)
    print(f"Saved missingness data: {len(missing_df)} features")

if __name__ == '__main__':
    main()
