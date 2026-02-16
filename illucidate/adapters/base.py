```python
"""
Base classes and data structures for Illucidate data adapters.

This module provides:
- DataFormat: Enum of supported formats
- GrowthCurveDataset: Container for growth curve data with metadata
- BaseLoader: Abstract base class for all data loaders
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union


class DataFormat:
    """Supported data formats."""
    MULTI_SHEET_EXCEL = "multi_sheet_excel"
    WIDE_CSV = "wide_csv"
    LONG_CSV = "long_csv"
    VICTOR_NIVO = "victor_nivo"
    CUSTOM = "custom"


class GrowthCurveDataset:
    """
    Container for growth curve data with metadata.
    
    Standard data structure for all loaders and analyzers.
    """
    
    def __init__(self, data: Dict[str, pd.DataFrame], metadata: Dict = None):
        self.data = data
        self.metadata = metadata or {}
        self.format_type = metadata.get('format_type', 'unknown')
        
    def get_sample_ids(self) -> List[str]:
        """Get all sample IDs."""
        return list(self.data.keys())
    
    def get_sample(self, sample_id: str) -> pd.DataFrame:
        """Get data for specific sample."""
        return self.data.get(sample_id)
    
    def get_conditions(self) -> List[str]:
        """Get unique experimental conditions."""
        return list(set(self.metadata.get('conditions', {}).values()))
    
    def get_samples_by_condition(self, condition: str) -> List[str]:
        """Get all samples matching a condition."""
        conditions = self.metadata.get('conditions', {})
        return [sid for sid, cond in conditions.items() if cond == condition]
    
    def to_wide_format(self, measurement='value') -> pd.DataFrame:
        """
        Convert to wide format for analysis.
        
        Returns DataFrame with time as index, samples as columns.
        """
        wide_data = {}
        for sample_id, df in self.data.items():
            if 'replicate' in df.columns:
                grouped = df.groupby('time')[measurement].mean()
                wide_data[sample_id] = grouped
            else:
                wide_data[sample_id] = df.set_index('time')[measurement]
        
        return pd.DataFrame(wide_data)
    
    def summary(self) -> str:
        """Generate dataset summary."""
        n_samples = len(self.data)
        conditions = self.get_conditions()
        
        first_sample = list(self.data.values())[0]
        time_range = (first_sample['time'].min(), first_sample['time'].max())
        n_timepoints = len(first_sample['time'].unique())
        
        if 'replicate' in first_sample.columns:
            n_replicates = first_sample['replicate'].nunique()
            rep_info = f"Replicates: {n_replicates} per sample"
        else:
            rep_info = "Replicates: Single measurement per timepoint"
        
        summary = f"""
Dataset Summary
===============
Source: {self.metadata.get('source', 'Unknown')}
Format: {self.format_type}
Samples: {n_samples}
Conditions: {len(conditions)} ({', '.join(conditions[:3])}{'...' if len(conditions) > 3 else ''})
Timepoints: {n_timepoints}
Time Range: {time_range[0]:.1f} - {time_range[1]:.1f} {self.metadata.get('time_unit', 'h')}
Measurement: {self.metadata.get('measurement_type', 'OD600')}
{rep_info}
"""
        return summary


class BaseLoader:
    """Abstract base class for data loaders."""
    
    def __init__(self, filepath: Union[str, Path]):
        self.filepath = Path(filepath)
        
    def load(self, **kwargs) -> GrowthCurveDataset:
        """Load data and return GrowthCurveDataset."""
        raise NotImplementedError("Subclasses must implement load()")
    
    def detect_format(self) -> bool:
        """Check if this loader can handle the file."""
        raise NotImplementedError("Subclasses must implement detect_format()")
```

---