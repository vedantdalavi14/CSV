# Smart CSV Cleaner: Hybrid CLI & Natural Language Data Cleaning Tool

A powerful, user-friendly tool for cleaning messy CSV files, accessible via a modern **web interface** and a powerful **command-line interface (CLI)**. It supports both traditional cleaning operations and advanced transformations, making data cleaning faster and more intuitive.

![Smart CSV Cleaner UI](attached_assets/app_screenshot.png) <!-- Assuming a screenshot will be placed here -->

## 🚀 Features

### 1. Interactive Web Interface (GUI)

The primary way to use the Smart CSV Cleaner is through its intuitive web interface.

- **Upload & Analyze**: Simply upload your CSV file to get an instant analysis, including:
    - Row and column counts
    - A preview of the first 10 rows
    - A count of missing values
- **Core Cleaning Operations**:
    - **Fix Column Names**: Standardizes column headers (strips extra spaces, removes special characters, and ensures uniqueness).
    - **Handle Missing Data**: Choose a strategy (mean, median, mode, or drop rows) to handle empty cells.
    - **Remove Outliers**: Automatically detect and remove outliers using Z-score or IQR methods.
- **Advanced Cleaning Operations**:
    - **Remove Duplicates**: Delete duplicate rows from your dataset.
    - **Trim Whitespace**: Remove leading/trailing whitespace from all cells.
    - **Change Text Case**: Convert text to `UPPERCASE`, `lowercase`, or `Title Case`.
    - **Find and Replace**: Replace specific values throughout the dataset.
    - **Drop Columns**: Select and remove unwanted columns.
- **Post-Cleaning Analysis**: After cleaning, see a "Final File Analysis" with updated stats and a preview of the cleaned data.
- **Export Options**: Download the cleaned data as a `.csv` or `.xlsx` file.

### 2. Command-Line Interface (CLI)

For users who prefer the command line or need to automate cleaning tasks.

- **Dual Input Support**:
    - **Traditional flags**: `--fix-names`, `--fix-missing mean`, `--drop-outliers zscore`
    - **Natural language commands**: `"fix column names and remove outliers"`
- **Comprehensive Operations**: All core cleaning operations from the UI are available via the CLI.
- **Detailed Logging**: Every transformation is timestamped and logged for full traceability.

## 📦 Installation & Setup

### Requirements
- Python 3.7+
- pandas
- click
- tabulate
- openpyxl
- numpy
- Flask

### Install Dependencies
```bash
pip install pandas click tabulate openpyxl numpy flask
```

## Usage

### Running the Web Application
1. Start the Flask server:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to `http://127.0.0.1:5000`.

### Using the CLI
Run the tool from your terminal with the desired flags:
```bash
python main.py --input-file your_data.csv --fix-names --fix-missing median --output-file cleaned_data.csv
```

Or with a natural language command:
```bash
python main.py --input-file your_data.csv --nlp-command "fix names and fill missing values with the median"
```
