```python
#!/usr/bin/env python3
"""
Test script for E. coli reduced genome dataset.
Run from project root: python scripts/test_ecoli.py
"""

from pathlib import Path
from illucidate.adapters import load_data
from illucidate.core import EarlyDetectionAnalyzer
import pandas as pd
import matplotlib.pyplot as plt


def test_ecoli_dataset():
    """Load and analyze E. coli reduced genome dataset."""
    
    # File path
    data_file = Path.home() / 'KHKgrowthcurves_LB.xlsx'
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        print("Please download from:")
        print("https://springernature.figshare.com/articles/dataset/Growth_data_of_the_E_coli_strains_carrying_the_reduced_genomes/5918608")
        return
    
    print("="*70)
    print("ILLUCIDATE - E. coli Reduced Genome Analysis")
    print("="*70)
    
    # 1. Load data
    print("\n1️⃣  Loading data...")
    dataset = load_data(data_file, measurement_type='OD600')
    print(dataset.summary())
    
    # 2. Convert to wide format
    print("\n2️⃣  Converting to wide format...")
    wide_df = dataset.to_wide_format()
    print(f"   Shape: {wide_df.shape[0]} timepoints × {wide_df.shape[1]} samples")
    
    # 3. Create sample labels
    print("\n3️⃣  Creating sample groups...")
    sample_ids = dataset.get_sample_ids()
    n_samples = len(sample_ids)
    samples_per_group = n_samples // 4
    
    sample_labels = {}
    for i, sample_id in enumerate(sample_ids):
        if i < samples_per_group:
            sample_labels[sample_id] = 'Group_A'
        elif i < 2 * samples_per_group:
            sample_labels[sample_id] = 'Group_B'
        elif i < 3 * samples_per_group:
            sample_labels[sample_id] = 'Group_C'
        else:
            sample_labels[sample_id] = 'Group_D'
    
    print(f"   Created {len(set(sample_labels.values()))} groups")
    
    # 4. Initialize analyzer
    print("\n4️⃣  Initializing analyzer...")
    analyzer = EarlyDetectionAnalyzer(wide_df, sample_labels)
    print("   ✓ Analyzer ready")
    
    # 5. Visualization
    print("\n5️⃣  Creating visualization...")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, sample_id in enumerate(sample_ids[:6]):
        sample_data = dataset.get_sample(sample_id)
        for rep in sample_data['replicate'].unique():
            rep_data = sample_data[sample_data['replicate'] == rep]
            alpha = 0.3 if rep > 1 else 1.0
            linewidth = 2 if rep == 1 else 1
            ax.plot(rep_data['time'], rep_data['value'], 
                   alpha=alpha, linewidth=linewidth,
                   label=f"{sample_id}" if rep == 1 else "")
    
    ax.set_xlabel('Time (h)', fontsize=12)
    ax.set_ylabel('OD600', fontsize=12)
    ax.set_title('E. coli Growth Curves - LB Medium', fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    
    output_file = Path('/mnt/user-data/outputs/ecoli_test_preview.png')
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"   ✓ Saved to {output_file}")
    
    # 6. Save processed data
    print("\n6️⃣  Saving processed data...")
    wide_df.to_csv('/mnt/user-data/outputs/ecoli_LB_wide_format.csv')
    pd.DataFrame({'sample_id': list(sample_labels.keys()), 
                  'group': list(sample_labels.values())}).to_csv(
        '/mnt/user-data/outputs/ecoli_LB_labels.csv', index=False)
    print("   ✓ Saved wide format and labels")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)


if __name__ == '__main__':
    test_ecoli_dataset()
```

---