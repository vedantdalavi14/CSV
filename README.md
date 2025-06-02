# Smart CSV Cleaner

A powerful, user-friendly **Python CLI tool** for cleaning messy CSV files. Like Black is for Python formatting, this tool is for CSVs — but smarter. It supports **both traditional CLI flags** and **natural language commands**.

## 🚀 Features

### Dual Input Support
- **Traditional CLI flags**: `--fix-names`, `--fix-missing mean`, `--drop-outliers zscore`
- **Natural language commands**: `"fix column names and remove outliers"`
- **Combined approach**: Mix both for maximum flexibility

### Core Cleaning Operations

#### 1. Column Name Standardization
- Strip whitespace and normalize case
- Replace spaces with underscores
- Remove special characters
- Ensure unique column names
- Handle numeric prefixes

#### 2. Missing Data Handling
- **Multiple strategies**: mean, median, mode, drop
- **Smart detection**: Works with numeric and categorical data
- **Column-specific**: Different strategies per data type
- **Comprehensive logging**: Track all changes

#### 3. Outlier Detection & Removal
- **Z-score method**: Configurable threshold (default: 3.0)
- **IQR method**: Interquartile range with 1.5x multiplier
- **Numeric columns only**: Automatically detects applicable columns
- **Detailed reporting**: Shows outliers removed per column

#### 4. Data Type Standardization
- **Automatic detection**: String → datetime, int, float, bool
- **Smart conversion**: Handles various date formats
- **Boolean parsing**: Recognizes true/false, yes/no, 1/0
- **Categorical optimization**: Converts appropriate columns to category type

#### 5. Export Options
- **CSV output**: UTF-8 encoded, clean formatting
- **Excel export**: With auto-sized columns and summary sheets
- **Custom naming**: Specify output path or use auto-generated names

#### 6. Comprehensive Logging
- **Detailed tracking**: Every transformation timestamped
- **Operation summary**: Clear before/after statistics
- **Error handling**: Graceful failure with informative messages
- **Verbose mode**: Additional debugging information

## 📦 Installation

### Requirements
- Python 3.7+
- pandas
- click
- tabulate
- openpyxl
- numpy

### Install Dependencies
```bash
pip install pandas click tabulate openpyxl numpy
