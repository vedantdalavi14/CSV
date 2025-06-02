"""
Natural Language Parser for CSV Cleaning Commands
Converts natural language commands to cleaning flags using regex patterns
"""

import re
from typing import Dict, Optional, Any
import logging


class NLPParser:
    """Parses natural language commands and converts them to cleaning flags"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define regex patterns for different cleaning operations
        self.patterns = {
            'fix_names': [
                r'fix\s+(the\s+)?(column\s+)?(names?|headers?|titles?)',
                r'clean\s+(the\s+)?(column\s+)?(names?|headers?|titles?)',
                r'standardize\s+(the\s+)?(column\s+)?(names?|headers?|titles?)',
                r'normalize\s+(the\s+)?(column\s+)?(names?|headers?|titles?)'
            ],
            'fix_missing_mean': [
                r'(fill|handle|fix)\s+missing\s+(data\s+)?(with\s+|using\s+)?mean',
                r'mean\s+(for\s+)?missing',
                r'replace\s+missing\s+(with\s+)?mean'
            ],
            'fix_missing_median': [
                r'(fill|handle|fix)\s+missing\s+(data\s+)?(with\s+|using\s+)?median',
                r'median\s+(for\s+)?missing',
                r'replace\s+missing\s+(with\s+)?median'
            ],
            'fix_missing_mode': [
                r'(fill|handle|fix)\s+missing\s+(data\s+)?(with\s+|using\s+)?mode',
                r'mode\s+(for\s+)?missing',
                r'replace\s+missing\s+(with\s+)?mode'
            ],
            'fix_missing_drop': [
                r'drop\s+(rows\s+with\s+)?missing',
                r'remove\s+(rows\s+with\s+)?missing',
                r'delete\s+(rows\s+with\s+)?missing',
                r'(handle|fix)\s+missing\s+(data\s+)?(by\s+)?drop'
            ],
            'drop_outliers_zscore': [
                r'remove\s+outliers\s+(using\s+)?z.?score',
                r'drop\s+outliers\s+(using\s+)?z.?score',
                r'z.?score\s+outliers?'
            ],
            'drop_outliers_iqr': [
                r'remove\s+outliers\s+(using\s+)?iqr',
                r'drop\s+outliers\s+(using\s+)?iqr',
                r'iqr\s+outliers?',
                r'interquartile\s+range\s+outliers?'
            ],
            'drop_outliers_general': [
                r'remove\s+outliers?',
                r'drop\s+outliers?',
                r'delete\s+outliers?',
                r'(fix|handle)\s+outliers?'
            ],
            'standardize_types': [
                r'standardize\s+(data\s+)?types?',
                r'convert\s+(data\s+)?types?',
                r'fix\s+(data\s+)?types?',
                r'normalize\s+(data\s+)?types?'
            ]
        }
    
    def parse_command(self, command: str) -> Dict[str, Any]:
        """
        Parse a natural language command and return corresponding flags
        
        Args:
            command: Natural language command string
            
        Returns:
            Dictionary with cleaning flags
        """
        if not command or not command.strip():
            return {}
        
        # Normalize command: lowercase and remove extra whitespace
        normalized_command = re.sub(r'\s+', ' ', command.lower().strip())
        self.logger.debug(f"Parsing normalized command: '{normalized_command}'")
        
        flags = {}
        
        # Check for column name fixing
        if self._match_patterns(normalized_command, self.patterns['fix_names']):
            flags['fix_names'] = True
            self.logger.debug("Detected: fix column names")
        
        # Check for missing data handling (specific strategies first)
        if self._match_patterns(normalized_command, self.patterns['fix_missing_mean']):
            flags['fix_missing'] = 'mean'
            self.logger.debug("Detected: fix missing data with mean")
        elif self._match_patterns(normalized_command, self.patterns['fix_missing_median']):
            flags['fix_missing'] = 'median'
            self.logger.debug("Detected: fix missing data with median")
        elif self._match_patterns(normalized_command, self.patterns['fix_missing_mode']):
            flags['fix_missing'] = 'mode'
            self.logger.debug("Detected: fix missing data with mode")
        elif self._match_patterns(normalized_command, self.patterns['fix_missing_drop']):
            flags['fix_missing'] = 'drop'
            self.logger.debug("Detected: fix missing data by dropping")
        
        # Check for outlier removal (specific methods first)
        if self._match_patterns(normalized_command, self.patterns['drop_outliers_zscore']):
            flags['drop_outliers'] = 'zscore'
            self.logger.debug("Detected: remove outliers using z-score")
        elif self._match_patterns(normalized_command, self.patterns['drop_outliers_iqr']):
            flags['drop_outliers'] = 'iqr'
            self.logger.debug("Detected: remove outliers using IQR")
        elif self._match_patterns(normalized_command, self.patterns['drop_outliers_general']):
            # Default to z-score for general outlier removal
            flags['drop_outliers'] = 'zscore'
            self.logger.debug("Detected: remove outliers (defaulting to z-score)")
        
        # Check for type standardization
        if self._match_patterns(normalized_command, self.patterns['standardize_types']):
            flags['standardize_types'] = True
            self.logger.debug("Detected: standardize data types")
        
        return flags
    
    def _match_patterns(self, text: str, patterns: list) -> bool:
        """
        Check if any of the given patterns match the text
        
        Args:
            text: Text to search in
            patterns: List of regex patterns
            
        Returns:
            True if any pattern matches, False otherwise
        """
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def get_supported_commands(self) -> Dict[str, list]:
        """
        Return a dictionary of supported command examples
        
        Returns:
            Dictionary with operation types and example phrases
        """
        return {
            'Column Names': [
                'fix column names',
                'clean headers',
                'standardize titles'
            ],
            'Missing Data': [
                'fill missing with mean',
                'handle missing using median',
                'drop rows with missing values'
            ],
            'Outliers': [
                'remove outliers',
                'drop outliers using iqr',
                'remove outliers using z-score'
            ],
            'Data Types': [
                'standardize data types',
                'convert data types',
                'fix data types'
            ],
            'Combined': [
                'fix column names and remove outliers',
                'standardize types and fill missing with median',
                'clean headers and drop outliers using iqr'
            ]
        }
