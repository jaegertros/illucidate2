<p align="center">
  <img src="assets/illucidate_logo.svg" alt="Illucidate Logo" width="400"/>
</p>

# Illucidate 💡

**Illuminating early signals in bacterial detection**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> *Illucidate* = **Illuminate** + **Elucidate**  
> Because bacterial detection should be both *bright* and *clear*.

---

## What is Illucidate?

Illucidate is an open-source toolkit for discovering **multivariate, time-structured patterns** in bacterial detection assays that enable earlier, more reliable pathogen identification.

---

## Why I Built This

Most of my work has been on early detection of foodborne pathogens using bioluminescent reporter phages—specifically *E. coli* O157:H7 with engineered phages ΦV10::NanoLuc and ΦV10::lux. 

**The frustration:** We collect *so much data* during these assays (OD at multiple wavelengths, bioluminescence, temperature, timing), but traditional analysis looks at each measurement in isolation. Testing protocols split samples into separate pathways, each running a different confirmation test, hoping to detect the pathogen in *one* of them.

**The realization:** What if we're already collecting the signals we need? What if the **combination** of measurements—the ratios, the timing differences, the cross-channel patterns—contains information that's invisible when we look at each measurement alone?

**The goal:** Combine what we already have. Build smarter detection pathways that need *fewer tests*, generate *less waste*, and get answers *faster*. Not by collecting more data, but by actually *seeing* what's already there.

That's Illucidate—bringing the hidden signals to light.

---

## Quick Start

### Installation

```bash
pip install illucidate
```

Or clone and install from source:

```bash
git clone https://github.com/jaegertros/illucidate.git
cd illucidate
pip install -e .
```

### Basic Usage

```python
from illucidate.adapters import VictorNivoAdapter
from illucidate.core import FeatureGenerator, find_early_signals

# Load your data
adapter = VictorNivoAdapter('experiment.xlsx')
data = adapter.parse()

# Define experimental design
design = {
    'A1': {'bacteria': 'E.coli_O157H7', 'phage': 'Yes'},
    'A2': {'bacteria': 'E.coli_O157H7', 'phage': 'No'},
    # ...
}

# Generate features
generator = FeatureGenerator(data, design)
features = generator.generate_all()

# Find early detection signals
signals = find_early_signals(features, compare='phage')

# Top signal might be:
# "OD600_time_to_12x" - effect size: 31.5
# With phage: 1.2 hours | Without phage: 8.5 hours
```

### Google Colab (Zero Setup)

Try Illucidate instantly in your browser:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jaegertros/illucidate/blob/main/notebooks/01_quickstart_colab.ipynb)

---

## Features

### 🔧 Modular Design
- **Standalone components** - Use just the feature generator, just the statistical tests, or the full pipeline
- **Extensible adapters** - Add support for new plate readers easily
- **Import as needed** - No bloated dependencies

### 📊 Comprehensive Analysis
- **100+ features** per sample including:
  - Early timepoint statistics (mean, slope, max of first 3, 5, 10, 15, 20 measurements)
  - Growth characteristics (max rate, time to max rate, acceleration)
  - Lag detection (time to reach 1.1x, 1.2x, 1.5x, 2.0x baseline)
  - Cross-measurement features (ratios, correlations, temporal relationships)

### 🎯 Statistical Rigor
- T-tests with multiple comparison correction
- Effect size calculations (Cohen's d)
- False discovery rate control
- Ranked by discriminative power

### 🔌 Multiple Plate Reader Support
- Victor Nivo (Perkin Elmer)
- BioTek Synergy
- Tecan Spark/Infinite
- Generic CSV/Excel formats
- *Add your own adapter in ~50 lines of Python*

### 📈 Rich Visualizations
- Growth curve overlays (colored by experimental variables)
- Signal ranking plots
- Interaction heatmaps
- Time-to-detection comparisons

---

## Use Cases

### 🔬 Research & Development
- Optimize phage-bacteria combinations
- Test environmental conditions (temperature, pH, salts)
- Evaluate antibiotic + phage synergy
- Compare detection modalities (OD vs bioluminescence vs fluorescence)

### 📝 Publications & Theses
- Demonstrate multivariate signal discovery
- Validate findings across datasets
- Generate publication-ready figures
- Reproducible computational methods

### 🏭 Quality Control
- Rapid pathogen screening in food/water
- Earlier regulatory decisions
- Reduced time-to-release for negative samples

---

## Documentation

- [**Getting Started Guide**](docs/GETTING_STARTED.md) - Installation and first analysis
- [**Citation Guidelines**](docs/CITATION.md) - How to cite & attribute data
- [**Contributing**](docs/CONTRIBUTING.md) - How to add adapters, features, or improvements

---

## Example Results

### Time-to-Detection Improvement

| Measurement | Traditional Detection | Illucidate Signal | Improvement |
|-------------|----------------------|------------------|-------------|
| OD600 alone | 6.2 hours | - | - |
| RLU alone | 4.8 hours | - | - |
| **OD600/RLU ratio** | - | **1.3 hours** | **79% faster** |

---

## Citation

If you use Illucidate in your research, please cite:

```bibtex
@software{illucidate2024,
  title = {Illucidate: Illuminating early signals in bacterial detection},
  author = {Waddell, Caleb L.},
  year = {2024},
  url = {https://github.com/jaegertros/illucidate},
  version = {0.1.0}
}
```

**And cite the original data sources!** See [CITATION.md](docs/CITATION.md) for details.

---

## License

Illucidate is released under the [MIT License](LICENSE).

**Attribution requirements:**
- ✅ Use freely in academic and commercial projects
- ✅ Modify and redistribute
- ✅ Must preserve copyright notice
- ✅ Cite Illucidate if used in publications

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
- Adding new plate reader adapters
- Implementing additional features
- Improving documentation
- Reporting bugs

---

## Acknowledgments

Built for researchers working on:
- Phage-based bacterial detection
- Food safety and quality control
- Clinical diagnostics
- Environmental monitoring
- One Health applications

**Inspired by the need for faster, more reliable pathogen detection to protect public health.**

---

## Contact

- **Author:** Caleb L. Waddell
- **Email:** cwaddell13@gmail.com
- **Institution:** Purdue University, Department of Food Science
- **GitHub:** [@jaegertros](https://github.com/jaegertros)
- **Issues:** [GitHub Issues](https://github.com/jaegertros/illucidate/issues)

---

**Illucidate** - Because earlier detection saves lives. 💡
