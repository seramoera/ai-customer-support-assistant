#!/usr/bin/env python
"""Quick test of CLINC150 dataset loading"""

import logging
from src.data_pipeline import Dataset

logging.basicConfig(level=logging.INFO)

print("Testing CLINC150 dataset loading...")
print("=" * 60)

try:
    dataset = Dataset()
    df = dataset.load_data()
    
    print(f"\n✓ Successfully loaded {len(df)} samples")
    print(f"✓ Intents ({len(df['intent'].unique())}): {df['intent'].unique().tolist()}")
    print(f"\nSample queries:")
    for intent in df['intent'].unique()[:3]:
        sample = df[df['intent'] == intent].iloc[0]['text']
        print(f"  • {intent}: {sample}")
    
    print("\n✓ CLINC150 dataset loaded successfully!")
    
except Exception as e:
    print(f"\n✗ Error loading dataset: {e}")
    import traceback
    traceback.print_exc()
