#!/usr/bin/env python3
"""
Test script for Victor Nivo plate reader data.
Tests the VictorNivoListLoader with real plate reader exports.
"""

from pathlib import Path
from illucidate.adapters import load_data, VictorNivoListLoader
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def test_victor_nivo():
    """Test Victor Nivo loader with real data."""
    
    # File paths
    data_file = Path('/mnt/user-data/uploads/PBSouter_20260216_021203_list.xlsx')
    layout_file = Path('/mnt/user-data/uploads/96WellPlate2.xlsx')
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        return
    
    print("="*80)
    print("VICTOR NIVO PLATE READER DATA - TEST")
    print("="*80)
    
    # 1. Check what measurements are in the file
    print("\n1️⃣  Checking measurement types...")
    loader = VictorNivoListLoader(data_file)
    measurement_types = loader.get_measurement_types()
    print(f"   Found {len(measurement_types)} measurement types:")
    for mtype in measurement_types:
        print(f"   - {mtype}")
    
    # 2. Load data with auto-detection
    print("\n2️⃣  Loading data...")
    dataset = load_data(
        data_file,
        layout_file=layout_file,
        measurement_names={
            'LUM-Kinetics': 'Luminescence',
            'ABS (F)-Kinetics': 'OD600'
        }
    )
    
    print(dataset.summary())
    
    # 3. Examine loaded data structure
    print("\n3️⃣  Data structure:")
    sample_ids = dataset.get_sample_ids()
    print(f"   Total samples loaded: {len(sample_ids)}")
    print(f"   First 5 samples: {sample_ids[:5]}")
    
    # Check different measurement types
    lum_samples = [s for s in sample_ids if 'Luminescence' in s]
    od_samples = [s for s in sample_ids if 'OD600' in s]
    print(f"   Luminescence samples: {len(lum_samples)}")
    print(f"   OD600 samples: {len(od_samples)}")
    
    # 4. Check sample layout
    if 'layout' in dataset.metadata:
        print("\n4️⃣  Sample layout:")
        layout = dataset.metadata['layout']
        
        # Show PBS controls
        pbs_wells = [w for w, desc in layout.items() if 'PBS' in desc]
        print(f"   PBS control wells: {len(pbs_wells)}")
        print(f"   Example PBS wells: {pbs_wells[:5]}")
        
        # Show experimental wells
        exp_wells = [w for w, desc in layout.items() if 'PBS' not in desc and desc != 'Empty']
        print(f"   Experimental wells: {len(exp_wells)}")
        print(f"   Example conditions:")
        for well in exp_wells[:5]:
            print(f"     {well}: {layout[well][:60]}...")
    
    # 5. Plot some data
    print("\n5️⃣  Creating visualizations...")
    
    # Plot luminescence for first few wells
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Luminescence plot
    for i, sample_id in enumerate(lum_samples[:6]):
        sample_data = dataset.get_sample(sample_id)
        well_name = sample_id.split('_')[0]
        ax1.plot(sample_data['time'] / 3600, sample_data['value'],  # Convert to hours
                alpha=0.7, linewidth=1.5, label=well_name)
    
    ax1.set_xlabel('Time (hours)', fontsize=11)
    ax1.set_ylabel('Luminescence (RLU)', fontsize=11)
    ax1.set_title('Luminescence - First 6 Wells', fontsize=13, fontweight='bold')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # OD600 plot
    for i, sample_id in enumerate(od_samples[:6]):
        sample_data = dataset.get_sample(sample_id)
        well_name = sample_id.split('_')[0]
        ax2.plot(sample_data['time'] / 3600, sample_data['value'],  # Convert to hours
                alpha=0.7, linewidth=1.5, label=well_name)
    
    ax2.set_xlabel('Time (hours)', fontsize=11)
    ax2.set_ylabel('OD600', fontsize=11)
    ax2.set_title('OD600 - First 6 Wells', fontsize=13, fontweight='bold')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = Path('/mnt/user-data/outputs/victor_nivo_test.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"   ✓ Saved plot to {output_file}")
    
    # 6. Create summary table
    print("\n6️⃣  Creating summary table...")
    
    summary_data = []
    for sample_id in sample_ids[:20]:  # First 20 for demo
        sample_data = dataset.get_sample(sample_id)
        well_name = sample_id.split('_')[0]
        meas_type = sample_id.split('_')[1]
        
        summary_data.append({
            'Well': well_name,
            'Measurement': meas_type,
            'Timepoints': len(sample_data),
            'Min_value': sample_data['value'].min(),
            'Max_value': sample_data['value'].max(),
            'Mean_value': sample_data['value'].mean()
        })
    
    df_summary = pd.DataFrame(summary_data)
    print(df_summary.to_string(index=False))
    
    # Save summary
    df_summary_full = pd.DataFrame([
        {
            'Well': s.split('_')[0],
            'Measurement': s.split('_')[1],
            'Timepoints': len(dataset.get_sample(s)),
            'Min': dataset.get_sample(s)['value'].min(),
            'Max': dataset.get_sample(s)['value'].max(),
            'Mean': dataset.get_sample(s)['value'].mean()
        }
        for s in sample_ids
    ])
    
    summary_file = Path('/mnt/user-data/outputs/victor_nivo_summary.csv')
    df_summary_full.to_csv(summary_file, index=False)
    print(f"\n   ✓ Saved full summary to {summary_file}")
    
    print("\n" + "="*80)
    print("✅ VICTOR NIVO TEST COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("  - Data is loaded and ready for analysis")
    print("  - Use dataset.to_wide_format() for specific measurement")
    print("  - Or access individual wells via dataset.get_sample()")
    print()


if __name__ == '__main__':
    test_victor_nivo()
