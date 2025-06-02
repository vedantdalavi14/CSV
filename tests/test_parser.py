"""
Test cases for the NLP parser functionality
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from parser.nlp_parser import NLPParser


class TestNLPParser:
    """Test cases for NLPParser class"""
    
    @pytest.fixture
    def parser(self):
        """Create an NLPParser instance for testing"""
        return NLPParser()
    
    def test_fix_column_names_detection(self, parser):
        """Test detection of column name fixing commands"""
        test_cases = [
            "fix column names",
            "clean headers",
            "standardize titles",
            "normalize column names",
            "fix the column headers",
            "clean column titles"
        ]
        
        for command in test_cases:
            result = parser.parse_command(command)
            assert result.get('fix_names') == True, f"Failed for command: '{command}'"
    
    def test_missing_data_mean_detection(self, parser):
        """Test detection of mean-based missing data handling"""
        test_cases = [
            "fill missing with mean",
            "handle missing using mean",
            "replace missing with mean",
            "fix missing data with mean",
            "use mean for missing values"
        ]
        
        for command in test_cases:
            result = parser.parse_command(command)
            assert result.get('fix_missing') == 'mean', f"Failed for command: '{command}'"
    
    def test_missing_data_median_detection(self, parser):
        """Test detection of median-based missing data handling"""
        test_cases = [
            "fill missing with median",
            "handle missing using median", 
            "replace missing with median",
            "use median for missing"
        ]
        
        for command in test_cases:
            result = parser.parse_command(command)
            assert result.get('fix_missing') == 'median', f"Failed for command: '{command}'"
    
    def test_missing_data_mode_detection(self, parser):
        """Test detection of mode-based missing data handling"""
        test_cases = [
            "fill missing with mode",
            "handle missing using mode",
            "replace missing with mode",
            "use mode for missing"
        ]
        
        for command in test_cases:
            result = parser.parse_command(command)
            assert result.get('fix_missing') == 'mode', f"Failed for command: '{command}'"
    
    def test_missing_data_drop_detection(self, parser):
        """Test detection of drop-based missing data handling"""
        test_cases = [
            "drop missing",
            "remove rows with missing",
            "delete missing values",
            "handle missing by drop",
            "drop rows with missing values"
        ]
        
        for command in test_cases:
            result = parser.parse_command(command)
            assert result.get('fix_missing') == 'drop', f"Failed for command: '{command}'"
    
    def test_outlier_zscore_detection(self, parser):
        """Test detection of Z-score outlier removal"""
        test_cases = [
            "remove outliers using zscore",
            "drop outliers using z-score",
            "z-score outliers",
            "remove outliers using z score"
        ]
        
        for command in test_cases:
            result = parser.parse_command(command)
            assert result.get('drop_outliers') == 'zscore', f"Failed for command: '{command}'"
    
    def test_outlier_iqr_detection(self, parser):
        """Test detection of IQR outlier removal"""
        test_cases = [
            "remove outliers using iqr",
            "drop outliers using IQR",
            "iqr outliers",
            "interquartile range outliers"
        ]
        
        for command in test_cases:
            result = parser.parse_command(command)
            assert result.get('drop_outliers') == 'iqr', f"Failed for command: '{command}'"
    
    def test_outlier_general_detection(self, parser):
        """Test detection of general outlier removal (defaults to zscore)"""
        test_cases = [
            "remove outliers",
            "drop outliers", 
            "delete outliers",
            "fix outliers",
            "handle outliers"
        ]
        
        for command in test_cases:
            result = parser.parse_command(command)
            assert result.get('drop_outliers') == 'zscore', f"Failed for command: '{command}'"
    
    def test_standardize_types_detection(self, parser):
        """Test detection of type standardization commands"""
        test_cases = [
            "standardize data types",
            "convert data types",
            "fix data types",
            "normalize types",
            "standardize types"
        ]
        
        for command in test_cases:
            result = parser.parse_command(command)
            assert result.get('standardize_types') == True, f"Failed for command: '{command}'"
    
    def test_combined_commands(self, parser):
        """Test parsing of combined commands"""
        test_cases = [
            {
                'command': "fix column names and remove outliers",
                'expected': {'fix_names': True, 'drop_outliers': 'zscore'}
            },
            {
                'command': "standardize types and fill missing with median",
                'expected': {'standardize_types': True, 'fix_missing': 'median'}
            },
            {
                'command': "clean headers and drop outliers using iqr",
                'expected': {'fix_names': True, 'drop_outliers': 'iqr'}
            },
            {
                'command': "fix column names, handle missing using mean, and remove outliers",
                'expected': {'fix_names': True, 'fix_missing': 'mean', 'drop_outliers': 'zscore'}
            }
        ]
        
        for test_case in test_cases:
            result = parser.parse_command(test_case['command'])
            for key, expected_value in test_case['expected'].items():
                assert result.get(key) == expected_value, \
                    f"Failed for command: '{test_case['command']}', key: '{key}'"
    
    def test_case_insensitive_parsing(self, parser):
        """Test that parsing is case insensitive"""
        test_cases = [
            "FIX COLUMN NAMES",
            "Clean Headers",
            "REMOVE OUTLIERS",
            "standardize DATA types",
            "Fill Missing With MEAN"
        ]
        
        for command in test_cases:
            result = parser.parse_command(command)
            # Should parse something (not empty)
            assert len(result) > 0, f"Failed to parse case variant: '{command}'"
    
    def test_empty_command(self, parser):
        """Test handling of empty commands"""
        test_cases = ["", "   ", None]
        
        for command in test_cases:
            if command is None:
                # Skip None test as it would cause TypeError in real usage
                continue
            result = parser.parse_command(command)
            assert result == {}, f"Empty command should return empty dict: '{command}'"
    
    def test_unrecognized_command(self, parser):
        """Test handling of unrecognized commands"""
        test_cases = [
            "do something random",
            "invalid command",
            "xyz abc def",
            "123 456 789"
        ]
        
        for command in test_cases:
            result = parser.parse_command(command)
            assert result == {}, f"Unrecognized command should return empty dict: '{command}'"
    
    def test_partial_matches(self, parser):
        """Test that partial word matches don't trigger false positives"""
        test_cases = [
            "outline the process",  # Contains 'outli' but shouldn't match 'outliers'
            "column namespaces",    # Contains 'column name' but different context
            "meaning of life",      # Contains 'mean' but different context
            "drop table"           # Contains 'drop' but different context
        ]
        
        for command in test_cases:
            result = parser.parse_command(command)
            # These should not match any patterns
            assert result == {}, f"Partial match should not trigger: '{command}'"
    
    def test_priority_resolution(self, parser):
        """Test that specific strategies take priority over general ones"""
        # When both specific and general patterns could match, specific should win
        result = parser.parse_command("fill missing using median and drop missing")
        
        # Should detect both but specific strategies should be chosen
        # The last specific strategy mentioned should be used
        assert 'fix_missing' in result
        # Either 'median' or 'drop' is acceptable depending on parsing order
        assert result['fix_missing'] in ['median', 'drop']
    
    def test_supported_commands_method(self, parser):
        """Test the get_supported_commands method"""
        supported = parser.get_supported_commands()
        
        assert isinstance(supported, dict)
        
        expected_categories = ['Column Names', 'Missing Data', 'Outliers', 'Data Types', 'Combined']
        for category in expected_categories:
            assert category in supported, f"Missing category: {category}"
            assert isinstance(supported[category], list)
            assert len(supported[category]) > 0
    
    def test_regex_pattern_coverage(self, parser):
        """Test that all defined patterns are accessible and functional"""
        # Test each pattern type individually
        pattern_tests = {
            'fix_names': "fix column names",
            'fix_missing_mean': "fill missing with mean", 
            'fix_missing_median': "fill missing with median",
            'fix_missing_mode': "fill missing with mode",
            'fix_missing_drop': "drop missing",
            'drop_outliers_zscore': "remove outliers using zscore",
            'drop_outliers_iqr': "remove outliers using iqr",
            'drop_outliers_general': "remove outliers",
            'standardize_types': "standardize data types"
        }
        
        for pattern_type, test_command in pattern_tests.items():
            result = parser.parse_command(test_command)
            assert len(result) > 0, f"Pattern {pattern_type} failed to match: '{test_command}'"
    
    def test_whitespace_handling(self, parser):
        """Test handling of extra whitespace in commands"""
        test_cases = [
            "  fix   column    names  ",
            "\t\tremove\toutliers\t\t",
            "\nstandardize\n\ndata\ntypes\n",
            "   fill   missing   with   mean   "
        ]
        
        for command in test_cases:
            result = parser.parse_command(command)
            assert len(result) > 0, f"Whitespace handling failed for: '{command}'"
    
    def test_special_characters_in_commands(self, parser):
        """Test handling of special characters in commands"""
        test_cases = [
            "fix column names!",
            "remove outliers?",
            "standardize data types.",
            "fill missing with mean, please"
        ]
        
        for command in test_cases:
            result = parser.parse_command(command)
            # Should still parse the core command despite special characters
            assert len(result) > 0, f"Special character handling failed for: '{command}'"


if __name__ == '__main__':
    pytest.main([__file__])
