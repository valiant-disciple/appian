import functools
import streamlit as st
from typing import Any, Callable

class ErrorHandler:
    """Handles errors in the application"""
    
    @staticmethod
    def handle_error(func: Callable) -> Callable:
        """Decorator to handle errors in async functions"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                st.error(f"Error: {str(e)}")
                print(f"Error in {func.__name__}: {str(e)}")
                return None
        return wrapper 