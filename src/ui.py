import streamlit as st
from typing import Optional
from pathlib import Path
import asyncio
from .state import StateManager
from .preview import PreviewSystem
from .ai.chat import AIChat
from .export_manager import ExportManager
from dataclasses import dataclass

@dataclass
class UIConfig:
    """UI Configuration"""
    show_preview: bool = True
    show_code: bool = True
    show_chat: bool = True
    dark_mode: bool = False
    layout: str = "wide"  # wide, centered, or minimal

class UI:
    """Main UI handler"""
    
    def __init__(self):
        self.preview = PreviewSystem()
        self.ai_chat = AIChat()
        self.export_manager = ExportManager()
        self._initialize_ui()

    def _initialize_ui(self):
        """Initialize UI state and configuration"""
        if 'ui_config' not in st.session_state:
            st.session_state.ui_config = UIConfig()
        
        # Set page configuration
        st.set_page_config(
            page_title="Web Component Builder",
            page_icon="🎨",
            layout=st.session_state.ui_config.layout,
            initial_sidebar_state="expanded"
        )

    def render(self):
        """Render main UI"""
        self._render_header()
        
        # Main layout
        if st.session_state.ui_config.layout == "wide":
            self._render_wide_layout()
        else:
            self._render_centered_layout()

    def _render_header(self):
        """Render page header and controls"""
        col1, col2, col3 = st.columns([3,1,1])
        
        with col1:
            st.title("Web Component Builder")
        
        with col2:
            if st.button("Export", key="export_btn"):
                self._handle_export()
        
        with col3:
            if st.button("Settings", key="settings_btn"):
                self._show_settings()

    def _render_wide_layout(self):
        """Render wide layout with side-by-side panels"""
        col1, col2, col3 = st.columns([2,2,1])
        
        with col1:
            self._render_code_editor()
        
        with col2:
            if st.session_state.ui_config.show_preview:
                self._render_preview()
        
        with col3:
            if st.session_state.ui_config.show_chat:
                self.ai_chat.render_chat_interface()

    def _render_centered_layout(self):
        """Render centered layout with stacked panels"""
        if st.session_state.ui_config.show_code:
            self._render_code_editor()
        
        if st.session_state.ui_config.show_preview:
            self._render_preview()
        
        if st.session_state.ui_config.show_chat:
            self.ai_chat.render_chat_interface()

    def _render_code_editor(self):
        """Render code editor tabs"""
        st.subheader("Code Editor")
        
        tabs = st.tabs(["HTML", "CSS", "JavaScript"])
        
        with tabs[0]:
            new_html = st.text_area(
                "HTML",
                value=st.session_state.get('current_html', ''),
                height=400,
                key="html_editor"
            )
            if new_html != st.session_state.get('current_html'):
                asyncio.run(self._handle_code_change('html', new_html))
        
        with tabs[1]:
            new_css = st.text_area(
                "CSS",
                value=st.session_state.get('current_css', ''),
                height=400,
                key="css_editor"
            )
            if new_css != st.session_state.get('current_css'):
                asyncio.run(self._handle_code_change('css', new_css))
        
        with tabs[2]:
            new_js = st.text_area(
                "JavaScript",
                value=st.session_state.get('current_js', ''),
                height=400,
                key="js_editor"
            )
            if new_js != st.session_state.get('current_js'):
                asyncio.run(self._handle_code_change('js', new_js))

    def _render_preview(self):
        """Render preview section"""
        st.subheader("Preview")
        self.preview.render_preview(
            st.session_state.get('current_html', ''),
            st.session_state.get('current_css', ''),
            st.session_state.get('current_js', '')
        )

    async def _handle_code_change(self, code_type: str, new_code: str):
        """Handle code changes and trigger AI analysis"""
        StateManager.update_state(**{f'current_{code_type}': new_code})
        
        if not st.session_state.get('initial_analysis_done'):
            await self.ai_chat.analyze_initial_code(
                st.session_state.get('current_html', ''),
                st.session_state.get('current_css', ''),
                st.session_state.get('current_js', '')
            )
            st.session_state.initial_analysis_done = True

    def _handle_export(self):
        """Handle code export"""
        export_type = st.selectbox(
            "Export as:",
            list(self.export_manager.FORMATS.keys())
        )
        
        if st.button("Download"):
            result = self.export_manager.export(
                export_type,
                st.session_state.get('current_html', ''),
                st.session_state.get('current_css', ''),
                st.session_state.get('current_js', ''),
                "my_component"
            )
            
            if result:
                st.download_button(
                    "Download File",
                    result,
                    file_name=f"my_component{self.export_manager.FORMATS[export_type].file_extension}",
                    mime="application/octet-stream"
                )

    def _show_settings(self):
        """Show settings modal"""
        with st.expander("Settings", expanded=True):
            config = st.session_state.ui_config
            
            config.show_preview = st.checkbox("Show Preview", config.show_preview)
            config.show_code = st.checkbox("Show Code Editor", config.show_code)
            config.show_chat = st.checkbox("Show AI Chat", config.show_chat)
            
            config.layout = st.selectbox(
                "Layout",
                ["wide", "centered", "minimal"],
                index=["wide", "centered", "minimal"].index(config.layout)
            )
            
            config.dark_mode = st.checkbox("Dark Mode", config.dark_mode)
            
            if st.button("Apply Settings"):
                st.experimental_rerun()

class HTMLEnhancementApp(UI):
    """Legacy HTML Enhancement Application"""
    
    def __init__(self):
        super().__init__()
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize session state with legacy support"""
        if 'input_html' not in st.session_state:
            st.session_state.input_html = ""
        if 'enhanced_html' not in st.session_state:
            st.session_state.enhanced_html = ""
        if 'css_code' not in st.session_state:
            st.session_state.css_code = ""
        if 'js_code' not in st.session_state:
            st.session_state.js_code = ""

    def render(self):
        """Render the HTML Enhancement App"""
        st.title("HTML Enhancement App")

        # Input section
        with st.container():
            st.subheader("Input HTML")
            input_html = st.text_area(
                "Enter your HTML code here:",
                st.session_state.input_html,
                height=200,
                key="html_input"
            )

            if input_html != st.session_state.input_html:
                st.session_state.input_html = input_html
                if input_html.strip():
                    asyncio.run(self.ai_chat.analyze_initial_code(
                        input_html,
                        st.session_state.css_code,
                        st.session_state.js_code
                    ))

        # AI Chat and Suggestions
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.session_state.input_html:
                st.subheader("Preview")
                self.preview.render_preview(
                    st.session_state.input_html,
                    st.session_state.css_code,
                    st.session_state.js_code
                )

        with col2:
            self.ai_chat.render_chat_interface()

        # Export options
        if st.session_state.input_html:
            st.subheader("Export")
            export_format = st.selectbox(
                "Export Format",
                list(self.export_manager.FORMATS.keys())
            )
            
            if st.button("Export"):
                result = self.export_manager.export(
                    export_format,
                    st.session_state.input_html,
                    st.session_state.css_code,
                    st.session_state.js_code
                )
                
                if result:
                    st.download_button(
                        "Download",
                        result,
                        file_name=f"enhanced_component{self.export_manager.FORMATS[export_format].file_extension}",
                        mime="application/octet-stream"
                    )