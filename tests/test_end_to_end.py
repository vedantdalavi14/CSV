"""
End-to-end integration tests for the Smart CSV Cleaner
Tests the complete pipeline from CLI input to output files
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
from pathlib import Path
from click.testing import CliRunner

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli import clean_csv
from main import CSVCleaner
from utils.logger import setup_test_logger


class TestEndToEnd:
    """End-to-end integration tests"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def sample_messy_csv(self, temp_dir):
        """Create a sample messy CSV file for testing"""
        # Create messy data with various issues
        np.random.seed(42)
        
        data = {
            'First Name ': ['John', 'Jane', 'Bob', '', 'Alice', 'Charlie', 'Diana'],
            'LAST_NAME': ['Doe', 'Smith', 'Johnson', 'Williams', 'Brown', 'Davis', 'Miller'],
            'Age (years)': [25, 30, np.nan, 35, 28, 150, 22],  # Has missing and outlier
            'Email@Address': ['john@email.com', 'jane@email.com', None, 'williams@email.com', 
                             'alice@email.com', 'charlie@email.com', 'diana@email.com'],
            'Salary $$$': [50000, 60000, 55000, np.nan, 52000, 1000000, 48000],  # Has missing and outlier
            '  Phone Number  ': ['123-456-7890', '987-654-3210', '555-123-4567', 
                               '444-555-6666', '', '222-333-4444', '111-222-3333'],
            'Department': ['IT', 'HR', 'IT', 'Finance', 'IT', 'HR', np.nan],
            'Start Date': ['2020-01-15', '2019-06-20', '2021-03-10', '2018-12-05', 
                          '2022-02-28', '2020-11-18', '2021-08-03'],
            'Active': ['true', 'false', 'TRUE', 'FALSE', '1', '0', 'yes']
        }
        
        df = pd.DataFrame(data)
        csv_path = os.path.join(temp_dir, 'messy_data.csv')
        df.to_csv(csv_path, index=False)
        
        return csv_path
    
    @pytest.fixture
    def clean_csv_no_issues(self, temp_dir):
        """Create a clean CSV file with no issues"""
        data = {
            'first_name': ['John', 'Jane', 'Bob'],
            'last_name': ['Doe', 'Smith', 'Johnson'],
            'age': [25, 30, 35],
            'email': ['john@email.com', 'jane@email.com', 'bob@email.com']
        }
        
        df = pd.DataFrame(data)
        csv_path = os.path.join(temp_dir, 'clean_data.csv')
        df.to_csv(csv_path, index=False)
        
        return csv_path
    
    def test_cli_flags_only(self, sample_messy_csv, temp_dir):
        """Test CLI with traditional flags only"""
        runner = CliRunner()
        
        output_file = os.path.join(temp_dir, 'output.csv')
        
        result = runner.invoke(clean_csv, [
            sample_messy_csv,
            '--fix-names',
            '--fix-missing', 'mean',
            '--drop-outliers', 'zscore',
            '--standardize-types',
            '--output', output_file,
            '--log', os.path.join(temp_dir, 'test.log')
        ])
        
        assert result.exit_code == 0
        assert 'CSV cleaning completed successfully' in result.output
        assert os.path.exists(output_file)
        
        # Verify the output
        result_df = pd.read_csv(output_file)
        
        # Check that columns were cleaned
        expected_columns = ['first_name', 'last_name', 'age_years', 'emailaddress', 
                          'salary', 'phone_number', 'department', 'start_date', 'active']
        assert all(col.replace('_', '').replace('years', '').replace('address', '') in 
                  ''.join(expected_columns) or col in expected_columns 
                  for col in result_df.columns)
        
        # Check that outliers were removed (should have fewer rows)
        original_df = pd.read_csv(sample_messy_csv)
        assert len(result_df) <= len(original_df)
    
    def test_nlp_commands_only(self, sample_messy_csv, temp_dir):
        """Test CLI with natural language commands only"""
        runner = CliRunner()
        
        output_file = os.path.join(temp_dir, 'output_nlp.csv')
        
        result = runner.invoke(clean_csv, [
            sample_messy_csv,
            'fix column names and remove outliers and fill missing with median',
            '--output', output_file,
            '--log', os.path.join(temp_dir, 'test_nlp.log')
        ])
        
        assert result.exit_code == 0
        assert 'CSV cleaning completed successfully' in result.output
        assert os.path.exists(output_file)
        
        # Verify that operations were applied
        result_df = pd.read_csv(output_file)
        
        # Should have cleaned column names
        for col in result_df.columns:
            assert col.islower()
            assert ' ' not in col
    
    def test_mixed_flags_and_nlp(self, sample_messy_csv, temp_dir):
        """Test CLI with both flags and natural language (flags should take precedence)"""
        runner = CliRunner()
        
        output_file = os.path.join(temp_dir, 'output_mixed.csv')
        
        result = runner.invoke(clean_csv, [
            sample_messy_csv,
            'fill missing with mode',  # NLP suggests mode
            '--fix-missing', 'mean',   # Flag suggests mean (should win)
            '--fix-names',
            '--output', output_file,
            '--log', os.path.join(temp_dir, 'test_mixed.log')
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(output_file)
        
        # Verify log shows that mean was used (flag precedence)
        log_file = os.path.join(temp_dir, 'test_mixed.log')
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        # Should mention mean strategy was used
        assert 'mean' in log_content.lower()
    
    def test_excel_export(self, sample_messy_csv, temp_dir):
        """Test Excel export functionality"""
        runner = CliRunner()
        
        output_file = os.path.join(temp_dir, 'output.xlsx')
        
        result = runner.invoke(clean_csv, [
            sample_messy_csv,
            '--fix-names',
            '--excel',
            '--output', output_file,
            '--log', os.path.join(temp_dir, 'test_excel.log')
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(output_file)
        
        # Verify Excel file can be read
        result_df = pd.read_excel(output_file, sheet_name='Cleaned Data')
        assert len(result_df) > 0
    
    def test_large_file_performance(self, temp_dir):
        """Test performance with larger CSV file"""
        # Create a larger dataset
        np.random.seed(42)
        size = 5000
        
        data = {
            'id': range(size),
            'name': [f'Person_{i}' for i in range(size)],
            'value': np.random.normal(100, 20, size),
            'category': np.random.choice(['A', 'B', 'C', None], size, p=[0.3, 0.3, 0.3, 0.1]),
            'score': np.concatenate([np.random.normal(50, 10, size-100), np.random.normal(200, 50, 100)])  # Some outliers
        }
        
        df = pd.DataFrame(data)
        large_csv = os.path.join(temp_dir, 'large_data.csv')
        df.to_csv(large_csv, index=False)
        
        runner = CliRunner()
        output_file = os.path.join(temp_dir, 'large_output.csv')
        
        result = runner.invoke(clean_csv, [
            large_csv,
            'standardize data types and remove outliers',
            '--output', output_file,
            '--log', os.path.join(temp_dir, 'large_test.log')
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(output_file)
        
        # Verify processing completed
        result_df = pd.read_csv(output_file)
        assert len(result_df) > 0
    
    def test_invalid_input_file(self):
        """Test handling of invalid input file"""
        runner = CliRunner()
        
        result = runner.invoke(clean_csv, [
            'nonexistent_file.csv',
            '--fix-names'
        ])
        
        assert result.exit_code != 0
        assert 'Error' in result.output
    
    def test_invalid_output_directory(self, sample_messy_csv):
        """Test handling of invalid output directory"""
        runner = CliRunner()
        
        # Try to write to a path that doesn't exist and can't be created
        invalid_output = '/root/nonexistent/output.csv'
        
        result = runner.invoke(clean_csv, [
            sample_messy_csv,
            '--fix-names',
            '--output', invalid_output
        ])
        
        # Should handle gracefully (might succeed if directory can be created)
        # or fail with appropriate error message
        if result.exit_code != 0:
            assert 'Error' in result.output
    
    def test_empty_csv_file(self, temp_dir):
        """Test handling of empty CSV file"""
        empty_csv = os.path.join(temp_dir, 'empty.csv')
        
        # Create empty CSV
        with open(empty_csv, 'w') as f:
            f.write('')
        
        runner = CliRunner()
        
        result = runner.invoke(clean_csv, [
            empty_csv,
            '--fix-names'
        ])
        
        assert result.exit_code != 0
        assert 'Error' in result.output
    
    def test_csv_with_only_headers(self, temp_dir):
        """Test CSV file with only headers (no data rows)"""
        headers_only_csv = os.path.join(temp_dir, 'headers_only.csv')
        
        df = pd.DataFrame(columns=['Name', 'Age', 'Email'])
        df.to_csv(headers_only_csv, index=False)
        
        runner = CliRunner()
        output_file = os.path.join(temp_dir, 'headers_output.csv')
        
        result = runner.invoke(clean_csv, [
            headers_only_csv,
            '--fix-names',
            '--output', output_file
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(output_file)
        
        # Should still clean column names even with no data
        result_df = pd.read_csv(output_file)
        expected_columns = ['name', 'age', 'email']
        assert list(result_df.columns) == expected_columns
    
    def test_verbose_output(self, sample_messy_csv, temp_dir):
        """Test verbose output option"""
        runner = CliRunner()
        
        output_file = os.path.join(temp_dir, 'verbose_output.csv')
        
        result = runner.invoke(clean_csv, [
            sample_messy_csv,
            '--fix-names',
            '--verbose',
            '--output', output_file,
            '--log', os.path.join(temp_dir, 'verbose.log')
        ])
        
        assert result.exit_code == 0
        # In verbose mode, should see more detailed output
        # The exact content depends on logging configuration
    
    def test_no_preview_option(self, sample_messy_csv, temp_dir):
        """Test disabling preview output"""
        runner = CliRunner()
        
        output_file = os.path.join(temp_dir, 'no_preview_output.csv')
        
        result = runner.invoke(clean_csv, [
            sample_messy_csv,
            '--fix-names',
            '--no-preview',
            '--output', output_file
        ])
        
        assert result.exit_code == 0
        # Should not show preview table in output
        assert 'Preview of cleaned data' not in result.output
    
    def test_default_output_filename(self, sample_messy_csv, temp_dir):
        """Test default output filename generation"""
        # Copy the messy CSV to temp_dir so default output is in same directory
        import shutil
        local_csv = os.path.join(temp_dir, 'local_messy.csv')
        shutil.copy(sample_messy_csv, local_csv)
        
        runner = CliRunner()
        
        result = runner.invoke(clean_csv, [
            local_csv,
            '--fix-names'
        ])
        
        assert result.exit_code == 0
        
        # Should create a file with _cleaned suffix
        expected_output = os.path.join(temp_dir, 'local_messy_cleaned.csv')
        assert os.path.exists(expected_output)
    
    def test_custom_zscore_threshold(self, sample_messy_csv, temp_dir):
        """Test custom Z-score threshold for outlier detection"""
        runner = CliRunner()
        
        output_file = os.path.join(temp_dir, 'custom_zscore.csv')
        
        result = runner.invoke(clean_csv, [
            sample_messy_csv,
            '--drop-outliers', 'zscore',
            '--zscore-threshold', '2.0',  # More strict threshold
            '--output', output_file
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(output_file)
        
        # With stricter threshold, might remove more outliers
        result_df = pd.read_csv(output_file)
        original_df = pd.read_csv(sample_messy_csv)
        
        # Should have same or fewer rows due to outlier removal
        assert len(result_df) <= len(original_df)
    
    def test_integration_with_cleaner_class(self, sample_messy_csv, temp_dir):
        """Test direct integration with CSVCleaner class"""
        logger = setup_test_logger()
        cleaner = CSVCleaner(logger)
        
        output_file = os.path.join(temp_dir, 'direct_integration.csv')
        
        result = cleaner.process_csv(
            input_file=sample_messy_csv,
            natural_command='fix column names and standardize types',
            fix_missing='median',
            output=output_file,
            preview=False
        )
        
        assert result['success'] == True
        assert result['error'] is None
        assert os.path.exists(result['output_file'])
        assert len(result['summary']) > 0
    
    def test_log_file_creation(self, sample_messy_csv, temp_dir):
        """Test that log files are created correctly"""
        runner = CliRunner()
        
        log_file = os.path.join(temp_dir, 'custom.log')
        output_file = os.path.join(temp_dir, 'logged_output.csv')
        
        result = runner.invoke(clean_csv, [
            sample_messy_csv,
            '--fix-names',
            '--log', log_file,
            '--output', output_file
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(log_file)
        
        # Verify log content
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        assert 'Smart CSV Cleaner' in log_content
        assert 'Session started' in log_content
    
    def test_clean_data_no_changes_needed(self, clean_csv_no_issues, temp_dir):
        """Test processing already clean data"""
        runner = CliRunner()
        
        output_file = os.path.join(temp_dir, 'already_clean_output.csv')
        
        result = runner.invoke(clean_csv, [
            clean_csv_no_issues,
            '--fix-names',
            '--fix-missing', 'mean',
            '--drop-outliers', 'zscore',
            '--standardize-types',
            '--output', output_file
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(output_file)
        
        # Should complete successfully even if no changes needed
        assert 'CSV cleaning completed successfully' in result.output
        
        # Output should be similar to input
        original_df = pd.read_csv(clean_csv_no_issues)
        result_df = pd.read_csv(output_file)
        
        assert len(result_df) == len(original_df)


if __name__ == '__main__':
    pytest.main([__file__])
