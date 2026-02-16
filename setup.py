"""
Setup configuration for Illucidate package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="illucidate",
    version="0.1.0",
    author="Caleb Waddell",
    author_email="your.email@purdue.edu",  # Update this
    description="AI-powered early detection for bacterial strain classification from growth curves",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/illucidate",  # Update this
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "scipy>=1.9.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.5.0",
        "openpyxl>=3.0.0",  # For Excel file support
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "jupyter>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "illucidate-test=illucidate.scripts.test_ecoli:test_ecoli_dataset",
        ],
    },
)
