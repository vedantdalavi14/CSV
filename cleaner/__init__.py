"""
Smart CSV Cleaner - Data Cleaning Modules
Contains all individual cleaning functions for CSV data processing
"""

__version__ = "1.0.0"
__author__ = "Smart CSV Cleaner"

# Import all cleaning modules for easy access
from .fix_names import ColumnNameFixer
from .fix_missing import MissingDataHandler
from .drop_outliers import OutlierRemover
from .standardize_types import TypeStandardizer
from .export import DataExporter
from .remove_duplicates import DuplicateRemover
from .string_cleaner import StringCleaner

__all__ = [
    'ColumnNameFixer',
    'MissingDataHandler', 
    'OutlierRemover',
    'TypeStandardizer',
    'DataExporter',
    'DuplicateRemover',
    'StringCleaner'
]
