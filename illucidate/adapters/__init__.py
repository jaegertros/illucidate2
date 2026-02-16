```python
"""
Illucidate Data Adapters - Universal data loading for growth curve analysis.
"""

from pathlib import Path
from typing import Union

from .base import BaseLoader, GrowthCurveDataset, DataFormat
from .excel import MultiSheetExcelLoader
from .interactive import InteractiveDataHelper


# List of all available loaders (in priority order)
LOADERS = [
    MultiSheetExcelLoader,
]


def load_data(filepath: Union[str, Path], **kwargs) -> GrowthCurveDataset:
    """
    Universal data loading function.
    
    Automatically detects file format and loads data.
    
    Args:
        filepath: Path to data file
        **kwargs: Loader-specific parameters
    
    Returns:
        GrowthCurveDataset ready for analysis
    
    Example:
        >>> from illucidate.adapters import load_data
        >>> dataset = load_data('growth_curves.xlsx')
        >>> wide_df = dataset.to_wide_format()
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Try each loader
    for loader_class in LOADERS:
        loader = loader_class(filepath)
        if loader.detect_format():
            print(f"✓ Detected format: {loader_class.__name__}")
            return loader.load(**kwargs)
    
    # No loader found - use interactive helper
    print("❓ Unknown format - running diagnostic...\n")
    helper = InteractiveDataHelper()
    diagnosis = helper.diagnose_file(filepath)
    print(diagnosis)
    
    raise ValueError(
        f"Could not auto-detect format for {filepath}. "
        "See diagnostic output above for suggestions."
    )


__all__ = [
    'load_data',
    'GrowthCurveDataset',
    'BaseLoader',
    'DataFormat',
    'MultiSheetExcelLoader',
    'InteractiveDataHelper',
]
```

---