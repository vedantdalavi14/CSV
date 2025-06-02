"""
Test cases for the column name fixing functionality
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cleaner.fix_names import ColumnNameFixer
from utils.logger import setup_test_logger


class TestColumnNameFixer:
    """Test cases for ColumnNameFixer class"""
    
    @pytest.fixture
    def fixer(self):
        """Create a ColumnNameFixer instance for testing"""
        logger = setup_test_logger()
        return ColumnNameFixer(logger)
    
    @pytest.fixture
    def sample_df_messy_names(self):
        """Create a DataFrame with messy column names"""
        return pd.DataFrame({
            'First Name ': [1, 2, 3],
            'LAST_NAME': [4, 5, 6],
            'Age (years)': [7, 8, 9],
            'Email@Address': [10, 11, 12],
            'Phone # Number': [13, 14, 15],
            'Salary $$$': [16, 17, 18],
            '  Spaces  ': [19, 20, 21],
            '123Numbers': [22, 23, 24],
            '': [25, 26, 27],  # Empty column name
            'Column-With-Dashes': [28, 29, 30]
        })
    
    def test_fix_simple_names(self, fixer):
        """Test fixing simple column name issues"""
        df = pd.DataFrame({
            'First Name': [1, 2, 3],
            'LAST NAME': [4, 5, 6],
            'Age': [7, 8, 9]
        })
        
        result_df, changes = fixer.fix_column_names(df)
        
        expected_columns = ['first_name', 'last_name', 'age']
        assert list(result_df.columns) == expected_columns
        assert len(changes) == 2  # First Name and LAST NAME should change
        assert 'First Name' in changes
        assert 'LAST NAME' in changes
    
    def test_fix_special_characters(self, fixer):
        """Test removal of special characters"""
        df = pd.DataFrame({
            'Email@Address': [1, 2, 3],
            'Phone#Number': [4, 5, 6],
            'Salary$$$': [7, 8, 9],
            'Weight(lbs)': [10, 11, 12]
        })
        
        result_df, changes = fixer.fix_column_names(df)
        
        expected_columns = ['emailaddress', 'phonenumber', 'salary', 'weightlbs']
        assert list(result_df.columns) == expected_columns
        assert len(changes) == 4
    
    def test_fix_whitespace_issues(self, fixer):
        """Test handling of whitespace issues"""
        df = pd.DataFrame({
            '  Leading Spaces': [1, 2, 3],
            'Trailing Spaces  ': [4, 5, 6],
            '  Both Sides  ': [7, 8, 9],
            'Multiple   Spaces': [10, 11, 12]
        })
        
        result_df, changes = fixer.fix_column_names(df)
        
        expected_columns = ['leading_spaces', 'trailing_spaces', 'both_sides', 'multiple_spaces']
        assert list(result_df.columns) == expected_columns
        assert len(changes) == 4
    
    def test_unique_name_generation(self, fixer):
        """Test handling of duplicate column names"""
        df = pd.DataFrame({
            'Name': [1, 2, 3],
            'name': [4, 5, 6],
            'NAME': [7, 8, 9],
            'Name ': [10, 11, 12]
        })
        
        result_df, changes = fixer.fix_column_names(df)
        
        # Should generate unique names
        columns = list(result_df.columns)
        assert len(set(columns)) == len(columns)  # All unique
        assert 'name' in columns
        assert 'name_1' in columns or 'name_2' in columns  # Some variation
    
    def test_numeric_start_handling(self, fixer):
        """Test handling of column names starting with numbers"""
        df = pd.DataFrame({
            '123abc': [1, 2, 3],
            '456def': [4, 5, 6],
            '789': [7, 8, 9]
        })
        
        result_df, changes = fixer.fix_column_names(df)
        
        columns = list(result_df.columns)
        for col in columns:
            assert not col[0].isdigit(), f"Column '{col}' starts with a digit"
        
        # Should have 'col_' prefix
        assert any(col.startswith('col_') for col in columns)
    
    def test_empty_column_names(self, fixer):
        """Test handling of empty column names"""
        df = pd.DataFrame({
            '': [1, 2, 3],
            ' ': [4, 5, 6],
            '   ': [7, 8, 9],
            'Valid': [10, 11, 12]
        })
        
        result_df, changes = fixer.fix_column_names(df)
        
        columns = list(result_df.columns)
        
        # No empty columns should remain
        for col in columns:
            assert col.strip() != '', f"Column '{col}' is empty or whitespace"
        
        # Should have unnamed_column or similar
        unnamed_cols = [col for col in columns if 'unnamed' in col]
        assert len(unnamed_cols) >= 1
    
    def test_complex_messy_names(self, fixer, sample_df_messy_names):
        """Test fixing very messy column names"""
        result_df, changes = fixer.fix_column_names(sample_df_messy_names)
        
        columns = list(result_df.columns)
        
        # Check that all columns are properly formatted
        for col in columns:
            # Should be lowercase
            assert col == col.lower(), f"Column '{col}' is not lowercase"
            
            # Should not start with digit
            assert not col[0].isdigit(), f"Column '{col}' starts with digit"
            
            # Should not have special characters (except underscores)
            import re
            assert re.match(r'^[a-z][a-z0-9_]*$', col), f"Column '{col}' has invalid format"
            
            # Should not have leading/trailing underscores
            assert not col.startswith('_'), f"Column '{col}' starts with underscore"
            assert not col.endswith('_'), f"Column '{col}' ends with underscore"
        
        # Should have changes for messy names
        assert len(changes) > 0
    
    def test_already_clean_names(self, fixer):
        """Test that already clean names are not changed"""
        df = pd.DataFrame({
            'first_name': [1, 2, 3],
            'last_name': [4, 5, 6],
            'age': [7, 8, 9],
            'email': [10, 11, 12]
        })
        
        result_df, changes = fixer.fix_column_names(df)
        
        # No changes should be made
        assert len(changes) == 0
        assert list(result_df.columns) == list(df.columns)
    
    def test_empty_dataframe(self, fixer):
        """Test handling of empty DataFrame"""
        df = pd.DataFrame()
        
        result_df, changes = fixer.fix_column_names(df)
        
        assert result_df.empty
        assert len(changes) == 0
    
    def test_single_column(self, fixer):
        """Test with single column DataFrame"""
        df = pd.DataFrame({
            'Messy Column Name!!!': [1, 2, 3, 4, 5]
        })
        
        result_df, changes = fixer.fix_column_names(df)
        
        assert len(result_df.columns) == 1
        assert list(result_df.columns)[0] == 'messy_column_name'
        assert len(changes) == 1
    
    def test_validation_method(self, fixer):
        """Test the column name validation method"""
        df = pd.DataFrame({
            'Good_Name': [1, 2, 3],
            'Bad Name!': [4, 5, 6],
            '  Whitespace  ': [7, 8, 9],
            '': [10, 11, 12],
            '123Start': [13, 14, 15],
            'duplicate': [16, 17, 18],
            'duplicate': [19, 20, 21]
        })
        
        issues = fixer.validate_column_names(df)
        
        assert len(issues['special_chars']) > 0
        assert len(issues['whitespace']) > 0
        assert len(issues['empty']) > 0
        assert len(issues['numeric_start']) > 0
        assert len(issues['duplicates']) > 0


if __name__ == '__main__':
    pytest.main([__file__])
