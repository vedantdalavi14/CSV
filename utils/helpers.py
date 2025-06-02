"""
Helper Utilities Module
Common utility functions used across the CSV cleaner application
"""

import os
import re
from pathlib import Path
from typing import Union, Optional, List, Dict, Any
import pandas as pd


def validate_file(file_path: Union[str, Path]) -> bool:
    """
    Validate that a file exists and is readable
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file is valid, False otherwise
    """
    try:
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            return False
        
        # Check if it's a file (not directory)
        if not path.is_file():
            return False
        
        # Check if file is readable
        if not os.access(path, os.R_OK):
            return False
        
        # Check if file has content
        if path.stat().st_size == 0:
            return False
        
        return True
        
    except (OSError, PermissionError):
        return False


def validate_csv_file(file_path: Union[str, Path]) -> tuple:
    """
    Validate that a file is a readable CSV file
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not validate_file(file_path):
        return False, "File does not exist or is not readable"
    
    path = Path(file_path)
    
    # Check file extension
    if path.suffix.lower() not in ['.csv', '.txt']:
        return False, f"File extension '{path.suffix}' is not supported. Use .csv or .txt files."
    
    # Try to read the first few lines to validate CSV format
    try:
        # Read just the first few rows to check format
        pd.read_csv(file_path, nrows=5)
        return True, None
        
    except pd.errors.EmptyDataError:
        return False, "CSV file is empty"
    except pd.errors.ParserError as e:
        return False, f"CSV parsing error: {str(e)}"
    except Exception as e:
        return False, f"Error reading CSV file: {str(e)}"


def generate_output_filename(input_file: Union[str, Path], excel: bool = False) -> str:
    """
    Generate an appropriate output filename based on input file
    
    Args:
        input_file: Path to input file
        excel: Whether to generate Excel filename
        
    Returns:
        Generated output filename
    """
    path = Path(input_file)
    
    # Get base name without extension
    base_name = path.stem
    
    # Add suffix
    output_name = f"{base_name}_cleaned"
    
    # Add appropriate extension
    if excel:
        extension = '.xlsx'
    else:
        extension = '.csv'
    
    # Combine with original directory
    output_path = path.parent / f"{output_name}{extension}"
    
    return str(output_path)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing/replacing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = 'unnamed_file'
    
    return sanitized


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get detailed information about a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    try:
        path = Path(file_path)
        stat = path.stat()
        
        return {
            'exists': path.exists(),
            'is_file': path.is_file(),
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'readable': os.access(path, os.R_OK),
            'writable': os.access(path, os.W_OK),
            'extension': path.suffix.lower(),
            'name': path.name,
            'stem': path.stem,
            'parent': str(path.parent)
        }
        
    except Exception as e:
        return {
            'exists': False,
            'error': str(e)
        }


def format_number(number: Union[int, float], precision: int = 2) -> str:
    """
    Format a number with appropriate precision and thousand separators
    
    Args:
        number: Number to format
        precision: Decimal places for floats
        
    Returns:
        Formatted number string
    """
    if isinstance(number, int):
        return f"{number:,}"
    elif isinstance(number, float):
        if precision == 0:
            return f"{number:,.0f}"
        else:
            return f"{number:,.{precision}f}"
    else:
        return str(number)


def create_backup_filename(original_path: Union[str, Path]) -> str:
    """
    Create a backup filename for the original file
    
    Args:
        original_path: Path to original file
        
    Returns:
        Backup filename
    """
    path = Path(original_path)
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    
    backup_name = f"{path.stem}_backup_{timestamp}{path.suffix}"
    backup_path = path.parent / backup_name
    
    return str(backup_path)


def safe_column_name(name: str) -> str:
    """
    Create a safe column name for DataFrame operations
    
    Args:
        name: Original column name
        
    Returns:
        Safe column name
    """
    # Convert to string
    safe_name = str(name)
    
    # Replace problematic characters
    safe_name = re.sub(r'[^\w\s-]', '', safe_name)
    safe_name = re.sub(r'[-\s]+', '_', safe_name)
    
    # Remove leading/trailing underscores
    safe_name = safe_name.strip('_')
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = 'unnamed_column'
    
    # Ensure it doesn't start with a number
    if safe_name[0].isdigit():
        safe_name = f'col_{safe_name}'
    
    return safe_name


def get_memory_usage(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get detailed memory usage information for a DataFrame
    
    Args:
        df: pandas DataFrame
        
    Returns:
        Dictionary with memory usage details
    """
    if df.empty:
        return {'total_mb': 0, 'per_column': {}}
    
    memory_usage = df.memory_usage(deep=True)
    total_bytes = memory_usage.sum()
    
    # Convert to MB
    total_mb = total_bytes / (1024 * 1024)
    
    # Per column usage
    per_column = {}
    for col in df.columns:
        col_bytes = df[col].memory_usage(deep=True)
        col_mb = col_bytes / (1024 * 1024)
        per_column[col] = {
            'mb': round(col_mb, 3),
            'percentage': round((col_bytes / total_bytes) * 100, 1)
        }
    
    return {
        'total_mb': round(total_mb, 3),
        'total_bytes': total_bytes,
        'per_column': per_column
    }


def estimate_processing_time(df: pd.DataFrame) -> str:
    """
    Estimate processing time based on DataFrame size
    
    Args:
        df: pandas DataFrame
        
    Returns:
        Estimated processing time string
    """
    if df.empty:
        return "< 1 second"
    
    total_cells = len(df) * len(df.columns)
    
    if total_cells < 10000:
        return "< 1 second"
    elif total_cells < 100000:
        return "1-5 seconds"
    elif total_cells < 1000000:
        return "5-30 seconds"
    elif total_cells < 10000000:
        return "30 seconds - 2 minutes"
    else:
        return "2+ minutes"


def chunk_dataframe(df: pd.DataFrame, chunk_size: int = 10000) -> List[pd.DataFrame]:
    """
    Split a large DataFrame into smaller chunks for processing
    
    Args:
        df: pandas DataFrame
        chunk_size: Number of rows per chunk
        
    Returns:
        List of DataFrame chunks
    """
    if df.empty:
        return [df]
    
    chunks = []
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i + chunk_size].copy()
        chunks.append(chunk)
    
    return chunks


def merge_chunks(chunks: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Merge a list of DataFrame chunks back into a single DataFrame
    
    Args:
        chunks: List of DataFrame chunks
        
    Returns:
        Merged DataFrame
    """
    if not chunks:
        return pd.DataFrame()
    
    if len(chunks) == 1:
        return chunks[0]
    
    return pd.concat(chunks, ignore_index=True)
