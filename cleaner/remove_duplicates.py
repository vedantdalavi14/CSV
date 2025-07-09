"""
Duplicate Row Removal Module
"""

import pandas as pd
from typing import Tuple, Dict, Any

class DuplicateRemover:
    """Handles the removal of duplicate rows from a DataFrame."""
    
    def __init__(self, logger):
        self.logger = logger
    
    def remove_duplicates(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Removes complete duplicate rows from the DataFrame.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (DataFrame with duplicates removed, statistics dictionary)
        """
        if df.empty:
            self.logger.warning("DataFrame is empty, skipping duplicate removal.")
            return df, {}
            
        original_rows = len(df)
        result_df = df.drop_duplicates(keep='first').reset_index(drop=True)
        rows_removed = original_rows - len(result_df)
        
        stats = {
            'rows_removed': rows_removed,
            'original_rows': original_rows,
            'final_rows': len(result_df)
        }
        
        if rows_removed > 0:
            self.logger.info(f"Removed {rows_removed} duplicate rows.")
        else:
            self.logger.info("No duplicate rows found.")
            
        return result_df, stats 