"""
Smart CSV Cleaner - Central Logic Dispatcher
Handles the main cleaning pipeline and coordinates all modules
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from tabulate import tabulate

from parser.nlp_parser import NLPParser
from cleaner.fix_names import ColumnNameFixer
from cleaner.fix_missing import MissingDataHandler
from cleaner.drop_outliers import OutlierRemover
from cleaner.standardize_types import TypeStandardizer
from cleaner.export import DataExporter
from cleaner.remove_duplicates import DuplicateRemover
from cleaner.string_cleaner import StringCleaner
from utils.helpers import validate_file, generate_output_filename


class CSVCleaner:
    """Main CSV cleaning coordinator class"""
    
    def __init__(self, zscore_threshold: float = 3.0, logger=None):
        # If no logger is provided, create a basic one
        if logger:
            self.logger = logger
        else:
            import logging
            self.logger = logging.getLogger(__name__)
            logging.basicConfig(level=logging.INFO)

        self.zscore_threshold = zscore_threshold
        self.nlp_parser = NLPParser()
        self.name_fixer = ColumnNameFixer(self.logger)
        self.missing_handler = MissingDataHandler(self.logger)
        self.outlier_remover = OutlierRemover(self.logger, zscore_threshold)
        self.type_standardizer = TypeStandardizer(self.logger)
        self.exporter = DataExporter(self.logger)
        self.duplicate_remover = DuplicateRemover(self.logger)
        self.string_cleaner = StringCleaner(self.logger)
        
    def process_csv(self, input_file: str, natural_command: str = '', 
                   fix_names: bool = False, fix_missing: Optional[str] = None,
                   drop_outliers: Optional[str] = None, standardize_types: bool = False,
                   remove_duplicates: bool = False,
                   trim_whitespace: bool = False, change_case: Optional[str] = None,
                   find_replace: Optional[Dict[str, str]] = None,
                   drop_columns: Optional[List[str]] = None,
                   output: Optional[str] = None, excel: bool = False, 
                   preview: bool = True) -> Dict[str, Any]:
        """
        Main processing pipeline for CSV cleaning
        
        Returns:
            Dict with success status, output file path, error message, and summary
        """
        try:
            # Validate input file
            if not validate_file(input_file):
                return {
                    'success': False,
                    'error': f'Invalid input file: {input_file}',
                    'output_file': None,
                    'summary': []
                }
            
            self.logger.info(f"Starting CSV cleaning process for: {input_file}")
            
            # Load CSV data
            try:
                df = pd.read_csv(input_file)
                self.logger.info(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Failed to load CSV file: {str(e)}',
                    'output_file': None,
                    'summary': []
                }
            
            # Store original shape for summary
            original_shape = df.shape
            
            # Parse natural language command if provided
            nlp_flags = {}
            if natural_command.strip():
                self.logger.info(f"Parsing natural language command: '{natural_command}'")
                nlp_flags = self.nlp_parser.parse_command(natural_command)
                self.logger.info(f"NLP parsing result: {nlp_flags}")
            
            # Merge CLI flags with NLP flags (CLI flags take precedence)
            final_flags = {
                'fix_names': fix_names or nlp_flags.get('fix_names', False),
                'fix_missing': fix_missing or nlp_flags.get('fix_missing'),
                'drop_outliers': drop_outliers or nlp_flags.get('drop_outliers'),
                'standardize_types': standardize_types or nlp_flags.get('standardize_types', False),
                'remove_duplicates': remove_duplicates,
                'trim_whitespace': trim_whitespace,
                'change_case': change_case,
                'find_replace': find_replace,
                'drop_columns': drop_columns
            }
            
            self.logger.info(f"Final cleaning flags: {final_flags}")
            
            # Execute cleaning pipeline in order
            transformations = []
            
            # 0. Drop columns
            if final_flags['drop_columns']:
                cols_to_drop = [col for col in final_flags['drop_columns'] if col in df.columns]
                if cols_to_drop:
                    df.drop(columns=cols_to_drop, inplace=True)
                    transformations.append(f"Dropped {len(cols_to_drop)} columns: {', '.join(cols_to_drop)}")
                    self.logger.info(f"Dropped columns: {', '.join(cols_to_drop)}")
            
            # 1. Fix column names
            if final_flags['fix_names']:
                df, name_changes = self.name_fixer.fix_column_names(df)
                if name_changes:
                    transformations.append(f"Fixed {len(name_changes)} column names")
            
            # 2. Remove duplicates
            if final_flags['remove_duplicates']:
                df, duplicate_stats = self.duplicate_remover.remove_duplicates(df)
                if duplicate_stats.get('rows_removed', 0) > 0:
                    transformations.append(f"Removed {duplicate_stats['rows_removed']} duplicate rows")
            
            # 3. String transformations
            if final_flags['trim_whitespace']:
                df, trim_stats = self.string_cleaner.trim_whitespace(df)
                if trim_stats.get('columns_trimmed'):
                    transformations.append(f"Trimmed whitespace from {len(trim_stats['columns_trimmed'])} columns")
            
            if final_flags['change_case']:
                df, case_stats = self.string_cleaner.change_case(df, final_flags['change_case'])
                if case_stats:
                    transformations.append(f"Changed string case to {final_flags['change_case']}")

            if final_flags['find_replace'] and final_flags['find_replace'].get('find'):
                find_val = final_flags['find_replace']['find']
                replace_val = final_flags['find_replace'].get('replace', '')
                df.replace(find_val, replace_val, inplace=True)
                transformations.append(f"Replaced all instances of '{find_val}' with '{replace_val}'")
                self.logger.info(f"Replaced '{find_val}' with '{replace_val}'")
            
            # 4. Handle missing data
            if final_flags['fix_missing']:
                df, missing_stats = self.missing_handler.handle_missing_data(
                    df, strategy=final_flags['fix_missing']
                )
                if missing_stats and missing_stats.get('changes_made'):
                    transformations.append(f"Handled missing data using {final_flags['fix_missing']} strategy")
            
            # 5. Remove outliers
            if final_flags['drop_outliers']:
                df, outlier_stats = self.outlier_remover.remove_outliers(
                    df, method=final_flags['drop_outliers']
                )
                if outlier_stats['total_removed'] > 0:
                    transformations.append(f"Removed {outlier_stats['total_removed']} outlier rows")
            
            # 6. Standardize data types
            if final_flags['standardize_types']:
                df, type_changes = self.type_standardizer.standardize_types(df)
                if type_changes:
                    transformations.append(f"Standardized {len(type_changes)} column types")
            
            # Generate output filename
            output_file = output or generate_output_filename(input_file, excel)
            
            # Export results
            export_success = self.exporter.export_data(df, output_file, excel)
            if not export_success:
                return {
                    'success': False,
                    'error': 'Failed to export cleaned data',
                    'output_file': None,
                    'summary': []
                }
            
            # Create summary
            final_shape = df.shape
            total_missing = int(df.isnull().sum().sum())

            summary = [
                f"Original: {original_shape[0]} rows × {original_shape[1]} columns",
                f"Final: {final_shape[0]} rows × {final_shape[1]} columns"
            ]
            summary.extend(transformations)
            
            # Show preview if requested
            preview_data = None
            if preview and not df.empty:
                preview_data = {
                    'columns': df.columns.tolist(),
                    'data': df.head(10).to_dict('records')
                }
            
            self.logger.info("CSV cleaning completed successfully")
            
            excel_filename = f"{Path(output_file).stem}.xlsx" if excel else None
            
            return {
                'success': True,
                'error': None,
                'output_filename': Path(output_file).name,
                'excel_filename': excel_filename,
                'transformations': transformations,
                'preview': preview_data,
                'final_stats': {
                    'rows': final_shape[0],
                    'columns': final_shape[1],
                    'missing_values': total_missing
                }
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error during processing: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}',
                'output_file': None,
                'summary': []
            }

    def _show_preview(self, df: pd.DataFrame, max_rows: int = 5):
        """Show a preview of the cleaned data using tabulate"""
        try:
            preview_df = df.head(max_rows)
            print("\n📊 Preview of cleaned data:")
            print(tabulate(preview_df, headers='keys', tablefmt='grid', showindex=False))
            
            if len(df) > max_rows:
                print(f"... and {len(df) - max_rows} more rows")
                
        except Exception as e:
            self.logger.warning(f"Failed to show preview: {str(e)}")
