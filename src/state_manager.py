from dataclasses import dataclass
import streamlit as st
from typing import Optional, List, Dict, Any

@dataclass
class State:
    current_html: str = ""
    chat_history: List[Dict[str, Any]] = None
    current_suggestions: List[Dict[str, Any]] = None
    last_suggestion_index: int = 0

class StateManager:
    @staticmethod
    def initialize_state():
        """Initialize the application state"""
        if 'app_state' not in st.session_state:
            st.session_state.app_state = State()
            st.session_state.app_state.chat_history = []
            st.session_state.app_state.current_suggestions = []
    
    @staticmethod
    def get_state() -> State:
        """Get the current application state"""
        if 'app_state' not in st.session_state:
            StateManager.initialize_state()
        return st.session_state.app_state
    
    @staticmethod
    def update_html(html: str):
        """Update the current HTML"""
        state = StateManager.get_state()
        state.current_html = html
    
    @staticmethod
    def add_message(role: str, content: str, **kwargs):
        """Add a message to chat history"""
        state = StateManager.get_state()
        message = {"role": role, "content": content, **kwargs}
        state.chat_history.append(message)
    
    @staticmethod
    def update_suggestions(suggestions: List[Dict[str, Any]]):
        """Update current suggestions"""
        state = StateManager.get_state()
        state.current_suggestions = suggestions
        state.last_suggestion_index = 0
    
    @staticmethod
    def get_next_suggestion() -> Optional[Dict[str, Any]]:
        """Get next suggestion from the queue"""
        state = StateManager.get_state()
        if not state.current_suggestions:
            return None
        if state.last_suggestion_index >= len(state.current_suggestions):
            return None
        suggestion = state.current_suggestions[state.last_suggestion_index]
        state.last_suggestion_index += 1
        return suggestion
    
    @staticmethod
    def clear_suggestions():
        """Clear current suggestions"""
        state = StateManager.get_state()
        state.current_suggestions = []
        state.last_suggestion_index = 0 