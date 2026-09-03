#!/usr/bin/env python3
"""Profile cardinality of IEEE-CIS dataset features"""
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
    
    # Calculate cardinality for each feature
    cardinality_data = []
    for col in merged.columns:
        dtype = str(merged[col].dtype)
        unique_count = merged[col].nunique()
        total_count = len(merged)
        unique_ratio = unique_count / total_count if total_count > 0 else 0
        
        # Classify based on cardinality
        if unique_ratio < 0.01:
            category = 'RARE'
        elif unique_ratio < 0.05:
            category = 'LOW_CARDINALITY'
        elif unique_ratio < 0.2:
            category = 'MEDIUM_CARDINALITY'
        else:
            category = 'HIGH_CARDINALITY'
        
        cardinality_data.append({
            'feature': col,
            'dtype': dtype,
            'unique_count': unique_count,
            'unique_ratio': unique_ratio,
            'category': category
        })
    
    # Create cardinality dataframe
    cardinality_df = pd.DataFrame(cardinality_data)
    
    # Sort by unique ratio descending
    cardinality_df = cardinality_df.sort_values('unique_ratio', ascending=False)
    
    # Ensure reports directory exists
    os.makedirs('ml/reports', exist_ok=True)
    
    # Save cardinality CSV
    cardinality_df.to_csv('ml/reports/cardinality.csv', index=False)
    print(f"Saved cardinality data: {len(cardinality_df)} features")

if __name__ == '__main__':
    main()
