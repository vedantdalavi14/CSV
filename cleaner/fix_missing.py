"""
Missing Data Handling Module
Provides various strategies for handling missing/null values in CSV data
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any
import logging


class MissingDataHandler:
    """Handles missing data with various strategies"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def handle_missing_data(self, df: pd.DataFrame, strategy: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Handle missing data using the specified strategy
        
        Args:
            df: Input DataFrame
            strategy: One of 'mean', 'median', 'mode', 'drop'
            
        Returns:
            Tuple of (processed DataFrame, statistics dictionary)
        """
        if df.empty:
            self.logger.warning("DataFrame is empty, skipping missing data handling")
            return df, {}
        
        strategy = strategy.lower()
        valid_strategies = ['mean', 'median', 'mode', 'drop']
        
        if strategy not in valid_strategies:
            self.logger.error(f"Invalid strategy '{strategy}'. Must be one of {valid_strategies}")
            return df, {}
        
        self.logger.info(f"Handling missing data using '{strategy}' strategy")
        
        # Analyze missing data before processing
        missing_info = self._analyze_missing_data(df)
        
        if missing_info['total_missing'] == 0:
            self.logger.info("No missing values found in the dataset")
            return df, {'strategy': strategy, 'changes_made': False}
        
        self.logger.info(f"Found {missing_info['total_missing']} missing values across {len(missing_info['columns_with_missing'])} columns")
        
        # Apply the selected strategy
        if strategy == 'drop':
            result_df, stats = self._drop_missing(df)
        else:
            result_df, stats = self._fill_missing(df, strategy)
        
        stats['strategy'] = strategy
        stats['original_missing_info'] = missing_info
        
        return result_df, stats
    
    def _analyze_missing_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze missing data patterns in the DataFrame
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with missing data statistics
        """
        missing_counts = df.isnull().sum()
        total_missing = missing_counts.sum()
        
        columns_with_missing = missing_counts[missing_counts > 0].to_dict()
        missing_percentages = (missing_counts / len(df) * 100).round(2)
        
        return {
            'total_missing': int(total_missing),
            'columns_with_missing': columns_with_missing,
            'missing_percentages': missing_percentages.to_dict(),
            'total_rows': len(df),
            'total_columns': len(df.columns)
        }
    
    def _fill_missing(self, df: pd.DataFrame, strategy: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Fill missing values using the specified strategy
        
        Args:
            df: Input DataFrame
            strategy: 'mean', 'median', or 'mode'
            
        Returns:
            Tuple of (filled DataFrame, statistics)
        """
        result_df = df.copy()
        fill_values = {}
        columns_filled = []
        
        for column in df.columns:
            if df[column].isnull().any():
                original_missing = df[column].isnull().sum()
                
                try:
                    if strategy == 'mean':
                        if pd.api.types.is_numeric_dtype(df[column]):
                            fill_value = df[column].mean()
                            result_df[column].fillna(fill_value, inplace=True)
                            fill_values[column] = fill_value
                            columns_filled.append(column)
                            self.logger.debug(f"Filled {original_missing} missing values in '{column}' with mean: {fill_value:.4f}")
                        else:
                            self.logger.warning(f"Cannot apply mean to non-numeric column '{column}', skipping")
                    
                    elif strategy == 'median':
                        if pd.api.types.is_numeric_dtype(df[column]):
                            fill_value = df[column].median()
                            result_df[column].fillna(fill_value, inplace=True)
                            fill_values[column] = fill_value
                            columns_filled.append(column)
                            self.logger.debug(f"Filled {original_missing} missing values in '{column}' with median: {fill_value:.4f}")
                        else:
                            self.logger.warning(f"Cannot apply median to non-numeric column '{column}', skipping")
                    
                    elif strategy == 'mode':
                        if not df[column].mode().empty:
                            fill_value = df[column].mode().iloc[0]
                            result_df[column].fillna(fill_value, inplace=True)
                            fill_values[column] = fill_value
                            columns_filled.append(column)
                            self.logger.debug(f"Filled {original_missing} missing values in '{column}' with mode: {fill_value}")
                        else:
                            self.logger.warning(f"Cannot determine mode for column '{column}', skipping")
                
                except Exception as e:
                    self.logger.error(f"Error filling missing values in column '{column}': {str(e)}")
        
        stats = {
            'changes_made': len(columns_filled) > 0,
            'columns_filled': columns_filled,
            'fill_values': fill_values,
            'total_columns_processed': len(columns_filled)
        }
        
        if columns_filled:
            self.logger.info(f"Successfully filled missing values in {len(columns_filled)} columns")
        else:
            self.logger.info("No missing values were filled (no applicable columns found)")
        
        return result_df, stats
    
    def _drop_missing(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Drop rows containing missing values
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (DataFrame with rows dropped, statistics)
        """
        original_rows = len(df)
        result_df = df.dropna()
        rows_dropped = original_rows - len(result_df)
        
        stats = {
            'changes_made': rows_dropped > 0,
            'rows_dropped': rows_dropped,
            'original_rows': original_rows,
            'final_rows': len(result_df)
        }
        
        if rows_dropped > 0:
            self.logger.info(f"Dropped {rows_dropped} rows containing missing values")
            self.logger.info(f"Dataset reduced from {original_rows} to {len(result_df)} rows")
        else:
            self.logger.info("No rows needed to be dropped (no missing values found)")
        
        return result_df, stats
    
    def get_missing_data_report(self, df: pd.DataFrame) -> str:
        """
        Generate a detailed report of missing data in the DataFrame
        
        Args:
            df: Input DataFrame
            
        Returns:
            Formatted string report
        """
        missing_info = self._analyze_missing_data(df)
        
        if missing_info['total_missing'] == 0:
            return "✅ No missing values found in the dataset"
        
        report = [
            f"📊 Missing Data Report",
            f"Total missing values: {missing_info['total_missing']}",
            f"Columns affected: {len(missing_info['columns_with_missing'])}/{missing_info['total_columns']}",
            f"",
            f"Missing values by column:"
        ]
        
        for column, count in missing_info['columns_with_missing'].items():
            percentage = missing_info['missing_percentages'][column]
            report.append(f"  • {column}: {count} ({percentage}%)")
        
        return "\n".join(report)
