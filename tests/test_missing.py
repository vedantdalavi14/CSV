"""
Test cases for the missing data handling functionality
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cleaner.fix_missing import MissingDataHandler
from utils.logger import setup_test_logger


class TestMissingDataHandler:
    """Test cases for MissingDataHandler class"""
    
    @pytest.fixture
    def handler(self):
        """Create a MissingDataHandler instance for testing"""
        logger = setup_test_logger()
        return MissingDataHandler(logger)
    
    @pytest.fixture
    def sample_df_with_missing(self):
        """Create a DataFrame with missing values"""
        return pd.DataFrame({
            'numeric_col': [1.0, 2.0, np.nan, 4.0, 5.0, np.nan, 7.0],
            'text_col': ['a', 'b', None, 'd', 'e', 'f', 'g'],
            'mixed_col': [1, 'text', np.nan, 4, 'more_text', np.nan, 7],
            'no_missing': [1, 2, 3, 4, 5, 6, 7],
            'all_missing': [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        })
    
    @pytest.fixture
    def sample_df_no_missing(self):
        """Create a DataFrame without missing values"""
        return pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['a', 'b', 'c', 'd', 'e'],
            'col3': [1.1, 2.2, 3.3, 4.4, 5.5]
        })
    
    def test_fill_missing_mean(self, handler, sample_df_with_missing):
        """Test filling missing values with mean"""
        result_df, stats = handler.handle_missing_data(sample_df_with_missing, 'mean')
        
        # Check that numeric column was filled
        assert not result_df['numeric_col'].isnull().any()
        
        # Mean should be calculated correctly
        original_mean = sample_df_with_missing['numeric_col'].mean()
        filled_values = result_df['numeric_col'].iloc[[2, 5]]  # Previously missing indices
        assert all(val == original_mean for val in filled_values)
        
        # Text columns should not be affected by mean strategy
        assert result_df['text_col'].isnull().sum() == sample_df_with_missing['text_col'].isnull().sum()
        
        # Check statistics
        assert stats['strategy'] == 'mean'
        assert stats['changes_made'] == True
        assert 'numeric_col' in stats['columns_filled']
    
    def test_fill_missing_median(self, handler, sample_df_with_missing):
        """Test filling missing values with median"""
        result_df, stats = handler.handle_missing_data(sample_df_with_missing, 'median')
        
        # Check that numeric column was filled
        assert not result_df['numeric_col'].isnull().any()
        
        # Median should be calculated correctly
        original_median = sample_df_with_missing['numeric_col'].median()
        filled_values = result_df['numeric_col'].iloc[[2, 5]]  # Previously missing indices
        assert all(val == original_median for val in filled_values)
        
        assert stats['strategy'] == 'median'
        assert 'numeric_col' in stats['columns_filled']
    
    def test_fill_missing_mode(self, handler):
        """Test filling missing values with mode"""
        # Create a DataFrame where mode makes sense
        df = pd.DataFrame({
            'category': ['A', 'B', 'A', 'A', np.nan, 'B', np.nan],
            'numeric': [1, 1, 1, 2, np.nan, 2, np.nan]
        })
        
        result_df, stats = handler.handle_missing_data(df, 'mode')
        
        # Check that missing values were filled with mode
        assert not result_df['category'].isnull().any()
        assert not result_df['numeric'].isnull().any()
        
        # Mode should be 'A' for category and 1 for numeric
        filled_categories = result_df['category'].iloc[[4, 6]]
        filled_numerics = result_df['numeric'].iloc[[4, 6]]
        
        assert all(val == 'A' for val in filled_categories)
        assert all(val == 1 for val in filled_numerics)
        
        assert stats['strategy'] == 'mode'
    
    def test_drop_missing(self, handler, sample_df_with_missing):
        """Test dropping rows with missing values"""
        original_length = len(sample_df_with_missing)
        
        result_df, stats = handler.handle_missing_data(sample_df_with_missing, 'drop')
        
        # Should have fewer rows
        assert len(result_df) < original_length
        
        # Should have no missing values
        assert not result_df.isnull().any().any()
        
        # Check statistics
        assert stats['strategy'] == 'drop'
        assert stats['changes_made'] == True
        assert stats['rows_dropped'] > 0
        assert stats['original_rows'] == original_length
        assert stats['final_rows'] == len(result_df)
    
    def test_no_missing_data(self, handler, sample_df_no_missing):
        """Test handling DataFrame with no missing data"""
        result_df, stats = handler.handle_missing_data(sample_df_no_missing, 'mean')
        
        # DataFrame should be unchanged
        pd.testing.assert_frame_equal(result_df, sample_df_no_missing)
        
        # No changes should be recorded
        assert stats['changes_made'] == False
    
    def test_empty_dataframe(self, handler):
        """Test handling empty DataFrame"""
        df = pd.DataFrame()
        
        result_df, stats = handler.handle_missing_data(df, 'mean')
        
        assert result_df.empty
        assert len(stats) == 0
    
    def test_invalid_strategy(self, handler, sample_df_with_missing):
        """Test with invalid strategy"""
        result_df, stats = handler.handle_missing_data(sample_df_with_missing, 'invalid')
        
        # Should return original DataFrame
        pd.testing.assert_frame_equal(result_df, sample_df_with_missing)
        assert len(stats) == 0
    
    def test_all_missing_column(self, handler):
        """Test handling column with all missing values"""
        df = pd.DataFrame({
            'all_missing': [np.nan, np.nan, np.nan],
            'normal': [1, 2, 3]
        })
        
        result_df, stats = handler.handle_missing_data(df, 'mean')
        
        # All missing column should remain missing for numeric strategies
        assert result_df['all_missing'].isnull().all()
        
        # Normal column should be unchanged
        assert not result_df['normal'].isnull().any()
    
    def test_mixed_data_types_mean(self, handler):
        """Test mean strategy with mixed data types"""
        df = pd.DataFrame({
            'numeric_int': [1, 2, np.nan, 4, 5],
            'numeric_float': [1.1, 2.2, np.nan, 4.4, 5.5],
            'text': ['a', 'b', None, 'd', 'e'],
            'boolean': [True, False, np.nan, True, False]  # This might be tricky
        })
        
        result_df, stats = handler.handle_missing_data(df, 'mean')
        
        # Only numeric columns should be filled
        assert not result_df['numeric_int'].isnull().any()
        assert not result_df['numeric_float'].isnull().any()
        
        # Text column should still have missing values
        assert result_df['text'].isnull().sum() > 0
        
        # Check that appropriate columns were processed
        filled_columns = stats.get('columns_filled', [])
        assert 'numeric_int' in filled_columns
        assert 'numeric_float' in filled_columns
        assert 'text' not in filled_columns
    
    def test_analyze_missing_data(self, handler, sample_df_with_missing):
        """Test missing data analysis functionality"""
        missing_info = handler._analyze_missing_data(sample_df_with_missing)
        
        assert 'total_missing' in missing_info
        assert 'columns_with_missing' in missing_info
        assert 'missing_percentages' in missing_info
        
        # Should detect missing values
        assert missing_info['total_missing'] > 0
        
        # Should identify columns with missing values
        expected_columns = ['numeric_col', 'text_col', 'mixed_col', 'all_missing']
        for col in expected_columns:
            if col != 'no_missing':  # This column has no missing values
                assert col in missing_info['columns_with_missing']
    
    def test_get_missing_data_report(self, handler, sample_df_with_missing):
        """Test missing data report generation"""
        report = handler.get_missing_data_report(sample_df_with_missing)
        
        assert isinstance(report, str)
        assert 'Missing Data Report' in report
        assert 'Total missing values' in report
    
    def test_get_missing_data_report_no_missing(self, handler, sample_df_no_missing):
        """Test missing data report with no missing values"""
        report = handler.get_missing_data_report(sample_df_no_missing)
        
        assert isinstance(report, str)
        assert 'No missing values found' in report
    
    def test_large_dataset_performance(self, handler):
        """Test performance with larger dataset"""
        # Create larger dataset with missing values
        np.random.seed(42)
        
        size = 10000
        df = pd.DataFrame({
            'col1': np.random.normal(50, 10, size),
            'col2': np.random.choice(['A', 'B', 'C', None], size, p=[0.3, 0.3, 0.3, 0.1]),
            'col3': np.random.uniform(0, 100, size)
        })
        
        # Introduce some missing values in col1 and col3
        missing_indices = np.random.choice(size, size // 20, replace=False)
        df.loc[missing_indices[:len(missing_indices)//2], 'col1'] = np.nan
        df.loc[missing_indices[len(missing_indices)//2:], 'col3'] = np.nan
        
        result_df, stats = handler.handle_missing_data(df, 'mean')
        
        # Should handle large dataset
        assert len(result_df) == len(df)
        assert stats['changes_made'] == True
    
    def test_mode_with_no_mode(self, handler):
        """Test mode strategy when column has no clear mode"""
        df = pd.DataFrame({
            'unique_values': [1, 2, 3, 4, np.nan],  # All different values
            'empty_mode': [np.nan, np.nan, np.nan, np.nan, np.nan]  # All missing
        })
        
        result_df, stats = handler.handle_missing_data(df, 'mode')
        
        # Should handle gracefully - might fill with first value or skip
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == len(df)


if __name__ == '__main__':
    pytest.main([__file__])
