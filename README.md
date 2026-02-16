<p align="center">
  <img src="assets/illucidate_logo2.svg" alt="Illucidate Logo" width="400"/>
</p>

# Illucidate 💡

**Illuminating early signals in bacterial detection**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/jaegertros/illucidate)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=flat-square&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/cwaddell13)

> *Illucidate* = **Illuminate** + **Elucidate**  
> Because bacterial detection should be both *bright* and *clear*.

---

## 🚧 Project Status: Active Development

**Current Version:** 0.1.0-alpha  
**Last Updated: February 2026

This toolkit is under active development as part of graduate research at Purdue University. Core functionality is being built and validated.

### ✅ What Works Now:
- [x] Project structure and documentation
- [x] Conceptual framework and methodology
- [ ] Victor Nivo adapter (in progress)
- [ ] Feature generation engine (in progress)
- [ ] Statistical testing framework (planned)
- [ ] Google Colab integration (planned)

### 🎯 Roadmap:

**Phase 1: Core Implementation** (Current)
- Building Victor Nivo plate reader parser
- Implementing feature generation (100+ features)
- Statistical analysis framework
- Initial validation on E. coli O157:H7 data

**Phase 2: Validation & Documentation** (Next)
- Analysis of published datasets
- Comprehensive documentation
- Example notebooks and tutorials
- Performance benchmarking

**Phase 3: Community Release** (Future)
- Multiple plate reader adapters
- Interactive Colab notebooks
- Example datasets (with attribution)
- Full API documentation

### 📢 Looking For:
- **Beta testers** with Victor Nivo, BioTek, or Tecan plate readers
- **Collaborators** interested in early detection methods
- **Datasets** for validation (with proper attribution)
- **Feedback** on methodology and implementation

**Interested?** Open an [issue](https://github.com/jaegertros/illucidate/issues) or reach out directly!

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

### ☕ Support the Synthesis ☕

Maintaining this level of cross-disciplinary research has a metabolic cost. If this toolkit helps your systems, feel free to fuel the next deep dive.

<p align="center">
  <a href="https://buymeacoffee.com/cwaddell13">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png"
         width="160">
  </a>
</p>

---

## Quick Start

**Note:** Installation instructions below reflect the planned final state. Core implementation is in progress.

### Installation (Coming Soon)

```bash
pip install illucidate
```

Or clone and follow development:

```bash
git clone https://github.com/jaegertros/illucidate.git
cd illucidate
# Watch for updates!
```

### Planned Usage

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
```

---

## Features (Planned)

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
- Victor Nivo (Perkin Elmer) - *in development*
- BioTek Synergy - *planned*
- Tecan Spark/Infinite - *planned*
- Generic CSV/Excel formats - *planned*

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

**Coming Soon:**
- Getting Started Guide
- Citation Guidelines
- Contributing Guide
- API Reference

For now, watch this repo or open an issue with questions!

---

## Example Results (Preliminary)

*Based on initial proof-of-concept work:*

| Measurement | Traditional Detection | Multivariate Signal | Improvement |
|-------------|----------------------|---------------------|-------------|
| OD600 alone | ~6 hours | - | - |
| RLU alone | ~5 hours | - | - |
| **OD600/RLU patterns** | - | **~1-2 hours** | **70-80% faster** |

*Full validation in progress.*

---

## Citation

If you use or reference Illucidate in your work, please cite:

```bibtex
@software{illucidate2025,
  title = {Illucidate: Illuminating early signals in bacterial detection},
  author = {Waddell, Caleb L.},
  year = {2025},
  url = {https://github.com/jaegertros/illucidate},
  version = {0.1.0-alpha},
  note = {Work in progress}
}
```

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

This project is in active development! Contributions, ideas, and feedback are welcome:

- 🐛 **Found a bug?** Open an [issue](https://github.com/jaegertros/illucidate/issues)
- 💡 **Have an idea?** Start a [discussion](https://github.com/jaegertros/illucidate/discussions)
- 🔧 **Want to contribute code?** Check back soon for contributing guidelines
- 📊 **Have data to share?** Reach out about collaboration

---

## Acknowledgments

Built for researchers working on:
- Phage-based bacterial detection
- Food safety and quality control
- Clinical diagnostics
- Environmental monitoring
- One Health applications

**Inspired by the need for faster, more reliable pathogen detection to protect public health.**

Special thanks to the open-source community and researchers who share their data and methods.

---

## Contact

- **Author:** Caleb L. Waddell
- **Email:** cwaddell13@gmail.com
- **Institution:** Purdue University, Department of Food Science
- **GitHub:** [@jaegertros](https://github.com/jaegertros)
- **Issues:** [GitHub Issues](https://github.com/jaegertros/illucidate/issues)

---

## Development Timeline

**February 2026** - Initial public repository and documentation  
**Spring 2026** - Core adapter implementation and thesis completion  
**Summer 2026** - Beta release with validated examples  
**Fall 2026** - Community testing and expanded documentation

*Timeline subject to change based on research priorities and validation requirements.*

---

**Illucidate** - Because earlier detection saves lives. 💡

*Watch this space. More coming soon.*
