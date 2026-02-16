"""
Victor Nivo plate reader adapter for list-format exports.

Handles multi-measurement files where each file contains:
- Multiple measurement types (LUM-Kinetics, ABS-Kinetics, etc.)
- 96-well plate data for each measurement type
- Time-series kinetic measurements
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Union, List, Tuple
import re

from .base import BaseLoader, GrowthCurveDataset, DataFormat


class VictorNivoListLoader(BaseLoader):
    """
    Loader for Victor Nivo plate reader data in "list" export format.
    
    Expected format:
        - Excel file with "Well results" sheet
        - Multiple measurement sections (e.g., LUM-Kinetics, ABS-Kinetics)
        - Each section has header row with times, then 96 rows (A1-H12)
        - Optional plate layout file with sample descriptions
    
    Example:
        Row 10: LUM-Kinetics
        Row 17: [Well, Time(s), 0.0, 357.2, 711.2, ...]
        Row 18: [A1, , 112, 105, 108, ...]
        Row 19: [A2, , 81, 102, 101, ...]
        ...
        Row 113: [H12, , 95, 98, 102, ...]
        Row 115: ABS (F)-Kinetics
        Row 122: [Well, Time(s), 0.0, 357.2, ...]
        Row 123: [A1, , 0.045, 0.052, ...]
    """
    
    def detect_format(self) -> bool:
        """Check if file is a Victor Nivo list export."""
        if not self.filepath.suffix in ['.xlsx', '.xls']:
            return False
        
        try:
            # Check for "Well results" sheet
            xl = pd.ExcelFile(self.filepath)
            if 'Well results' not in xl.sheet_names:
                return False
            
            # Check for characteristic structure
            df = pd.read_excel(self.filepath, sheet_name='Well results', 
                             header=None, nrows=20)
            
            # Look for "Kinetics" in column B (typical for Victor Nivo)
            col_b = df.iloc[:, 1].astype(str)
            has_kinetics = any('Kinetics' in str(val) for val in col_b)
            
            return has_kinetics
        except:
            return False
    
    def load(self, 
             layout_file: Union[str, Path] = None,
             measurement_names: Dict[str, str] = None) -> GrowthCurveDataset:
        """
        Load Victor Nivo list-format file.
        
        Args:
            layout_file: Optional plate layout file with sample descriptions
            measurement_names: Optional mapping to rename measurements
                              e.g., {'LUM-Kinetics': 'Luminescence', 
                                     'ABS (F)-Kinetics': 'OD600'}
        
        Returns:
            GrowthCurveDataset with all measurements
        """
        # Load full sheet
        df_full = pd.read_excel(self.filepath, sheet_name='Well results', header=None)
        
        # Find all measurement sections
        sections = self._find_measurement_sections(df_full)
        
        if not sections:
            raise ValueError("No measurement sections found in file")
        
        # Parse each section
        all_data = {}
        metadata = {
            'source': str(self.filepath),
            'format_type': DataFormat.VICTOR_NIVO,
            'measurement_types': {},
            'conditions': {}
        }
        
        for section in sections:
            meas_type = section['measurement_type']
            meas_data = self._parse_measurement_section(
                df_full, section['data_start_row'], section['time_row']
            )
            
            # Rename measurement if mapping provided
            if measurement_names and meas_type in measurement_names:
                meas_type = measurement_names[meas_type]
            
            # Store each well's data
            for well, time_series in meas_data.items():
                # Create unique key: well_measurement
                key = f"{well}_{meas_type}"
                
                # Convert to DataFrame format
                df_well = pd.DataFrame({
                    'time': time_series['time'],
                    'value': time_series['values'],
                    'replicate': 1  # Single measurement per well
                })
                
                all_data[key] = df_well
                metadata['measurement_types'][key] = meas_type
        
        # Load plate layout if provided
        if layout_file:
            layout = self._load_plate_layout(layout_file)
            metadata['layout'] = layout
            
            # Create condition labels
            for well in self._get_all_wells():
                if well in layout:
                    metadata['conditions'][well] = layout[well]
        
        metadata['time_unit'] = 's'  # Victor Nivo exports in seconds
        
        return GrowthCurveDataset(all_data, metadata)
    
    def _find_measurement_sections(self, df: pd.DataFrame) -> List[Dict]:
        """
        Find all measurement sections in the file.
        
        Returns list of dicts with:
            - measurement_type: Name of measurement (e.g., 'LUM-Kinetics')
            - type_row: Row where measurement type is declared
            - time_row: Row with time values
            - data_start_row: First row of well data
        """
        sections = []
        
        for i in range(len(df)):
            cell_b = df.iloc[i, 1]
            
            # Look for measurement type (e.g., "LUM-Kinetics")
            if pd.notna(cell_b) and isinstance(cell_b, str) and 'Kinetics' in cell_b:
                # Found a measurement section
                measurement_type = cell_b.strip()
                
                # Find the corresponding data header
                for j in range(i, min(i + 15, len(df))):
                    if df.iloc[j, 0] == 'Well':
                        time_row = j
                        data_start_row = j + 1
                        
                        sections.append({
                            'measurement_type': measurement_type,
                            'type_row': i,
                            'time_row': time_row,
                            'data_start_row': data_start_row
                        })
                        break
        
        return sections
    
    def _parse_measurement_section(self, df: pd.DataFrame, 
                                   data_start_row: int, 
                                   time_row: int) -> Dict[str, Dict]:
        """
        Parse a single measurement section (96 wells).
        
        Returns dict of {well_name: {'time': array, 'values': array}}
        """
        # Extract time values (row with "Time(s)")
        time_values = df.iloc[time_row, 2:].values
        time_values = np.array([t for t in time_values if pd.notna(t)])
        
        # Extract data for each well (96 rows: A1 through H12)
        well_data = {}
        
        for i in range(96):  # Exactly 96 wells
            row_idx = data_start_row + i
            if row_idx >= len(df):
                break
            
            well_name = df.iloc[row_idx, 0]
            if pd.isna(well_name):
                break
            
            # Extract values (starting from column 2)
            values = df.iloc[row_idx, 2:].values
            values = np.array([v for v in values if pd.notna(v)])
            
            # Ensure time and values have same length
            min_length = min(len(time_values), len(values))
            
            well_data[str(well_name)] = {
                'time': time_values[:min_length],
                'values': values[:min_length]
            }
        
        return well_data
    
    def _load_plate_layout(self, layout_file: Union[str, Path]) -> Dict[str, str]:
        """
        Load plate layout file and parse sample descriptions.
        
        Expected format: 8 rows (A-H) × 12 columns (1-12)
        Sample descriptions may contain semicolons as delimiters.
        
        Returns dict of {well_name: description}
        """
        layout_path = Path(layout_file)
        
        if not layout_path.exists():
            raise FileNotFoundError(f"Layout file not found: {layout_path}")
        
        # Load layout file
        df_layout = pd.read_excel(layout_path, sheet_name=0, header=None)
        
        # Parse into well names
        layout = {}
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        
        for row_idx, row_label in enumerate(rows):
            for col_idx in range(1, 13):  # Columns 1-12
                well_name = f"{row_label}{col_idx}"
                
                # Get cell value (account for 0-indexing)
                try:
                    cell_value = df_layout.iloc[row_idx, col_idx]
                    
                    if pd.notna(cell_value):
                        # Clean up the description
                        description = str(cell_value).strip()
                        
                        # Parse semicolon-delimited components
                        components = [c.strip() for c in description.split(';')]
                        layout[well_name] = '; '.join(components)
                    else:
                        layout[well_name] = 'Empty'
                except:
                    layout[well_name] = 'Unknown'
        
        return layout
    
    def _get_all_wells(self) -> List[str]:
        """Generate list of all 96 well names."""
        wells = []
        for row in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            for col in range(1, 13):
                wells.append(f"{row}{col}")
        return wells
    
    def get_measurement_types(self, filepath: Union[str, Path] = None) -> List[str]:
        """
        Get list of measurement types in the file without loading full data.
        
        Args:
            filepath: Optional path to file (uses self.filepath if not provided)
        
        Returns:
            List of measurement type names
        """
        path = Path(filepath) if filepath else self.filepath
        df_full = pd.read_excel(path, sheet_name='Well results', header=None)
        
        sections = self._find_measurement_sections(df_full)
        return [s['measurement_type'] for s in sections]
