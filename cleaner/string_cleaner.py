"""
String Cleaning Module
Provides functions for common string manipulations like trimming and case changes.
"""

import pandas as pd
from typing import Tuple, Dict, Any

class StringCleaner:
    """A class to handle common string cleaning operations."""
    
    def __init__(self, logger):
        self.logger = logger

    def trim_whitespace(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Trims leading and trailing whitespace from all string columns.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (processed DataFrame, statistics)
        """
        result_df = df.copy()
        string_columns = result_df.select_dtypes(include=['object', 'string']).columns
        
        if len(string_columns) == 0:
            self.logger.info("No string columns found to trim whitespace from.")
            return result_df, {}

        columns_trimmed = []
        for col in string_columns:
            # Check if there is anything to trim before applying to avoid unnecessary computation
            if result_df[col].astype(str).str.contains(r'(^\s+|\s+$)').any():
                result_df[col] = result_df[col].astype(str).str.strip()
                columns_trimmed.append(col)
        
        if columns_trimmed:
            self.logger.info(f"Trimmed whitespace from {len(columns_trimmed)} columns: {', '.join(columns_trimmed)}")
        else:
            self.logger.info("No columns required whitespace trimming.")

        return result_df, {'columns_trimmed': columns_trimmed}

    def change_case(self, df: pd.DataFrame, case_option: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Changes the case of all string columns.
        
        Args:
            df: Input DataFrame
            case_option: One of 'lower', 'upper', 'title'
            
        Returns:
            Tuple of (processed DataFrame, statistics)
        """
        case_option = case_option.lower()
        if case_option not in ['lower', 'upper', 'title']:
            self.logger.warning(f"Invalid case option '{case_option}'. Skipping case change.")
            return df, {}

        result_df = df.copy()
        string_columns = result_df.select_dtypes(include=['object', 'string']).columns

        if len(string_columns) == 0:
            self.logger.info("No string columns found to change case.")
            return result_df, {}

        for col in string_columns:
            if case_option == 'lower':
                result_df[col] = result_df[col].astype(str).str.lower()
            elif case_option == 'upper':
                result_df[col] = result_df[col].astype(str).str.upper()
            elif case_option == 'title':
                result_df[col] = result_df[col].astype(str).str.title()
        
        self.logger.info(f"Changed case to '{case_option}' for {len(string_columns)} string columns.")
        
        return result_df, {'case_changed_to': case_option, 'columns_affected': list(string_columns)} 