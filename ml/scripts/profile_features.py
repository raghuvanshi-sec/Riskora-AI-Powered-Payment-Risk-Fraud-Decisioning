#!/usr/bin/env python3
"""Create feature inventory for IEEE-CIS dataset"""
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
    
    # Feature inventory data
    inventory_data = []
    for col in merged.columns:
        dtype = str(merged[col].dtype)
        unique_count = merged[col].nunique()
        total_count = len(merged)
        missing_pct = (merged[col].isnull().sum() / total_count) * 100
        
        # Classify feature type
        if col == 'TransactionID':
            dtype_category = 'identifier'
        elif col == 'isFraud':
            dtype_category = 'target'
        elif col in ['TransactionDT', 'TransactionAmt']:
            dtype_category = 'temporal'
        elif dtype in ['int64', 'float64']:
            if unique_count <= 2:
                dtype_category = 'binary'
            else:
                dtype_category = 'numeric'
        elif dtype == 'object':
            if unique_count <= 10:
                dtype_category = 'categorical'
            else:
                dtype_category = 'high_cardinality_categorical'
        else:
            dtype_category = 'unknown'
        
        inventory_data.append({
            'feature': col,
            'dtype': dtype,
            'unique_count': unique_count,
            'missing_percentage': missing_pct,
            'dtype_category': dtype_category
        })
    
    # Create inventory dataframe
    inventory_df = pd.DataFrame(inventory_data)
    
    # Ensure reports directory exists
    os.makedirs('ml/reports', exist_ok=True)
    
    # Save feature inventory CSV
    inventory_df.to_csv('ml/reports/feature_inventory.csv', index=False)
    print(f"Saved feature inventory: {len(inventory_df)} features")

if __name__ == '__main__':
    main()
