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

# New advanced options
@click.option('--remove-duplicates', is_flag=True, help='Remove duplicate rows.')
@click.option('--trim-whitespace', is_flag=True, help='Trim leading/trailing whitespace from all cells.')
@click.option('--change-case', type=click.Choice(['upper', 'lower', 'title']), help='Change text case.')
@click.option('--find', help='Value to find for replacement.')
@click.option('--replace', help='Value to replace with.')
@click.option('--drop-columns', help='Comma-separated list of columns to drop.')

@click.option('--output', '-o', default=None, help='Output file path (default: adds _cleaned suffix)')
@click.option('--excel', is_flag=True, help='Export to Excel format (.xlsx)')
@click.option('--log', default=None, help='Log file path (default: cleaning.log)')
@click.option('--preview/--no-preview', default=True, help='Show preview of cleaned data')
@click.option('--zscore-threshold', default=3.0, type=float, help='Z-score threshold for outlier detection (default: 3.0)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def clean_csv(input_file, natural_command, fix_names, fix_missing, drop_outliers, 
              standardize_types, remove_duplicates, trim_whitespace, change_case,
              find, replace, drop_columns, output, excel, log, preview, zscore_threshold, verbose):
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
        cleaner = CSVCleaner(zscore_threshold=zscore_threshold, logger=logger)

        # Prepare find_replace dictionary
        find_replace_dict = None
        if find:
            find_replace_dict = {'find': find, 'replace': replace or ''}

        # Prepare drop_columns list
        drop_columns_list = drop_columns.split(',') if drop_columns else None
        
        # Process the CSV
        result = cleaner.process_csv(
            input_file=input_file,
            natural_command=natural_command,
            fix_names=fix_names,
            fix_missing=fix_missing,
            drop_outliers=drop_outliers,
            standardize_types=standardize_types,
            remove_duplicates=remove_duplicates,
            trim_whitespace=trim_whitespace,
            change_case=change_case,
            find_replace=find_replace_dict,
            drop_columns=drop_columns_list,
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
