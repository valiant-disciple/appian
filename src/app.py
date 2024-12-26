import streamlit as st
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.ai.llm_client import LLMClient
from src.models.suggestion import Suggestion

class StateManager:
    @staticmethod
    def initialize_state():
        """Initialize all session state variables"""
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.chat_history = []
            st.session_state.current_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>My Site</title>
            </head>
            <body>
                <h1>Welcome to My Site</h1>
            </body>
            </html>
            """
            st.session_state.html_editor = st.session_state.current_html  # Initialize html_editor
            st.session_state.current_suggestion_index = 0
            st.session_state.preview_key = 0

    @staticmethod
    def get_state():
        StateManager.initialize_state()
        return st.session_state

    @staticmethod
    def add_message(role: str, content: str, suggestion: Optional[Suggestion] = None):
        StateManager.initialize_state()
        message = {"role": role, "content": content}
        if suggestion:
            message["suggestion"] = suggestion
        st.session_state.chat_history.append(message)

    @staticmethod
    def update_html(html: str):
        StateManager.initialize_state()
        st.session_state.current_html = html
        st.session_state.html_editor = html  # Update html_editor as well

class App:
    def __init__(self):
        self.llm_client = LLMClient()
        StateManager.initialize_state()
        
    def run(self):
        st.set_page_config(layout="wide", page_title="AI Web Developer")
        self._render_main_interface()

    def _render_main_interface(self):
        st.title("AI Web Developer")
        
        # Two main columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            self._render_code_editor()
        with col2:
            self._render_preview()
        
        # Buttons and chat below
        self._render_analysis_buttons()
        self._render_chat_interface()

    def _render_code_editor(self):
        st.subheader("HTML Editor")
        new_html = st.text_area(
            "Enter your HTML code",
            value=st.session_state.current_html,
            height=300,
            key=f"html_editor_{st.session_state.preview_key}"
        )
        
        if new_html != st.session_state.current_html:
            StateManager.update_html(new_html)

    def _render_preview(self):
        st.subheader("Live Preview")
        if st.session_state.current_html:
            # Create a scrollable container that renders HTML properly
            preview_container = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <base target="_blank">
                    <style>
                        body {{ margin: 0; padding: 10px; }}
                    </style>
                </head>
                <body>
                    <div style="width:100%; height:100%; overflow:auto;">
                        {st.session_state.html_editor}
                    </div>
                </body>
                </html>
            """
            
            # Render with proper height and no overlay
            st.components.v1.html(
                preview_container,
                height=320,
                scrolling=True
            )
        else:
            st.info("Enter HTML code to see preview")

    def _render_analysis_buttons(self):
        st.markdown("---")
        cols = st.columns(3)
        
        with cols[0]:
            if st.button("🎨 AI UX Design Expert", use_container_width=True):
                self._analyze_code("ux")
        
        with cols[1]:
            if st.button("✨ Best Practices", use_container_width=True):
                self._analyze_code("practices")
        
        with cols[2]:
            if st.button("⚡ Performance Optimization", use_container_width=True):
                self._analyze_code("performance")

    def _render_chat_interface(self):
        st.markdown("### AI Suggestions")
        
        # Display chat history with suggestions
        for idx, message in enumerate(st.session_state.chat_history):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "suggestion" in message:
                    self._render_suggestion(message["suggestion"], idx)

        # Chat input
        if prompt := st.chat_input("Ask for specific improvements..."):
            self._handle_chat_input(prompt)

    def _render_suggestion(self, suggestion: Suggestion, idx: int):
        st.markdown("### Available Improvements")
        
        num_suggestions = len(suggestion.changes)
        st.markdown(f"Found **{num_suggestions}** potential improvements:")
        
        for i, (element_id, change) in enumerate(suggestion.changes.items(), 1):
            with st.expander(f"Suggestion {i}: {change.status}", expanded=True):
                if change.old:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Current Code:**")
                        st.code(change.old, language="html")
                    with col2:
                        st.markdown("**Improved Code:**")
                        st.code(change.new, language="html")
                else:
                    st.markdown("**New Code to Add:**")
                    st.code(change.new, language="html")
                
                action_cols = st.columns([1, 1])
                with action_cols[0]:
                    if st.button("✅ Apply", key=f"apply_{idx}_{element_id}"):
                        success = self._apply_change(change)
                        if success:
                            StateManager.add_message(
                                "assistant",
                                f"✅ Successfully applied change {i} of {num_suggestions}: {change.status}"
                            )
                            st.rerun()
                        else:
                            st.error("❌ Failed to apply change. The original code segment might have been modified.")
                
                with action_cols[1]:
                    if st.button("❌ Skip", key=f"skip_{idx}_{element_id}"):
                        StateManager.add_message(
                            "assistant",
                            f"⏭️ Skipped suggestion {i} of {num_suggestions}: {change.status}"
                        )
                        st.rerun()

    def _verify_and_apply_change(self, change, original_html: str) -> bool:
        """Verify if change is still applicable, if not get updated suggestion"""
        if self._can_apply_change(change, st.session_state.html_editor):
            return self._apply_change(change)
        
        # If change can't be applied, get fresh suggestion
        try:
            with st.spinner("Code has been modified, updating suggestion..."):
                new_suggestion = self.llm_client.analyze_code(
                    st.session_state.html_editor,
                    custom_prompt=f"Update this change: {change.status}. Original change was from '{change.old}' to '{change.new}'"
                )
                
                if new_suggestion and new_suggestion.changes:
                    new_change = list(new_suggestion.changes.values())[0]
                    if self._can_apply_change(new_change, st.session_state.html_editor):
                        return self._apply_change(new_change)
        except Exception as e:
            print(f"Error updating change: {e}")
        return False

    def _can_apply_change(self, change, html: str) -> bool:
        """Check if a change can be applied to the current HTML"""
        if not change.old:
            return True
            
        # Try direct match
        if change.old in html:
            return True
            
        # Try with different quote styles
        old_single = change.old.replace('"', "'")
        old_double = change.old.replace("'", '"')
        if old_single in html or old_double in html:
            return True
            
        # Try with normalized whitespace
        normalized_old = ' '.join(change.old.split())
        normalized_html = ' '.join(html.split())
        return normalized_old in normalized_html

    def _apply_change(self, change) -> bool:
        try:
            current_html = st.session_state.current_html
            new_html = None

            if change.old:
                # Try exact match first
                if change.old in current_html:
                    new_html = current_html.replace(change.old, change.new)
                else:
                    # Try with different quote styles
                    old_single = change.old.replace('"', "'")
                    old_double = change.old.replace("'", '"')
                    
                    if old_single in current_html:
                        new_html = current_html.replace(old_single, change.new)
                    elif old_double in current_html:
                        new_html = current_html.replace(old_double, change.new)
                    else:
                        # Try with normalized whitespace
                        normalized_old = ' '.join(change.old.split())
                        normalized_current = ' '.join(current_html.split())
                        
                        if normalized_old in normalized_current:
                            # Find the original segment
                            words = change.old.split()
                            start_idx = 0
                            for word in words:
                                idx = current_html[start_idx:].find(word)
                                if idx != -1:
                                    start_idx += idx
                                    break
                            
                            if start_idx != 0:
                                # Find the complete segment
                                end_idx = start_idx
                                for word in reversed(words):
                                    idx = current_html[end_idx:].find(word)
                                    if idx != -1:
                                        end_idx += idx + len(word)
                                        break
                                
                                original_segment = current_html[start_idx:end_idx]
                                new_html = current_html.replace(original_segment, change.new)
            else:
                # If no old code, assume it's an addition
                soup = BeautifulSoup(current_html, 'html.parser')
                body = soup.find('body')
                if body:
                    new_content = BeautifulSoup(change.new, 'html.parser')
                    body.append(new_content)
                    new_html = str(soup)
                else:
                    new_html = current_html.replace('</body>', f'{change.new}</body>')

            if new_html:
                # Update the state with new HTML
                StateManager.update_html(new_html)
                # Increment preview key to force refresh
                st.session_state.preview_key = st.session_state.get('preview_key', 0) + 1
                return True
            
            return False
            
        except Exception as e:
            print(f"Error applying change: {e}")
            return False

    def _analyze_code(self, analysis_type: str):
        if not st.session_state.current_html:
            st.warning("Please enter some HTML code first")
            return
        
        with st.spinner(f"Analyzing {analysis_type}..."):
            try:
                # Always get the latest HTML from the editor
                latest_html = st.session_state.html_editor
                
                suggestion = self.llm_client.analyze_code(
                    latest_html,
                    analysis_type=analysis_type
                )
                
                if suggestion:
                    messages = {
                        "ux": "Here are my UX design suggestions:",
                        "practices": "Here are my best practices suggestions:",
                        "performance": "Here are my performance optimization suggestions:"
                    }
                    StateManager.add_message(
                        "assistant",
                        messages.get(analysis_type, "Here are my suggestions:"),
                        suggestion
                    )
                else:
                    st.error("Failed to generate suggestions. Please try again.")
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")

    def _handle_chat_input(self, prompt: str):
        if not st.session_state.current_html:
            st.warning("Please enter some HTML code first")
            return
        
        # Add user message immediately for better feedback
        StateManager.add_message("user", f"🗣️ {prompt}")
        
        with st.spinner("🤔 Processing your request..."):
            try:
                # Get current HTML
                current_html = st.session_state.html_editor or st.session_state.current_html
                
                # Get suggestions
                suggestion = self.llm_client.analyze_code(
                    current_html,
                    custom_prompt=prompt
                )
                
                if suggestion and suggestion.changes:
                    # Add assistant response with the suggestions
                    StateManager.add_message(
                        "assistant",
                        "🎨 Here's how I can help with that:",
                        suggestion
                    )
                    # Force refresh to show new suggestions
                    st.rerun()
                else:
                    StateManager.add_message(
                        "assistant",
                        "❌ I couldn't generate appropriate changes for your request. Could you please rephrase it?"
                    )
                    st.rerun()
                    
            except Exception as e:
                print(f"Chat error: {str(e)}")  # Log the error
                StateManager.add_message(
                    "assistant",
                    "🔧 I encountered an error while processing your request. Please try again."
                )
                st.rerun()

def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()