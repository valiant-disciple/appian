import streamlit as st
from typing import Dict, Optional, List
import hashlib
from datetime import datetime
from dataclasses import dataclass
from .state import StateManager, ErrorHandler, SuccessHandler

@dataclass
class VersionMetadata:
    """Version metadata"""
    author: str = "system"
    tags: List[str] = None
    description: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass 
class Version:
    """Version data structure"""
    id: str
    timestamp: datetime
    html: str
    css: str
    js: str
    message: str
    hash: str
    metadata: VersionMetadata = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = VersionMetadata()

class VersionControl:
    """Handle code version control and history"""
    
    def __init__(self):
        """Initialize version control"""
        self._initialize_history()
        self.max_history = 50

    def _initialize_history(self) -> None:
        """Initialize version history"""
        if 'version_history' not in st.session_state:
            st.session_state.version_history = []
        if 'version_index' not in st.session_state:
            st.session_state.version_index = -1

    def save_state(self, html: str, css: str, js: str, message: str = "") -> None:
        """Save current state to history"""
        try:
            version = Version(
                id=self._generate_version_id(),
                timestamp=datetime.now(),
                html=html,
                css=css,
                js=js,
                message=message,
                hash=self._generate_hash(html, css, js)
            )
            
            # Remove any forward history if we're not at the latest version
            if st.session_state.version_index < len(st.session_state.version_history) - 1:
                st.session_state.version_history = (
                    st.session_state.version_history[:st.session_state.version_index + 1]
                )
            
            st.session_state.version_history.append(vars(version))
            st.session_state.version_index = len(st.session_state.version_history) - 1
            
            # Maintain history limit
            if len(st.session_state.version_history) > self.max_history:
                st.session_state.version_history.pop(0)
                st.session_state.version_index -= 1

            SuccessHandler.show_success("Version saved successfully")

        except Exception as e:
            ErrorHandler.handle_error(e, "saving version")

    def undo(self) -> Optional[Dict[str, str]]:
        """Undo to previous state"""
        try:
            if st.session_state.version_index > 0:
                st.session_state.version_index -= 1
                return self._get_current_state()
            return None
        except Exception as e:
            ErrorHandler.handle_error(e, "undoing changes")
            return None

    def redo(self) -> Optional[Dict[str, str]]:
        """Redo to next state"""
        try:
            if st.session_state.version_index < len(st.session_state.version_history) - 1:
                st.session_state.version_index += 1
                return self._get_current_state()
            return None
        except Exception as e:
            ErrorHandler.handle_error(e, "redoing changes")
            return None

    def get_history(self) -> List[Dict]:
        """Get version history"""
        return st.session_state.version_history

    def get_version(self, version_id: str) -> Optional[Version]:
        """Get specific version by ID"""
        try:
            for version in st.session_state.version_history:
                if version['id'] == version_id:
                    return Version(**version)
            return None
        except Exception as e:
            ErrorHandler.handle_error(e, "getting version")
            return None

    def restore_version(self, version_id: str) -> bool:
        """Restore to specific version"""
        try:
            for i, version in enumerate(st.session_state.version_history):
                if version['id'] == version_id:
                    st.session_state.version_index = i
                    state = self._get_current_state()
                    StateManager.update_state(**state)
                    SuccessHandler.show_success(f"Restored to version: {version_id}")
                    return True
            return False
        except Exception as e:
            ErrorHandler.handle_error(e, "restoring version")
            return False

    def _generate_version_id(self) -> str:
        """Generate unique version ID"""
        timestamp = datetime.now().timestamp()
        return hashlib.md5(f"version_{timestamp}".encode()).hexdigest()[:8]

    def _generate_hash(self, html: str, css: str, js: str) -> str:
        """Generate hash for state"""
        content = f"{html}{css}{js}".encode('utf-8')
        return hashlib.sha256(content).hexdigest()[:8]

    def _get_current_state(self) -> Dict[str, str]:
        """Get current state"""
        try:
            if not st.session_state.version_history:
                return {"html": "", "css": "", "js": ""}
            
            version = st.session_state.version_history[st.session_state.version_index]
            return {
                "current_html": version["html"],
                "current_css": version["css"],
                "current_js": version["js"]
            }
        except Exception as e:
            ErrorHandler.handle_error(e, "getting current state")
            return {"html": "", "css": "", "js": ""}

    def clear_history(self) -> None:
        """Clear version history"""
        try:
            st.session_state.version_history = []
            st.session_state.version_index = -1
            SuccessHandler.show_success("Version history cleared")
        except Exception as e:
            ErrorHandler.handle_error(e, "clearing history")

    def get_diff(self, version_id1: str, version_id2: str) -> Dict[str, List[str]]:
        """Get differences between two versions"""
        try:
            v1 = self.get_version(version_id1)
            v2 = self.get_version(version_id2)
            
            if not v1 or not v2:
                return {}
            
            import difflib
            
            return {
                "html": list(difflib.unified_diff(
                    v1.html.splitlines(),
                    v2.html.splitlines(),
                    lineterm=''
                )),
                "css": list(difflib.unified_diff(
                    v1.css.splitlines(),
                    v2.css.splitlines(),
                    lineterm=''
                )),
                "js": list(difflib.unified_diff(
                    v1.js.splitlines(),
                    v2.js.splitlines(),
                    lineterm=''
                ))
            }
        except Exception as e:
            ErrorHandler.handle_error(e, "getting version diff")
            return {}