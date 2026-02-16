```python
"""
Excel file loaders for Illucidate.
"""

import pandas as pd
from typing import Dict, Union
from pathlib import Path

from .base import BaseLoader, GrowthCurveDataset, DataFormat


class MultiSheetExcelLoader(BaseLoader):
    """
    Loader for multi-sheet Excel files.
    
    Expected format:
        - Each sheet = one strain/sample
        - Column 1 = time values
        - Columns 2+ = replicates
    """
    
    def detect_format(self) -> bool:
        """Check if file is a multi-sheet Excel file."""
        if not self.filepath.suffix in ['.xlsx', '.xls']:
            return False
        
        try:
            xl = pd.ExcelFile(self.filepath)
            if len(xl.sheet_names) < 2:
                return False
            
            df = pd.read_excel(self.filepath, sheet_name=xl.sheet_names[0], nrows=5)
            return len(df.columns) >= 2
        except:
            return False
    
    def load(self, 
             time_col: str = None,
             condition_mapping: Dict[str, str] = None,
             measurement_type: str = 'OD600') -> GrowthCurveDataset:
        """
        Load multi-sheet Excel file.
        
        Args:
            time_col: Name of time column (auto-detected if None)
            condition_mapping: Map sheet names to experimental conditions
            measurement_type: What's being measured (e.g., 'OD600', 'CFU/ml')
        
        Returns:
            GrowthCurveDataset with all sheets loaded
        """
        xl = pd.ExcelFile(self.filepath)
        data = {}
        
        for sheet_name in xl.sheet_names:
            df_raw = pd.read_excel(self.filepath, sheet_name=sheet_name)
            
            # Auto-detect time column
            if time_col is None:
                time_candidates = [col for col in df_raw.columns if 'time' in str(col).lower()]
                time_col_actual = time_candidates[0] if time_candidates else df_raw.columns[0]
            else:
                time_col_actual = time_col
            
            time_values = df_raw[time_col_actual].values
            measurement_cols = [col for col in df_raw.columns if col != time_col_actual]
            
            # Convert to long format with replicates
            rows = []
            for i, time in enumerate(time_values):
                for rep_idx, col in enumerate(measurement_cols):
                    value = df_raw[col].iloc[i]
                    if pd.notna(value):
                        rows.append({
                            'time': time,
                            'value': value,
                            'replicate': rep_idx + 1
                        })
            
            df_formatted = pd.DataFrame(rows)
            data[sheet_name] = df_formatted
        
        metadata = {
            'source': str(self.filepath),
            'format_type': DataFormat.MULTI_SHEET_EXCEL,
            'measurement_type': measurement_type,
            'time_unit': 'h',
            'n_sheets': len(xl.sheet_names),
            'conditions': condition_mapping or {sheet: sheet for sheet in xl.sheet_names}
        }
        
        return GrowthCurveDataset(data, metadata)
```

---