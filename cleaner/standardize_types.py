"""
Data Type Standardization Module
Automatically detects and converts data types for better consistency
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any, List
import re
import logging
from datetime import datetime


class TypeStandardizer:
    """Handles automatic data type detection and standardization"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def standardize_types(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Automatically standardize data types for all columns
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (DataFrame with standardized types, type change dictionary)
        """
        if df.empty:
            self.logger.warning("DataFrame is empty, skipping type standardization")
            return df, {}
        
        self.logger.info(f"Standardizing data types for {len(df.columns)} columns")
        
        result_df = df.copy()
        type_changes = {}
        
        for column in df.columns:
            try:
                original_dtype = str(df[column].dtype)
                new_dtype, converted_series = self._detect_and_convert_type(df[column])
                
                if new_dtype != original_dtype:
                    result_df[column] = converted_series
                    type_changes[column] = f"{original_dtype} -> {new_dtype}"
                    self.logger.debug(f"Column '{column}': {original_dtype} -> {new_dtype}")
                
            except Exception as e:
                self.logger.error(f"Error standardizing type for column '{column}': {str(e)}")
        
        if type_changes:
            self.logger.info(f"Successfully standardized types for {len(type_changes)} columns")
        else:
            self.logger.info("No type conversions were necessary")
        
        return result_df, type_changes
    
    def _detect_and_convert_type(self, series: pd.Series) -> Tuple[str, pd.Series]:
        """
        Detect the best data type for a series and convert it
        
        Args:
            series: Input pandas Series
            
        Returns:
            Tuple of (detected type name, converted series)
        """
        # Skip if series is empty or all null
        if series.empty or series.isnull().all():
            return str(series.dtype), series
        
        # Remove null values for type detection
        non_null_series = series.dropna()
        
        if non_null_series.empty:
            return str(series.dtype), series
        
        # Try conversions in order of preference
        
        # 1. Try boolean conversion
        if self._is_boolean_series(non_null_series):
            converted = self._convert_to_boolean(series)
            return 'bool', converted
        
        # 2. Try integer conversion
        if self._is_integer_series(non_null_series):
            converted = self._convert_to_integer(series)
            return 'int64', converted
        
        # 3. Try float conversion
        if self._is_float_series(non_null_series):
            converted = self._convert_to_float(series)
            return 'float64', converted
        
        # 4. Try datetime conversion
        if self._is_datetime_series(non_null_series):
            converted = self._convert_to_datetime(series)
            return 'datetime64[ns]', converted
        
        # 5. Convert to string/category if appropriate
        if series.dtype == 'object':
            # Check if it should be categorical
            if self._should_be_categorical(series):
                converted = series.astype('category')
                return 'category', converted
            else:
                # Ensure it's proper string type
                converted = series.astype('string')
                return 'string', converted
        
        # No conversion needed
        return str(series.dtype), series
    
    def _is_boolean_series(self, series: pd.Series) -> bool:
        """Check if series contains boolean-like values"""
        unique_values = set(str(val).lower().strip() for val in series.unique())
        
        # Common boolean representations
        true_values = {'true', '1', 'yes', 'y', 't', 'on'}
        false_values = {'false', '0', 'no', 'n', 'f', 'off'}
        boolean_values = true_values | false_values
        
        return unique_values.issubset(boolean_values)
    
    def _convert_to_boolean(self, series: pd.Series) -> pd.Series:
        """Convert series to boolean type"""
        def convert_value(val):
            if pd.isnull(val):
                return val
            str_val = str(val).lower().strip()
            true_values = {'true', '1', 'yes', 'y', 't', 'on'}
            return str_val in true_values
        
        return series.apply(convert_value)
    
    def _is_integer_series(self, series: pd.Series) -> bool:
        """Check if series contains integer values"""
        try:
            # Try to convert to numeric first
            numeric_series = pd.to_numeric(series, errors='coerce')
            
            # Check if all non-null values are integers
            non_null_numeric = numeric_series.dropna()
            if non_null_numeric.empty:
                return False
            
            # Check if all values are whole numbers
            return (non_null_numeric % 1 == 0).all()
        except:
            return False
    
    def _convert_to_integer(self, series: pd.Series) -> pd.Series:
        """Convert series to integer type"""
        try:
            # Convert to numeric first, then to integer
            numeric_series = pd.to_numeric(series, errors='coerce')
            return numeric_series.astype('Int64')  # Nullable integer type
        except:
            return series
    
    def _is_float_series(self, series: pd.Series) -> bool:
        """Check if series contains float values"""
        try:
            pd.to_numeric(series, errors='raise')
            return True
        except:
            return False
    
    def _convert_to_float(self, series: pd.Series) -> pd.Series:
        """Convert series to float type"""
        try:
            return pd.to_numeric(series, errors='coerce')
        except:
            return series
    
    def _is_datetime_series(self, series: pd.Series) -> bool:
        """Check if series contains datetime-like values"""
        # Sample a few values to test
        sample_size = min(10, len(series))
        sample_values = series.head(sample_size)
        
        datetime_count = 0
        for val in sample_values:
            if self._is_datetime_string(str(val)):
                datetime_count += 1
        
        # If most values look like dates, consider it a datetime series
        return datetime_count / sample_size >= 0.7
    
    def _is_datetime_string(self, value: str) -> bool:
        """Check if a string value looks like a datetime"""
        if not isinstance(value, str):
            return False
        
        # Common datetime patterns
        datetime_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # M/D/YY or MM/DD/YYYY
        ]
        
        for pattern in datetime_patterns:
            if re.search(pattern, value):
                return True
        
        # Try pandas datetime parsing
        try:
            pd.to_datetime(value)
            return True
        except:
            return False
    
    def _convert_to_datetime(self, series: pd.Series) -> pd.Series:
        """Convert series to datetime type"""
        try:
            return pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
        except:
            return series
    
    def _should_be_categorical(self, series: pd.Series) -> bool:
        """Determine if a series should be converted to categorical type"""
        if series.dtype != 'object':
            return False
        
        # Convert to categorical if:
        # 1. Number of unique values is less than 50% of total values
        # 2. Series has more than 10 values
        # 3. Number of unique values is less than 100
        
        unique_count = series.nunique()
        total_count = len(series)
        
        return (
            total_count > 10 and
            unique_count < min(100, total_count * 0.5)
        )
    
    def get_type_report(self, df: pd.DataFrame) -> str:
        """
        Generate a report of current data types in the DataFrame
        
        Args:
            df: Input DataFrame
            
        Returns:
            Formatted string report
        """
        if df.empty:
            return "❌ DataFrame is empty"
        
        report = [
            f"📊 Data Types Report",
            f"Total columns: {len(df.columns)}",
            f"Total rows: {len(df)}",
            f"",
            f"Column types:"
        ]
        
        # Group columns by data type
        type_groups = {}
        for column in df.columns:
            dtype = str(df[column].dtype)
            if dtype not in type_groups:
                type_groups[dtype] = []
            type_groups[dtype].append(column)
        
        for dtype, columns in sorted(type_groups.items()):
            report.append(f"  {dtype}: {len(columns)} columns")
            for col in columns[:5]:  # Show first 5 columns
                null_count = df[col].isnull().sum()
                null_pct = (null_count / len(df) * 100) if len(df) > 0 else 0
                report.append(f"    • {col} ({null_count} nulls, {null_pct:.1f}%)")
            
            if len(columns) > 5:
                report.append(f"    ... and {len(columns) - 5} more")
        
        return "\n".join(report)
    
    def suggest_type_improvements(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Suggest type improvements for the DataFrame
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with column names and suggested type changes
        """
        suggestions = {}
        
        for column in df.columns:
            current_type = str(df[column].dtype)
            suggested_type, _ = self._detect_and_convert_type(df[column])
            
            if suggested_type != current_type:
                suggestions[column] = f"Current: {current_type} → Suggested: {suggested_type}"
        
        return suggestions
