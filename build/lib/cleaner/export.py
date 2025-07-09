"""
Data Export Module
Handles exporting cleaned data to various formats (CSV, Excel)
"""

import pandas as pd
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging


class DataExporter:
    """Handles exporting cleaned data to different formats"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def export_data(self, df: pd.DataFrame, output_path: str, excel: bool = False) -> bool:
        """
        Export DataFrame to specified format
        
        Args:
            df: DataFrame to export
            output_path: Output file path
            excel: Whether to export to Excel format
            
        Returns:
            True if export successful, False otherwise
        """
        if df.empty:
            self.logger.warning("DataFrame is empty, creating empty output file")
        
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                self.logger.debug(f"Created output directory: {output_dir}")
            
            if excel or output_path.endswith('.xlsx'):
                return self._export_to_excel(df, output_path)
            else:
                return self._export_to_csv(df, output_path)
                
        except Exception as e:
            self.logger.error(f"Failed to export data: {str(e)}")
            return False
    
    def _export_to_csv(self, df: pd.DataFrame, output_path: str) -> bool:
        """
        Export DataFrame to CSV format
        
        Args:
            df: DataFrame to export
            output_path: CSV file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure .csv extension
            if not output_path.endswith('.csv'):
                output_path += '.csv'
            
            df.to_csv(output_path, index=False, encoding='utf-8')
            
            file_size = os.path.getsize(output_path)
            self.logger.info(f"Successfully exported {len(df)} rows to CSV: {output_path}")
            self.logger.debug(f"File size: {self._format_file_size(file_size)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export CSV: {str(e)}")
            return False
    
    def _export_to_excel(self, df: pd.DataFrame, output_path: str) -> bool:
        """
        Export DataFrame to Excel format
        
        Args:
            df: DataFrame to export
            output_path: Excel file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure .xlsx extension
            if not output_path.endswith('.xlsx'):
                output_path += '.xlsx'
            
            # Create Excel writer with formatting options
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Cleaned Data', index=False)
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Cleaned Data']
                
                # Auto-adjust column widths
                self._auto_adjust_column_widths(worksheet, df)
                
                # Add a summary sheet if there are multiple data types
                if len(df.columns) > 1:
                    self._add_summary_sheet(writer, df)
            
            file_size = os.path.getsize(output_path)
            self.logger.info(f"Successfully exported {len(df)} rows to Excel: {output_path}")
            self.logger.debug(f"File size: {self._format_file_size(file_size)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export Excel: {str(e)}")
            return False
    
    def _auto_adjust_column_widths(self, worksheet, df: pd.DataFrame):
        """Auto-adjust column widths in Excel worksheet"""
        try:
            for column in df.columns:
                column_letter = worksheet.cell(row=1, column=df.columns.get_loc(column) + 1).column_letter
                max_length = 0
                
                # Check header length
                max_length = max(max_length, len(str(column)))
                
                # Check data lengths (sample first 100 rows for performance)
                sample_data = df[column].head(100)
                for value in sample_data:
                    if pd.notna(value):
                        max_length = max(max_length, len(str(value)))
                
                # Set column width (with some padding)
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                worksheet.column_dimensions[column_letter].width = adjusted_width
                
        except Exception as e:
            self.logger.warning(f"Failed to auto-adjust column widths: {str(e)}")
    
    def _add_summary_sheet(self, writer, df: pd.DataFrame):
        """Add a summary sheet to the Excel workbook"""
        try:
            # Create summary data
            summary_data = {
                'Metric': [
                    'Total Rows',
                    'Total Columns',
                    'Data Types',
                    'Missing Values',
                    'Memory Usage (KB)'
                ],
                'Value': [
                    len(df),
                    len(df.columns),
                    len(df.dtypes.unique()),
                    df.isnull().sum().sum(),
                    round(df.memory_usage(deep=True).sum() / 1024, 2)
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Add column information
            column_info = {
                'Column': df.columns.tolist(),
                'Data Type': [str(dtype) for dtype in df.dtypes],
                'Non-Null Count': [df[col].count() for col in df.columns],
                'Null Count': [df[col].isnull().sum() for col in df.columns]
            }
            
            column_df = pd.DataFrame(column_info)
            column_df.to_excel(writer, sheet_name='Column Info', index=False)
            
        except Exception as e:
            self.logger.warning(f"Failed to add summary sheet: {str(e)}")
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def export_multiple_formats(self, df: pd.DataFrame, base_path: str) -> Dict[str, bool]:
        """
        Export DataFrame to multiple formats
        
        Args:
            df: DataFrame to export
            base_path: Base file path (without extension)
            
        Returns:
            Dictionary with format names and success status
        """
        results = {}
        
        # Remove extension from base_path if present
        base_path = os.path.splitext(base_path)[0]
        
        # Export to CSV
        csv_path = f"{base_path}.csv"
        results['csv'] = self._export_to_csv(df, csv_path)
        
        # Export to Excel
        xlsx_path = f"{base_path}.xlsx"
        results['excel'] = self._export_to_excel(df, xlsx_path)
        
        return results
    
    def validate_output_path(self, output_path: str, excel: bool = False) -> tuple:
        """
        Validate and normalize output path
        
        Args:
            output_path: Proposed output path
            excel: Whether Excel format is intended
            
        Returns:
            Tuple of (is_valid, normalized_path, error_message)
        """
        try:
            # Convert to Path object for easier manipulation
            path = Path(output_path)
            
            # Check if directory is writable
            parent_dir = path.parent
            if not parent_dir.exists():
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    return False, None, f"Cannot create directory: {parent_dir}"
            
            if not os.access(parent_dir, os.W_OK):
                return False, None, f"Directory not writable: {parent_dir}"
            
            # Ensure correct extension
            if excel:
                if not path.suffix.lower() in ['.xlsx', '.xls']:
                    path = path.with_suffix('.xlsx')
            else:
                if not path.suffix.lower() == '.csv':
                    path = path.with_suffix('.csv')
            
            # Check if file already exists and is writable
            if path.exists():
                if not os.access(path, os.W_OK):
                    return False, None, f"File not writable: {path}"
            
            return True, str(path), None
            
        except Exception as e:
            return False, None, f"Invalid path: {str(e)}"
