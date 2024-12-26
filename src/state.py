import streamlit as st
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AppState:
    """Application state structure"""
    current_html: str = ""
    current_css: str = ""
    current_js: str = ""
    version_history: list = None
    current_version: str = ""
    last_modified: datetime = None
    is_modified: bool = False
    active_suggestions: list = None
    chat_history: list = None
    preview_mode: str = "desktop"
    error_message: Optional[str] = None
    success_message: Optional[str] = None

    def __post_init__(self):
        """Initialize optional fields"""
        if self.version_history is None:
            self.version_history = []
        if self.active_suggestions is None:
            self.active_suggestions = []
        if self.chat_history is None:
            self.chat_history = []
        if self.last_modified is None:
            self.last_modified = datetime.now()

class StateManager:
    """Manage application state"""

    @staticmethod
    def initialize_session_state():
        """Initialize or reset session state"""
        if 'app_state' not in st.session_state:
            st.session_state.app_state = AppState()
        
        # Initialize other session state variables
        defaults = {
            'initial_analysis_done': False,
            'current_suggestions': [],
            'suggestion_index': 0,
            'chat_messages': [],
            'code_uploaded': False,
            'preview_device': 'desktop',
            'last_backup': None,
            'undo_stack': [],
            'redo_stack': []
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def get_state() -> AppState:
        """Get current application state"""
        if 'app_state' not in st.session_state:
            StateManager.initialize_session_state()
        return st.session_state.app_state

    @staticmethod
    def update_state(**kwargs):
        """Update state with new values"""
        state = StateManager.get_state()
        
        # Store current state in undo stack before updating
        if kwargs:
            StateManager._push_to_undo_stack()
        
        # Update state attributes
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)
                if key in ['current_html', 'current_css', 'current_js']:
                    state.is_modified = True
                    state.last_modified = datetime.now()

        # Auto-backup if needed
        StateManager._auto_backup()

    @staticmethod
    def _push_to_undo_stack():
        """Store current state in undo stack"""
        current_state = {
            'html': st.session_state.app_state.current_html,
            'css': st.session_state.app_state.current_css,
            'js': st.session_state.app_state.current_js
        }
        st.session_state.undo_stack.append(current_state)
        # Clear redo stack when new changes are made
        st.session_state.redo_stack.clear()

    @staticmethod
    def undo():
        """Restore previous state"""
        if st.session_state.undo_stack:
            # Store current state in redo stack
            current_state = {
                'html': st.session_state.app_state.current_html,
                'css': st.session_state.app_state.current_css,
                'js': st.session_state.app_state.current_js
            }
            st.session_state.redo_stack.append(current_state)
            
            # Restore previous state
            previous_state = st.session_state.undo_stack.pop()
            StateManager.update_state(
                current_html=previous_state['html'],
                current_css=previous_state['css'],
                current_js=previous_state['js']
            )

    @staticmethod
    def redo():
        """Restore previously undone state"""
        if st.session_state.redo_stack:
            # Store current state in undo stack
            current_state = {
                'html': st.session_state.app_state.current_html,
                'css': st.session_state.app_state.current_css,
                'js': st.session_state.app_state.current_js
            }
            st.session_state.undo_stack.append(current_state)
            
            # Restore redo state
            next_state = st.session_state.redo_stack.pop()
            StateManager.update_state(
                current_html=next_state['html'],
                current_css=next_state['css'],
                current_js=next_state['js']
            )

    @staticmethod
    def _auto_backup():
        """Automatically backup state if needed"""
        current_time = datetime.now()
        last_backup = st.session_state.get('last_backup')
        
        # Backup every 5 minutes if changes were made
        if (not last_backup or 
            (current_time - last_backup).total_seconds() > 300) and \
            st.session_state.app_state.is_modified:
            
            StateManager.backup_state()
            st.session_state.last_backup = current_time

    @staticmethod
    def backup_state():
        """Backup current state"""
        try:
            import json
            from pathlib import Path
            
            # Create backup directory if it doesn't exist
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            # Create backup file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"backup_{timestamp}.json"
            
            # Prepare backup data
            backup_data = {
                'html': st.session_state.app_state.current_html,
                'css': st.session_state.app_state.current_css,
                'js': st.session_state.app_state.current_js,
                'version_history': st.session_state.app_state.version_history,
                'timestamp': timestamp
            }
            
            # Save backup
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            # Update last backup time
            st.session_state.last_backup = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"Backup error: {str(e)}")
            return False

    @staticmethod
    def restore_backup(backup_file: str) -> bool:
        """Restore state from backup"""
        try:
            import json
            from pathlib import Path
            
            backup_path = Path("backups") / backup_file
            
            if backup_path.exists():
                with open(backup_path, 'r') as f:
                    backup_data = json.load(f)
                
                StateManager.update_state(
                    current_html=backup_data['html'],
                    current_css=backup_data['css'],
                    current_js=backup_data['js']
                )
                
                if 'version_history' in backup_data:
                    st.session_state.app_state.version_history = backup_data['version_history']
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Restore error: {str(e)}")
            return False

class ErrorHandler:
    """Handle and display errors"""
    
    @staticmethod
    def handle_error(error: Exception, context: str = ""):
        """Handle and display error message"""
        error_msg = f"Error {context}: {str(error)}"
        st.session_state.app_state.error_message = error_msg
        print(error_msg)  # For debugging

class SuccessHandler:
    """Handle and display success messages"""
    
    @staticmethod
    def show_success(message: str):
        """Display success message"""
        st.session_state.app_state.success_message = message