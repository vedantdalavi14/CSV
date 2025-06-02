#!/usr/bin/env python3
"""
Smart CSV Cleaner - CLI Entry Point
Hybrid CLI + Natural Language Data Cleaning Tool
"""

import click
import os
import sys
from pathlib import Path

# Add the current directory to sys.path to allow imports
sys.path.insert(0, str(Path(__file__).parent))

from main import CSVCleaner
from utils.logger import setup_logger


@click.command()
@click.argument('input_file', type=click.Path(exists=True, readable=True))
@click.argument('natural_command', required=False, default='')
@click.option('--fix-names', is_flag=True, help='Fix column names (lowercase, underscores, remove special chars)')
@click.option('--fix-missing', type=click.Choice(['mean', 'median', 'mode', 'drop']), 
              help='Handle missing data with specified strategy')
@click.option('--drop-outliers', type=click.Choice(['zscore', 'iqr']), 
              help='Remove outliers using Z-score or IQR method')
@click.option('--standardize-types', is_flag=True, help='Standardize data types automatically')
@click.option('--output', '-o', default=None, help='Output file path (default: adds _cleaned suffix)')
@click.option('--excel', is_flag=True, help='Export to Excel format (.xlsx)')
@click.option('--log', default=None, help='Log file path (default: cleaning.log)')
@click.option('--preview/--no-preview', default=True, help='Show preview of cleaned data')
@click.option('--zscore-threshold', default=3.0, type=float, help='Z-score threshold for outlier detection (default: 3.0)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def clean_csv(input_file, natural_command, fix_names, fix_missing, drop_outliers, 
              standardize_types, output, excel, log, preview, zscore_threshold, verbose):
    """
    Smart CSV Cleaner - Clean messy CSV files using CLI flags or natural language.
    
    Examples:
    clean-csv data.csv --fix-names --fix-missing mean
    clean-csv data.csv "fix column names and remove outliers"
    clean-csv data.csv "standardize data types and fill missing with median" --output clean_data.csv
    """
    try:
        # Setup logger
        log_file = log or 'cleaning.log'
        logger = setup_logger(log_file, verbose)
        
        # Initialize cleaner
        cleaner = CSVCleaner(logger, zscore_threshold)
        
        # Process the CSV
        result = cleaner.process_csv(
            input_file=input_file,
            natural_command=natural_command,
            fix_names=fix_names,
            fix_missing=fix_missing,
            drop_outliers=drop_outliers,
            standardize_types=standardize_types,
            output=output,
            excel=excel,
            preview=preview
        )
        
        if result['success']:
            click.echo(f"✅ CSV cleaning completed successfully!")
            click.echo(f"📁 Output file: {result['output_file']}")
            click.echo(f"📋 Log file: {log_file}")
            if result['summary']:
                click.echo("\n📊 Summary:")
                for line in result['summary']:
                    click.echo(f"   {line}")
        else:
            click.echo(f"❌ Error: {result['error']}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    clean_csv()
