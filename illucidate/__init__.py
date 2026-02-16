```python
"""
Illucidate - AI-powered early detection for bacterial strain classification.

Quick Start:
    >>> from illucidate import load_data, EarlyDetectionAnalyzer
    >>> dataset = load_data('growth_curves.xlsx')
    >>> wide_df = dataset.to_wide_format()
    >>> analyzer = EarlyDetectionAnalyzer(wide_df)
"""

__version__ = '0.1.0'

from .adapters import load_data, GrowthCurveDataset
from .core import EarlyDetectionAnalyzer

__all__ = ['load_data', 'GrowthCurveDataset', 'EarlyDetectionAnalyzer']
```

---