"""
Outlier Detection and Removal Module
Provides Z-score and IQR methods for detecting and removing outliers
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any, List
import logging


class OutlierRemover:
    """Handles outlier detection and removal using statistical methods"""
    
    def __init__(self, logger, zscore_threshold: float = 3.0):
        self.logger = logger
        self.zscore_threshold = zscore_threshold
    
    def remove_outliers(self, df: pd.DataFrame, method: str = 'zscore') -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Remove outliers using the specified method
        
        Args:
            df: Input DataFrame
            method: 'zscore' or 'iqr'
            
        Returns:
            Tuple of (DataFrame with outliers removed, statistics dictionary)
        """
        if df.empty:
            self.logger.warning("DataFrame is empty, skipping outlier removal")
            return df, {'total_removed': 0}
        
        method = method.lower()
        valid_methods = ['zscore', 'iqr']
        
        if method not in valid_methods:
            self.logger.error(f"Invalid method '{method}'. Must be one of {valid_methods}")
            return df, {'total_removed': 0}
        
        self.logger.info(f"Removing outliers using {method.upper()} method")
        
        # Get numeric columns only
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_columns:
            self.logger.warning("No numeric columns found for outlier detection")
            return df, {'total_removed': 0, 'numeric_columns_analyzed': 0}
        
        self.logger.info(f"Analyzing outliers in {len(numeric_columns)} numeric columns")
        
        original_rows = len(df)
        
        if method == 'zscore':
            result_df, outlier_stats = self._remove_zscore_outliers(df, numeric_columns)
        else:  # iqr
            result_df, outlier_stats = self._remove_iqr_outliers(df, numeric_columns)
        
        rows_removed = original_rows - len(result_df)
        
        # Compile final statistics
        stats = {
            'method': method,
            'total_removed': rows_removed,
            'original_rows': original_rows,
            'final_rows': len(result_df),
            'numeric_columns_analyzed': len(numeric_columns),
            'column_stats': outlier_stats,
            'removal_percentage': round((rows_removed / original_rows) * 100, 2) if original_rows > 0 else 0
        }
        
        if rows_removed > 0:
            self.logger.info(f"Removed {rows_removed} outlier rows ({stats['removal_percentage']}%)")
        else:
            self.logger.info("No outliers detected and removed")
        
        # Warn if too many rows removed
        if stats['removal_percentage'] > 20:
            self.logger.warning(f"Removed {stats['removal_percentage']}% of data - consider adjusting thresholds")
        
        return result_df, stats
    
    def _remove_zscore_outliers(self, df: pd.DataFrame, numeric_columns: List[str]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Remove outliers using Z-score method
        
        Args:
            df: Input DataFrame
            numeric_columns: List of numeric column names
            
        Returns:
            Tuple of (cleaned DataFrame, column statistics)
        """
        outlier_mask = pd.Series([False] * len(df))
        column_stats = {}
        
        for column in numeric_columns:
            try:
                # Calculate Z-scores
                z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
                
                # Identify outliers
                column_outliers = z_scores > self.zscore_threshold
                outlier_count = column_outliers.sum()
                
                # Update master mask
                outlier_mask |= column_outliers
                
                column_stats[column] = {
                    'outliers_detected': int(outlier_count),
                    'threshold': self.zscore_threshold,
                    'max_zscore': float(z_scores.max()) if not z_scores.empty else 0,
                    'mean': float(df[column].mean()),
                    'std': float(df[column].std())
                }
                
                if outlier_count > 0:
                    self.logger.debug(f"Column '{column}': {outlier_count} outliers (max Z-score: {z_scores.max():.2f})")
                
            except Exception as e:
                self.logger.error(f"Error processing column '{column}' for Z-score outliers: {str(e)}")
                column_stats[column] = {'error': str(e)}
        
        # Remove rows marked as outliers
        result_df = df[~outlier_mask].reset_index(drop=True)
        
        return result_df, column_stats
    
    def _remove_iqr_outliers(self, df: pd.DataFrame, numeric_columns: List[str]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Remove outliers using Interquartile Range (IQR) method
        
        Args:
            df: Input DataFrame
            numeric_columns: List of numeric column names
            
        Returns:
            Tuple of (cleaned DataFrame, column statistics)
        """
        outlier_mask = pd.Series([False] * len(df))
        column_stats = {}
        
        for column in numeric_columns:
            try:
                # Calculate quartiles and IQR
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                
                # Define outlier bounds
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Identify outliers
                column_outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
                outlier_count = column_outliers.sum()
                
                # Update master mask
                outlier_mask |= column_outliers
                
                column_stats[column] = {
                    'outliers_detected': int(outlier_count),
                    'Q1': float(Q1),
                    'Q3': float(Q3),
                    'IQR': float(IQR),
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound),
                    'min_value': float(df[column].min()),
                    'max_value': float(df[column].max())
                }
                
                if outlier_count > 0:
                    self.logger.debug(f"Column '{column}': {outlier_count} outliers outside [{lower_bound:.2f}, {upper_bound:.2f}]")
                
            except Exception as e:
                self.logger.error(f"Error processing column '{column}' for IQR outliers: {str(e)}")
                column_stats[column] = {'error': str(e)}
        
        # Remove rows marked as outliers
        result_df = df[~outlier_mask].reset_index(drop=True)
        
        return result_df, column_stats
    
    def detect_outliers_only(self, df: pd.DataFrame, method: str = 'zscore') -> Dict[str, Any]:
        """
        Detect outliers without removing them (for analysis purposes)
        
        Args:
            df: Input DataFrame
            method: 'zscore' or 'iqr'
            
        Returns:
            Dictionary with outlier detection results
        """
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_columns:
            return {'error': 'No numeric columns found'}
        
        if method.lower() == 'zscore':
            _, stats = self._remove_zscore_outliers(df, numeric_columns)
        else:
            _, stats = self._remove_iqr_outliers(df, numeric_columns)
        
        # Calculate total outliers without removing them
        total_outliers = sum(
            col_stats.get('outliers_detected', 0) 
            for col_stats in stats.values() 
            if isinstance(col_stats, dict) and 'error' not in col_stats
        )
        
        return {
            'method': method,
            'total_outliers_detected': total_outliers,
            'numeric_columns_analyzed': len(numeric_columns),
            'column_details': stats
        }
    
    def get_outlier_report(self, df: pd.DataFrame, method: str = 'zscore') -> str:
        """
        Generate a detailed report of outliers in the DataFrame
        
        Args:
            df: Input DataFrame
            method: 'zscore' or 'iqr'
            
        Returns:
            Formatted string report
        """
        outlier_info = self.detect_outliers_only(df, method)
        
        if 'error' in outlier_info:
            return f"❌ {outlier_info['error']}"
        
        if outlier_info['total_outliers_detected'] == 0:
            return f"✅ No outliers detected using {method.upper()} method"
        
        report = [
            f"📊 Outlier Detection Report ({method.upper()} method)",
            f"Total outliers detected: {outlier_info['total_outliers_detected']}",
            f"Columns analyzed: {outlier_info['numeric_columns_analyzed']}",
            f"",
            f"Outliers by column:"
        ]
        
        for column, stats in outlier_info['column_details'].items():
            if isinstance(stats, dict) and 'error' not in stats:
                count = stats.get('outliers_detected', 0)
                if count > 0:
                    if method.lower() == 'zscore':
                        report.append(f"  • {column}: {count} outliers (threshold: {stats.get('threshold', 'N/A')})")
                    else:
                        report.append(f"  • {column}: {count} outliers (bounds: [{stats.get('lower_bound', 'N/A'):.2f}, {stats.get('upper_bound', 'N/A'):.2f}])")
        
        return "\n".join(report)
