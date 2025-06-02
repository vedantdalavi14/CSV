"""
Test cases for the outlier detection and removal functionality
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cleaner.drop_outliers import OutlierRemover
from utils.logger import setup_test_logger


class TestOutlierRemover:
    """Test cases for OutlierRemover class"""
    
    @pytest.fixture
    def remover(self):
        """Create an OutlierRemover instance for testing"""
        logger = setup_test_logger()
        return OutlierRemover(logger, zscore_threshold=3.0)
    
    @pytest.fixture
    def sample_df_with_outliers(self):
        """Create a DataFrame with known outliers"""
        np.random.seed(42)  # For reproducible tests
        
        # Create normal data
        normal_data = np.random.normal(50, 10, 100)
        
        # Add some outliers
        outliers = [100, 150, -20, -50, 200]
        
        all_data = np.concatenate([normal_data, outliers])
        
        df = pd.DataFrame({
            'value': all_data,
            'category': ['A'] * len(all_data),
            'text_col': ['text'] * len(all_data)  # Non-numeric column
        })
        
        return df
    
    @pytest.fixture
    def sample_df_no_outliers(self):
        """Create a DataFrame without outliers"""
        np.random.seed(42)
        
        df = pd.DataFrame({
            'normal_dist': np.random.normal(50, 5, 100),
            'uniform_dist': np.random.uniform(10, 20, 100),
            'text_col': ['text'] * 100
        })
        
        return df
    
    def test_zscore_outlier_removal(self, remover, sample_df_with_outliers):
        """Test Z-score based outlier removal"""
        original_length = len(sample_df_with_outliers)
        
        result_df, stats = remover.remove_outliers(sample_df_with_outliers, method='zscore')
        
        # Should remove some outliers
        assert len(result_df) < original_length
        assert stats['total_removed'] > 0
        assert stats['method'] == 'zscore'
        assert stats['original_rows'] == original_length
        assert stats['final_rows'] == len(result_df)
        
        # Check that numeric columns were analyzed
        assert stats['numeric_columns_analyzed'] > 0
        assert 'value' in stats['column_stats']
    
    def test_iqr_outlier_removal(self, remover, sample_df_with_outliers):
        """Test IQR based outlier removal"""
        original_length = len(sample_df_with_outliers)
        
        result_df, stats = remover.remove_outliers(sample_df_with_outliers, method='iqr')
        
        # Should remove some outliers
        assert len(result_df) < original_length
        assert stats['total_removed'] > 0
        assert stats['method'] == 'iqr'
        
        # Check IQR statistics
        value_stats = stats['column_stats']['value']
        assert 'Q1' in value_stats
        assert 'Q3' in value_stats
        assert 'IQR' in value_stats
        assert 'lower_bound' in value_stats
        assert 'upper_bound' in value_stats
    
    def test_no_outliers_detected(self, remover, sample_df_no_outliers):
        """Test with data that has no outliers"""
        result_df, stats = remover.remove_outliers(sample_df_no_outliers, method='zscore')
        
        # Should not remove any rows
        assert len(result_df) == len(sample_df_no_outliers)
        assert stats['total_removed'] == 0
        assert stats['removal_percentage'] == 0
    
    def test_only_numeric_columns_analyzed(self, remover):
        """Test that only numeric columns are analyzed for outliers"""
        df = pd.DataFrame({
            'text_col': ['a', 'b', 'c', 'd', 'e'],
            'category_col': ['cat1', 'cat2', 'cat1', 'cat2', 'cat1'],
            'boolean_col': [True, False, True, False, True]
        })
        
        result_df, stats = remover.remove_outliers(df, method='zscore')
        
        # No numeric columns, so no outliers removed
        assert len(result_df) == len(df)
        assert stats['total_removed'] == 0
        assert stats['numeric_columns_analyzed'] == 0
    
    def test_mixed_data_types(self, remover):
        """Test with mixed data types including numeric columns"""
        df = pd.DataFrame({
            'numeric_normal': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'numeric_with_outlier': [10, 11, 12, 13, 14, 15, 16, 17, 18, 1000],  # 1000 is outlier
            'text_col': ['text'] * 10,
            'category_col': ['A', 'B'] * 5
        })
        
        result_df, stats = remover.remove_outliers(df, method='zscore')
        
        # Should analyze only numeric columns
        assert stats['numeric_columns_analyzed'] == 2
        assert 'numeric_normal' in stats['column_stats']
        assert 'numeric_with_outlier' in stats['column_stats']
        assert 'text_col' not in stats['column_stats']
    
    def test_zscore_threshold_custom(self):
        """Test with custom Z-score threshold"""
        logger = setup_test_logger()
        remover = OutlierRemover(logger, zscore_threshold=2.0)  # More strict threshold
        
        # Create data with mild outliers
        df = pd.DataFrame({
            'values': [1, 2, 3, 4, 5, 6, 7, 8, 9, 15]  # 15 might be outlier with threshold 2.0
        })
        
        result_df, stats = remover.remove_outliers(df, method='zscore')
        
        # Check that the threshold was applied
        if stats['total_removed'] > 0:
            value_stats = stats['column_stats']['values']
            assert value_stats['threshold'] == 2.0
    
    def test_empty_dataframe(self, remover):
        """Test handling of empty DataFrame"""
        df = pd.DataFrame()
        
        result_df, stats = remover.remove_outliers(df, method='zscore')
        
        assert result_df.empty
        assert stats['total_removed'] == 0
    
    def test_single_row_dataframe(self, remover):
        """Test with single row DataFrame"""
        df = pd.DataFrame({'value': [42], 'text': ['hello']})
        
        result_df, stats = remover.remove_outliers(df, method='zscore')
        
        # Single row can't be an outlier
        assert len(result_df) == 1
        assert stats['total_removed'] == 0
    
    def test_invalid_method(self, remover):
        """Test with invalid outlier detection method"""
        df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})
        
        result_df, stats = remover.remove_outliers(df, method='invalid')
        
        # Should return original DataFrame
        assert len(result_df) == len(df)
        assert stats['total_removed'] == 0
    
    def test_detect_outliers_only(self, remover, sample_df_with_outliers):
        """Test outlier detection without removal"""
        outlier_info = remover.detect_outliers_only(sample_df_with_outliers, method='zscore')
        
        assert 'total_outliers_detected' in outlier_info
        assert 'method' in outlier_info
        assert 'column_details' in outlier_info
        assert outlier_info['total_outliers_detected'] > 0
    
    def test_get_outlier_report(self, remover, sample_df_with_outliers):
        """Test outlier report generation"""
        report = remover.get_outlier_report(sample_df_with_outliers, method='zscore')
        
        assert isinstance(report, str)
        assert 'ZSCORE' in report.upper()
        assert 'outlier' in report.lower()
    
    def test_outlier_report_no_outliers(self, remover, sample_df_no_outliers):
        """Test outlier report when no outliers exist"""
        report = remover.get_outlier_report(sample_df_no_outliers, method='zscore')
        
        assert isinstance(report, str)
        assert 'no outliers detected' in report.lower()
    
    def test_outlier_report_no_numeric_columns(self, remover):
        """Test outlier report with no numeric columns"""
        df = pd.DataFrame({'text': ['a', 'b', 'c']})
        
        report = remover.get_outlier_report(df, method='zscore')
        
        assert isinstance(report, str)
        assert 'no numeric columns' in report.lower()
    
    def test_large_dataset_performance(self, remover):
        """Test performance with larger dataset"""
        np.random.seed(42)
        
        # Create larger dataset
        normal_data = np.random.normal(100, 15, 10000)
        outliers = np.random.normal(300, 50, 100)  # Clear outliers
        all_data = np.concatenate([normal_data, outliers])
        
        df = pd.DataFrame({
            'values': all_data,
            'group': ['A'] * len(all_data)
        })
        
        result_df, stats = remover.remove_outliers(df, method='zscore')
        
        # Should handle large dataset
        assert stats['original_rows'] == len(df)
        assert isinstance(stats['total_removed'], int)
        assert stats['total_removed'] >= 0
    
    def test_multiple_numeric_columns(self, remover):
        """Test with multiple numeric columns having different outlier patterns"""
        np.random.seed(42)
        
        # Create arrays of equal length
        normal_data1 = np.random.normal(50, 5, 100)
        outliers1 = [150, 200]
        col1_data = np.concatenate([normal_data1, outliers1])
        
        normal_data2 = np.random.normal(20, 3, 101)
        outliers2 = [-50]
        col2_data = np.concatenate([normal_data2, outliers2])
        
        col3_data = np.random.normal(75, 8, 102)
        
        df = pd.DataFrame({
            'col1': col1_data,
            'col2': col2_data,
            'col3': col3_data,
            'text': ['text'] * 102
        })
        
        result_df, stats = remover.remove_outliers(df, method='iqr')
        
        # Should analyze all numeric columns
        assert stats['numeric_columns_analyzed'] == 3
        assert 'col1' in stats['column_stats']
        assert 'col2' in stats['column_stats'] 
        assert 'col3' in stats['column_stats']
        
        # Should remove some outliers
        assert stats['total_removed'] > 0


if __name__ == '__main__':
    pytest.main([__file__])
