```python
"""
Interactive helper for diagnosing and loading unknown data formats.
"""

import pandas as pd
from pathlib import Path
from typing import Union


class InteractiveDataHelper:
    """
    Diagnose data files and help users load them.
    """
    
    def __init__(self):
        pass
    
    def diagnose_file(self, filepath: Union[str, Path]) -> str:
        """Examine file structure and suggest loading approach."""
        filepath = Path(filepath)
        
        if not filepath.exists():
            return f"❌ File not found: {filepath}"
        
        report = [f"\n📊 Analyzing: {filepath.name}\n{'='*60}"]
        
        if filepath.suffix in ['.xlsx', '.xls']:
            return self._diagnose_excel(filepath, report)
        elif filepath.suffix == '.csv':
            return self._diagnose_csv(filepath, report)
        else:
            report.append(f"❓ Unknown file type: {filepath.suffix}")
            report.append("\nSupported formats:")
            report.append("  - .xlsx, .xls (Excel)")
            report.append("  - .csv (CSV)")
            return "\n".join(report)
    
    def _diagnose_excel(self, filepath: Path, report: list) -> str:
        """Diagnose Excel file structure."""
        xl = pd.ExcelFile(filepath)
        n_sheets = len(xl.sheet_names)
        
        report.append(f"📁 Excel file with {n_sheets} sheet(s)")
        report.append(f"   Sheets: {', '.join(xl.sheet_names[:5])}" + 
                     ("..." if n_sheets > 5 else ""))
        
        df = pd.read_excel(filepath, sheet_name=xl.sheet_names[0], nrows=10)
        report.append(f"\n📋 First sheet structure ({xl.sheet_names[0]}):")
        report.append(f"   Rows: {len(df)} (showing first 10)")
        report.append(f"   Columns: {len(df.columns)}")
        report.append(f"   Column names: {list(df.columns)}")
        
        report.append("\n🔍 Data preview:")
        report.append(df.head(3).to_string(index=False))
        
        report.append("\n💡 Suggested approach:")
        
        if n_sheets > 1:
            report.append("   This looks like MULTI_SHEET_EXCEL format")
            report.append("   (each sheet = one sample/strain)\n")
            report.append("   Try this code:")
            report.append("   " + "-"*50)
            report.append("   from illucidate.adapters import load_data")
            report.append(f"   dataset = load_data('{filepath}')")
            report.append("   print(dataset.summary())")
            report.append("   wide_df = dataset.to_wide_format()")
        else:
            report.append("   Single sheet Excel file")
            report.append("   Check if this is wide or long format\n")
            report.append("   For WIDE format (time=rows, samples=columns):")
            report.append("   " + "-"*50)
            report.append("   import pandas as pd")
            report.append(f"   df = pd.read_excel('{filepath}')")
            report.append("   # Use df directly with EarlyDetectionAnalyzer")
        
        return "\n".join(report)
    
    def _diagnose_csv(self, filepath: Path, report: list) -> str:
        """Diagnose CSV file structure."""
        try:
            df = pd.read_csv(filepath, nrows=10)
            report.append(f"📁 CSV file")
            report.append(f"   Rows: {len(df)} (showing first 10)")
            report.append(f"   Columns: {len(df.columns)}")
            report.append(f"   Column names: {list(df.columns)}")
            
            report.append("\n🔍 Data preview:")
            report.append(df.head(3).to_string(index=False))
            
            report.append("\n💡 Format detection:")
            
            has_sample_col = any('sample' in str(col).lower() or 'strain' in str(col).lower() 
                                for col in df.columns)
            has_time_col = any('time' in str(col).lower() for col in df.columns)
            has_value_col = any('value' in str(col).lower() or 'od' in str(col).lower() 
                               for col in df.columns)
            
            if has_sample_col and has_time_col and has_value_col:
                report.append("   Looks like LONG format (each row = one measurement)")
                report.append("\n   TODO: Implement LongCsvLoader")
            else:
                report.append("   Looks like WIDE format (time=rows, samples=columns)")
                report.append("\n   Try this code:")
                report.append("   " + "-"*50)
                report.append("   import pandas as pd")
                report.append(f"   df = pd.read_csv('{filepath}', index_col=0)")
                report.append("   # Use df directly with EarlyDetectionAnalyzer")
            
        except Exception as e:
            report.append(f"❌ Error reading CSV: {e}")
        
        return "\n".join(report)
```

---