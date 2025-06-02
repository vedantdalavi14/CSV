"""
Setup configuration for Smart CSV Cleaner
"""

from setuptools import setup, find_packages
import pathlib

# Read README file for long description
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

# Read version from __init__.py or define here
VERSION = "1.0.0"

setup(
    name="smart-csv-cleaner",
    version=VERSION,
    description="A powerful Python CLI tool for cleaning messy CSV files with natural language support",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Smart CSV Cleaner Team",
    author_email="contact@smartcsvleaner.com",
    url="https://github.com/your-username/smart-csv-cleaner",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Data Scientists",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="csv data-cleaning pandas cli natural-language data-science",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.3.0",
        "click>=8.0.0",
        "tabulate>=0.8.9",
        "openpyxl>=3.0.0",
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "nlp": [
            "spacy>=3.4.0",
            "en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.4.1/en_core_web_sm-3.4.1.tar.gz",
        ],
    },
    entry_points={
        "console_scripts": [
            "clean-csv=cli:clean_csv",
            "smart-csv-cleaner=cli:clean_csv",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-username/smart-csv-cleaner/issues",
        "Source": "https://github.com/your-username/smart-csv-cleaner",
        "Documentation": "https://github.com/your-username/smart-csv-cleaner/blob/main/README.md",
    },
    zip_safe=False,
)
