"""
Column Name Fixing Module
Standardizes column names by removing special characters, normalizing case, etc.
"""

import pandas as pd
import re
from typing import Dict, Tuple
import logging


class ColumnNameFixer:
    """Handles column name standardization and cleaning"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def fix_column_names(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Fix column names by standardizing format
        
        Rules:
        - Strip whitespace
        - Convert to lowercase
        - Replace spaces with underscores
        - Remove special characters (keep only alphanumeric and underscores)
        - Ensure unique names
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (cleaned DataFrame, dictionary of name changes)
        """
        if df.empty:
            self.logger.warning("DataFrame is empty, skipping column name fixing")
            return df, {}
        
        original_columns = df.columns.tolist()
        name_changes = {}
        
        self.logger.info(f"Fixing column names for {len(original_columns)} columns")
        
        # Apply cleaning rules to each column name
        cleaned_names = []
        for col in original_columns:
            original_name = str(col)
            cleaned_name = self._clean_single_name(original_name)
            
            if cleaned_name != original_name:
                name_changes[original_name] = cleaned_name
                self.logger.debug(f"Column renamed: '{original_name}' -> '{cleaned_name}'")
            
            cleaned_names.append(cleaned_name)
        
        # Ensure unique column names
        unique_names = self._ensure_unique_names(cleaned_names)
        
        # Update name_changes if uniqueness required modifications
        for i, (original, cleaned) in enumerate(zip(original_columns, unique_names)):
            if str(original) != unique_names[i] and str(original) not in name_changes:
                name_changes[str(original)] = unique_names[i]
        
        # Apply new column names
        df.columns = unique_names
        
        if name_changes:
            self.logger.info(f"Successfully renamed {len(name_changes)} columns")
            for old, new in name_changes.items():
                self.logger.debug(f"  '{old}' -> '{new}'")
        else:
            self.logger.info("No column names needed fixing")
        
        return df, name_changes
    
    def _clean_single_name(self, name: str) -> str:
        """
        Clean a single column name according to standardization rules
        
        Args:
            name: Original column name
            
        Returns:
            Cleaned column name
        """
        # Convert to string and strip whitespace
        cleaned = str(name).strip()
        
        # Convert to lowercase
        cleaned = cleaned.lower()
        
        # Replace spaces and common separators with underscores
        cleaned = re.sub(r'[\s\-\.]+', '_', cleaned)
        
        # Remove special characters (keep only alphanumeric and underscores)
        cleaned = re.sub(r'[^a-z0-9_]', '', cleaned)
        
        # Remove multiple consecutive underscores
        cleaned = re.sub(r'_+', '_', cleaned)
        
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        
        # Ensure the name is not empty
        if not cleaned:
            cleaned = 'unnamed_column'
        
        # Ensure it doesn't start with a number (for better compatibility)
        if cleaned and cleaned[0].isdigit():
            cleaned = 'col_' + cleaned
        
        return cleaned
    
    def _ensure_unique_names(self, names: list) -> list:
        """
        Ensure all column names are unique by adding suffixes if needed
        
        Args:
            names: List of column names
            
        Returns:
            List of unique column names
        """
        unique_names = []
        name_counts = {}
        
        for name in names:
            original_name = name
            
            # Count occurrences
            if name in name_counts:
                name_counts[name] += 1
                name = f"{original_name}_{name_counts[name]}"
            else:
                name_counts[original_name] = 0
            
            unique_names.append(name)
        
        return unique_names
    
    def validate_column_names(self, df: pd.DataFrame) -> Dict[str, list]:
        """
        Validate column names and report potential issues
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        issues = {
            'duplicates': [],
            'special_chars': [],
            'whitespace': [],
            'empty': [],
            'numeric_start': []
        }
        
        columns = df.columns.tolist()
        
        # Check for duplicates
        seen = set()
        for col in columns:
            if col in seen:
                issues['duplicates'].append(col)
            seen.add(col)
        
        # Check for other issues
        for col in columns:
            col_str = str(col)
            
            # Check for special characters
            if re.search(r'[^a-zA-Z0-9_\s]', col_str):
                issues['special_chars'].append(col)
            
            # Check for leading/trailing whitespace
            if col_str != col_str.strip():
                issues['whitespace'].append(col)
            
            # Check for empty names
            if not col_str.strip():
                issues['empty'].append(col)
            
            # Check for names starting with numbers
            if col_str.strip() and col_str.strip()[0].isdigit():
                issues['numeric_start'].append(col)
        
        return issues
