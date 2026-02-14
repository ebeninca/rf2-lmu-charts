"""
Utility functions for analytics operations.
Provides data preparation, validation, and time formatting utilities.
"""
import pandas as pd
from functools import wraps
import plotly.graph_objs as go


# ============================================================================
# Time Formatting Utilities
# ============================================================================

def format_lap_time_hover(seconds):
    """
    Format lap time for hover display (MM:SS.sss format).
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted time as "MM:SS.sss"
    """
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"


def format_lap_time_tick(seconds):
    """
    Format lap time for axis ticks (MM:SS format).
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted time as "MM:SS"
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def format_gap_time_hover(seconds):
    """
    Format gap time for hover display (MM:SS.sss format).
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted time as "M:SS.sss"
    """
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}:{secs:06.3f}"


def format_gap_time_tick(seconds):
    """
    Format gap time for axis ticks (M:SS format).
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted time as "M:SS"
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:01d}:{secs:02d}"


def format_time_series(time_series, format_func):
    """
    Format a series of times using a given format function.
    
    Args:
        time_series (pd.Series): Series of time values in seconds
        format_func (callable): Function to format individual time values
        
    Returns:
        list: List of formatted time strings
    """
    return [format_func(t) for t in time_series]


# ============================================================================
# Data Preparation and Validation
# ============================================================================

def prepare_chart_data(data, selected_drivers=None, selected_classes=None):
    """
    Prepare and filter chart data.
    
    Performs common operations:
    - Convert data to DataFrame
    - Check if empty and return None if so
    - Filter by drivers if provided
    - Filter by classes if provided
    - Check if empty after filtering
    
    Args:
        data (list or dict): Raw data to convert to DataFrame
        selected_drivers (list, optional): List of driver names to filter
        selected_classes (list, optional): List of class names to filter
        
    Returns:
        tuple: (df, is_empty) where df is the filtered DataFrame and 
               is_empty is a boolean indicating if the result is empty
    """
    df = pd.DataFrame(data)
    
    if df.empty:
        return None, True
    
    if selected_drivers:
        df = df[df['Driver'].isin(selected_drivers)]
    
    if selected_classes:
        df = df[df['Class'].isin(selected_classes)]
    
    if df.empty:
        return None, True
    
    return df, False


def empty_figure(message="No data available"):
    """
    Create an empty Plotly figure with a message.
    
    Args:
        message (str): Message to display in the figure
        
    Returns:
        go.Figure: Empty figure with annotation
    """
    return go.Figure().add_annotation(text=message, showarrow=False)


def prepare_chart_data_with_validation(
    data, 
    selected_drivers=None, 
    selected_classes=None, 
    additional_filter=None,
    empty_message="No data available"
):
    """
    Prepare chart data with optional additional validation.
    
    This function extends prepare_chart_data with support for additional
    filtering logic (e.g., filter out zero lap times).
    
    Args:
        data (list or dict): Raw data to convert to DataFrame
        selected_drivers (list, optional): List of driver names to filter
        selected_classes (list, optional): List of class names to filter
        additional_filter (callable, optional): Function that takes a DataFrame
                                               and returns a filtered DataFrame
        empty_message (str): Message to display if data is empty
        
    Returns:
        tuple: (df, figure) where df is the filtered DataFrame (or None if empty)
               and figure is either None (if data exists) or an empty figure
    """
    df, is_empty = prepare_chart_data(data, selected_drivers, selected_classes)
    
    if is_empty:
        return None, empty_figure(empty_message)
    
    if additional_filter:
        df = additional_filter(df)
        if df.empty:
            return None, empty_figure(empty_message)
    
    return df, None


def chart_decorator(**decorator_kwargs):
    """
    Decorator for chart update functions to handle common data preparation.
    
    Automatically handles:
    - Data preparation and filtering
    - Empty data checks
    - Returning empty figures when appropriate
    
    Usage:
        @chart_decorator(empty_message="No lap time data")
        def update_my_chart(df, selected_drivers, selected_classes):
            # df is already prepared and filtered
            # Create and return the figure
            pass
    
    Args:
        **decorator_kwargs: Optional keyword arguments:
            - empty_message (str): Message for empty figures
            - additional_filter (callable): Extra filtering function
    
    Returns:
        function: Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(data, selected_drivers=None, selected_classes=None):
            empty_message = decorator_kwargs.get('empty_message', 'No data available')
            additional_filter = decorator_kwargs.get('additional_filter', None)
            
            df, empty_fig = prepare_chart_data_with_validation(
                data,
                selected_drivers=selected_drivers,
                selected_classes=selected_classes,
                additional_filter=additional_filter,
                empty_message=empty_message
            )
            
            if empty_fig is not None:
                return empty_fig
            
            return func(df, selected_drivers, selected_classes)
        
        return wrapper
    
    return decorator
