"""
Logging Configuration Module
Sets up structured logging for the CSV cleaning operations
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logger(log_file: str = 'cleaning.log', verbose: bool = False) -> logging.Logger:
    """
    Set up logging configuration for the CSV cleaner
    
    Args:
        log_file: Path to log file
        verbose: Whether to enable verbose console output
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('csv_cleaner')
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler - always detailed
    try:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
    except Exception as e:
        print(f"Warning: Could not set up file logging: {e}")
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    if verbose:
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(detailed_formatter)
    else:
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
    
    logger.addHandler(console_handler)
    
    # Log the start of a new session
    logger.info("=" * 60)
    logger.info(f"Smart CSV Cleaner - Session started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    return logger


def log_dataframe_info(logger: logging.Logger, df, stage: str = ""):
    """
    Log basic information about a DataFrame
    
    Args:
        logger: Logger instance
        df: pandas DataFrame
        stage: Description of the current processing stage
    """
    if df.empty:
        logger.info(f"{stage}DataFrame is empty")
        return
    
    stage_prefix = f"{stage} - " if stage else ""
    
    logger.info(f"{stage_prefix}DataFrame info: {len(df)} rows × {len(df.columns)} columns")
    logger.debug(f"{stage_prefix}Columns: {list(df.columns)}")
    logger.debug(f"{stage_prefix}Data types: {dict(df.dtypes)}")
    
    # Log memory usage
    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    logger.debug(f"{stage_prefix}Memory usage: {memory_mb:.2f} MB")
    
    # Log missing values summary
    missing_count = df.isnull().sum().sum()
    if missing_count > 0:
        logger.info(f"{stage_prefix}Missing values: {missing_count} total")
    else:
        logger.debug(f"{stage_prefix}No missing values")


def log_operation_start(logger: logging.Logger, operation: str, **kwargs):
    """
    Log the start of a cleaning operation
    
    Args:
        logger: Logger instance
        operation: Name of the operation
        **kwargs: Additional parameters to log
    """
    logger.info(f"🔧 Starting operation: {operation}")
    
    if kwargs:
        logger.debug(f"Parameters: {kwargs}")


def log_operation_complete(logger: logging.Logger, operation: str, success: bool = True, **stats):
    """
    Log the completion of a cleaning operation
    
    Args:
        logger: Logger instance
        operation: Name of the operation
        success: Whether the operation was successful
        **stats: Operation statistics to log
    """
    status = "✅ Completed" if success else "❌ Failed"
    logger.info(f"{status}: {operation}")
    
    if stats:
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")


def log_transformation_summary(logger: logging.Logger, transformations: list):
    """
    Log a summary of all transformations performed
    
    Args:
        logger: Logger instance
        transformations: List of transformation descriptions
    """
    logger.info("📋 Transformation Summary:")
    
    if not transformations:
        logger.info("  No transformations performed")
        return
    
    for i, transformation in enumerate(transformations, 1):
        logger.info(f"  {i}. {transformation}")


class CSVCleanerLogFilter(logging.Filter):
    """Custom log filter for CSV cleaner messages"""
    
    def filter(self, record):
        # Add custom attributes or filtering logic here
        # For now, just pass through all records
        return True


def create_operation_logger(operation_name: str, parent_logger: logging.Logger) -> logging.Logger:
    """
    Create a child logger for a specific operation
    
    Args:
        operation_name: Name of the operation
        parent_logger: Parent logger instance
        
    Returns:
        Child logger with operation-specific name
    """
    child_logger = parent_logger.getChild(operation_name)
    return child_logger


def log_error_with_context(logger: logging.Logger, error: Exception, context: str = ""):
    """
    Log an error with additional context information
    
    Args:
        logger: Logger instance
        error: Exception object
        context: Additional context about where the error occurred
    """
    error_msg = f"Error in {context}: {str(error)}" if context else f"Error: {str(error)}"
    logger.error(error_msg)
    logger.debug(f"Exception type: {type(error).__name__}")
    
    # Log stack trace in debug mode
    logger.debug("Stack trace:", exc_info=True)


def setup_test_logger() -> logging.Logger:
    """
    Set up a logger specifically for testing (writes to memory/console only)
    
    Returns:
        Test logger instance
    """
    logger = logging.getLogger('csv_cleaner_test')
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler only for tests
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger
