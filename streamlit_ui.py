# Must be the first import and first Streamlit command
import streamlit as st
st.set_page_config(
    page_title="Web Component Builder",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set, Union, Tuple
from pathlib import Path
import json
import re
import hashlib
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import difflib
from groq import Groq
import tempfile
import base64
from bs4 import BeautifulSoup, Tag
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class AppState:
    """Global application state"""
    current_project: Optional[str] = None
    current_component: Optional[str] = None
    current_html: str = ""
    current_css: str = ""
    current_js: str = ""
    chat_messages: List[Dict[str, str]] = field(default_factory=list)
    component_tree: List[Dict[str, Any]] = field(default_factory=list)
    is_preview_mode: bool = False
    show_grid: bool = False
    show_outlines: bool = False
    zoom_level: float = 1.0
    device_mode: str = "desktop"
    auto_optimize: bool = False
    live_preview: bool = True

def initialize_session_state():
    """Initialize or update session state with default values"""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.app_state = AppState()
        st.session_state.error = None
        st.session_state.success = None
        st.session_state.active_tab = "code"
        st.session_state.preview_content = ""
        st.session_state.undo_stack = []
        st.session_state.redo_stack = []
        st.session_state.current_project = None
        st.session_state.projects = {}
        st.session_state.components = {}

class UITheme:
    """UI theme configuration"""
    
    COLORS = {
        "primary": "#F3E8FF",
        "secondary": "#2D2D2D",
        "background": "#1A1A1A",
        "text": "#FFFFFF",
        "error": "#FF4444",
        "success": "#44FF44"
    }
    
    @classmethod
    def inject_styles(cls):
        """Inject theme styles into the app"""
        st.markdown("""
            <style>
                /* Main container styles */
                .main-container {
                    background-color: var(--background-color);
                    padding: 1rem;
                    border-radius: 8px;
                }
                
                /* Sidebar styles */
                .sidebar {
                    background-color: var(--secondary-color);
                    padding: 1rem;
                }
                [data-testid="stSidebar"] {
                    background-color: var(--secondary-color);
                }
                
                /* Code editor styles */
                .stTextArea textarea {
                    font-family: monospace !important;
                    background-color: var(--secondary-color) !important;
                    color: var(--text-color) !important;
                }
                
                /* Preview container styles */
                .preview-container {
                    background-color: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    margin: 1rem 0;
                }
                
                .preview-frame {
                    border: none;
                    width: 100%;
                    height: 100%;
                }
                
                /* Button styles */
                .stButton button {
                    width: 100%;
                    border-radius: 4px;
                    margin-bottom: 0.5rem;
                }
            </style>
        """, unsafe_allow_html=True)

class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def handle_error(error: Exception, context: str = "") -> None:
        """Handle and display error"""
        error_msg = f"Error in {context}: {str(error)}" if context else str(error)
        st.session_state.error = error_msg

    @staticmethod
    def show_error() -> None:
        """Display error if exists"""
        if st.session_state.error:
            st.error(st.session_state.error)
            st.session_state.error = None

class SuccessHandler:
    """Handle success messages"""
    
    @staticmethod
    def show_success(message: str) -> None:
        """Set success message"""
        st.session_state.success = message

    @staticmethod
    def display_success() -> None:
        """Display success message if exists"""
        if st.session_state.success:
            st.success(st.session_state.success)
            st.session_state.success = None

class ComponentManager:
    """Manage component creation, updates, and rendering"""
    
    def __init__(self):
        if 'components' not in st.session_state:
            st.session_state.components = {}
        self._load_default_components()

    def _load_default_components(self):
        """Load default component templates"""
        default_components = {
            "modern_search": {
                "html": """
                    <div class="search-container">
                        <input type="text" placeholder="Search..." class="search-input">
                        <button class="search-button">
                            <span class="search-icon">🔍</span>
                        </button>
                    </div>
                """,
                "css": """
                    .search-container {
                        display: flex;
                        max-width: 500px;
                        margin: 20px auto;
                        border-radius: 25px;
                        overflow: hidden;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }
                    
                    .search-input {
                        flex: 1;
                        padding: 12px 20px;
                        border: none;
                        outline: none;
                        font-size: 16px;
                    }
                    
                    .search-button {
                        background: var(--primary-color);
                        border: none;
                        padding: 0 20px;
                        cursor: pointer;
                        transition: background 0.3s ease;
                    }
                    
                    .search-button:hover {
                        background: #E9D5FF;
                    }
                """,
                "js": """
                    document.querySelector('.search-button').addEventListener('click', () => {
                        const input = document.querySelector('.search-input');
                        console.log('Search:', input.value);
                    });
                """,
                "category": "inputs"
            },
            "nav_bar": {
                "html": """
                    <nav class="nav-bar">
                        <div class="nav-brand">Brand</div>
                        <ul class="nav-links">
                            <li><a href="#home">Home</a></li>
                            <li><a href="#about">About</a></li>
                            <li><a href="#contact">Contact</a></li>
                        </ul>
                        <button class="nav-toggle">☰</button>
                    </nav>
                """,
                "css": """
                    .nav-bar {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 1rem 2rem;
                        background: white;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    
                    .nav-brand {
                        font-size: 1.5rem;
                        font-weight: bold;
                    }
                    
                    .nav-links {
                        display: flex;
                        gap: 2rem;
                        list-style: none;
                        margin: 0;
                        padding: 0;
                    }
                    
                    .nav-links a {
                        text-decoration: none;
                        color: #333;
                        transition: color 0.3s ease;
                    }
                    
                    .nav-links a:hover {
                        color: var(--primary-color);
                    }
                    
                    .nav-toggle {
                        display: none;
                        background: none;
                        border: none;
                        font-size: 1.5rem;
                        cursor: pointer;
                    }
                    
                    @media (max-width: 768px) {
                        .nav-links {
                            display: none;
                        }
                        .nav-toggle {
                            display: block;
                        }
                        .nav-links.active {
                            display: flex;
                            flex-direction: column;
                            position: absolute;
                            top: 100%;
                            left: 0;
                            right: 0;
                            background: white;
                            padding: 1rem;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }
                    }
                """,
                "js": """
                    const navToggle = document.querySelector('.nav-toggle');
                    const navLinks = document.querySelector('.nav-links');
                    
                    navToggle.addEventListener('click', () => {
                        navLinks.classList.toggle('active');
                    });
                """,
                "category": "navigation"
            }
        }

        for name, component in default_components.items():
            if name not in st.session_state.components:
                st.session_state.components[name] = {
                    "id": hashlib.md5(name.encode()).hexdigest()[:8],
                    "html": component["html"].strip(),
                    "css": component["css"].strip(),
                    "js": component["js"].strip(),
                    "category": component["category"],
                    "created": datetime.now().isoformat()
                }

    def render_component_selector(self):
        """Render component selection interface"""
        st.sidebar.subheader("Components")
        
        # Group components by category
        categories = {}
        for name, component in st.session_state.components.items():
            category = component["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append((name, component))

        # Render categories and components
        for category, components in sorted(categories.items()):
            with st.sidebar.expander(category.title()):
                for name, component in sorted(components):
                    if st.button(name, key=f"component_{component['id']}"):
                        self._handle_component_selection(name)

    def _handle_component_selection(self, name: str):
        """Handle component selection"""
        component = st.session_state.components.get(name)
        if component:
            st.session_state.app_state.current_html = component["html"]
            st.session_state.app_state.current_css = component["css"]
            st.session_state.app_state.current_js = component["js"]
            st.session_state.app_state.current_component = name
            SuccessHandler.show_success(f"Loaded component: {name}")
            st.experimental_rerun()

class PreviewSystem:
    """Handle live preview and responsive testing"""
    
    DEVICE_SIZES = {
        "mobile": {"width": 375, "height": 667},
        "tablet": {"width": 768, "height": 1024},
        "desktop": {"width": 1440, "height": 900}
    }

    def render_preview(self, html: str, css: str, js: str):
        """Render preview with controls"""
        # Device controls
        col1, col2, col3 = st.columns([2,2,1])
        
        with col1:
            device = st.selectbox(
                "Device",
                options=list(self.DEVICE_SIZES.keys()),
                index=list(self.DEVICE_SIZES.keys()).index(st.session_state.app_state.device_mode)
            )
            if device != st.session_state.app_state.device_mode:
                st.session_state.app_state.device_mode = device

        with col2:
            cols = st.columns(3)
            with cols[0]:
                st.session_state.app_state.show_grid = st.checkbox(
                    "Grid",
                    value=st.session_state.app_state.show_grid
                )
            with cols[1]:
                st.session_state.app_state.show_outlines = st.checkbox(
                    "Outlines",
                    value=st.session_state.app_state.show_outlines
                )
            with cols[2]:
                st.session_state.app_state.live_preview = st.checkbox(
                    "Live",
                    value=st.session_state.app_state.live_preview
                )

        with col3:
            st.session_state.app_state.zoom_level = st.slider(
                "Zoom",
                0.5,
                2.0,
                st.session_state.app_state.zoom_level
            )

        # Generate and render preview
        preview_html = self._generate_preview_html(html, css, js)
        device = self.DEVICE_SIZES[st.session_state.app_state.device_mode]
        width = int(device["width"] * st.session_state.app_state.zoom_level)
        height = int(device["height"] * st.session_state.app_state.zoom_level)

        st.components.v1.html(
            preview_html,
            height=height,
            scrolling=True
        )

    def _generate_preview_html(self, html: str, css: str, js: str) -> str:
        """Generate complete HTML for preview"""
        debug_styles = """
            * { outline: 1px solid rgba(255, 0, 0, 0.2); }
        """ if st.session_state.app_state.show_outlines else ""

        return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    {css}
                    {debug_styles}
                </style>
            </head>
            <body>
                {html}
                <script>
                    {js}
                </script>
            </body>
            </html>
        """

class VersionControl:
    """Handle code version control and history"""
    
    def __init__(self):
        if 'version_history' not in st.session_state:
            st.session_state.version_history = []
        if 'version_index' not in st.session_state:
            st.session_state.version_index = -1
        self.max_history = 50

    def save_state(self, html: str, css: str, js: str, message: str = ""):
        """Save current state to history"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "html": html,
            "css": css,
            "js": js,
            "message": message,
            "hash": self._generate_hash(html, css, js)
        }
        
        # Remove any forward history if we're not at the latest version
        if st.session_state.version_index < len(st.session_state.version_history) - 1:
            st.session_state.version_history = st.session_state.version_history[:st.session_state.version_index + 1]
        
        st.session_state.version_history.append(state)
        st.session_state.version_index = len(st.session_state.version_history) - 1
        
        # Maintain history limit
        if len(st.session_state.version_history) > self.max_history:
            st.session_state.version_history.pop(0)
            st.session_state.version_index -= 1

    def undo(self) -> Optional[Dict[str, str]]:
        """Undo to previous state"""
        if st.session_state.version_index > 0:
            st.session_state.version_index -= 1
            return self._get_current_state()
        return None

    def redo(self) -> Optional[Dict[str, str]]:
        """Redo to next state"""
        if st.session_state.version_index < len(st.session_state.version_history) - 1:
            st.session_state.version_index += 1
            return self._get_current_state()
        return None

    def _generate_hash(self, html: str, css: str, js: str) -> str:
        """Generate hash for state"""
        content = f"{html}{css}{js}".encode('utf-8')
        return hashlib.sha256(content).hexdigest()[:8]

    def _get_current_state(self) -> Dict[str, str]:
        """Get current state"""
        if not st.session_state.version_history:
            return {"html": "", "css": "", "js": ""}
        state = st.session_state.version_history[st.session_state.version_index]
        return {
            "html": state["html"],
            "css": state["css"],
            "js": state["js"]
        }

class AIIntegration:
    """Handle AI code generation and assistance"""
    
    def __init__(self, groq_client: Optional[Groq] = None):
        self.groq_client = groq_client
        if 'ai_context' not in st.session_state:
            st.session_state.ai_context = []
        self.max_context_length = 5

    async def generate_code(self, prompt: str) -> Optional[Dict[str, str]]:
        """Generate code using Groq"""
        if not self.groq_client:
            ErrorHandler.handle_error(Exception("Groq client not initialized"))
            return None

        try:
            # Update context window
            st.session_state.ai_context.append({"role": "user", "content": prompt})
            if len(st.session_state.ai_context) > self.max_context_length:
                st.session_state.ai_context.pop(0)

            # Generate response
            response = await self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    *st.session_state.ai_context
                ]
            )

            if response.choices:
                content = response.choices[0].message.content
                st.session_state.ai_context.append({"role": "assistant", "content": content})
                return self._parse_code_blocks(content)
            
            return None

        except Exception as e:
            ErrorHandler.handle_error(e, "AI code generation")
            return None

    def _get_system_prompt(self) -> str:
        """Get system prompt for AI"""
        return """You are an expert web developer. Generate clean, modern, and responsive code.
                 Provide code in separate HTML, CSS, and JavaScript blocks.
                 Use semantic HTML5, modern CSS (including flexbox and grid), and ES6+ JavaScript.
                 Include comments explaining key parts of the code."""

    def _parse_code_blocks(self, content: str) -> Dict[str, str]:
        """Parse code blocks from AI response"""
        html_match = re.search(r"```html\n(.*?)\n```", content, re.DOTALL)
        css_match = re.search(r"```css\n(.*?)\n```", content, re.DOTALL)
        js_match = re.search(r"```javascript\n(.*?)\n```", content, re.DOTALL)

        return {
            "html": html_match.group(1) if html_match else "",
            "css": css_match.group(1) if css_match else "",
            "js": js_match.group(1) if js_match else "",
            "explanation": self._extract_explanation(content)
        }

    def _extract_explanation(self, content: str) -> str:
        """Extract explanation from AI response"""
        # Remove code blocks
        clean_content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        return clean_content.strip()

class ProjectManager:
    """Manage project files and settings"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        if 'projects' not in st.session_state:
            st.session_state.projects = {}
        self._load_projects()

    def _load_projects(self):
        """Load existing projects"""
        try:
            for project_dir in self.base_path.iterdir():
                if project_dir.is_dir():
                    config_file = project_dir / "project.json"
                    if config_file.exists():
                        config = json.loads(config_file.read_text())
                        st.session_state.projects[project_dir.name] = config
        except Exception as e:
            ErrorHandler.handle_error(e, "loading projects")

    def create_project(self, name: str, template: str = "blank") -> bool:
        """Create new project"""
        try:
            project_path = self.base_path / name
            if project_path.exists():
                return False

            project_path.mkdir(parents=True)
            self._create_project_structure(project_path, template)
            
            st.session_state.projects[name] = {
                "name": name,
                "template": template,
                "created": datetime.now().isoformat(),
                "components": []
            }
            return True
        except Exception as e:
            ErrorHandler.handle_error(e, "creating project")
            return False

    def _create_project_structure(self, path: Path, template: str):
        """Create project directory structure"""
        (path / "src").mkdir()
        (path / "components").mkdir()
        (path / "assets").mkdir()
        
        # Create project configuration
        config = {
            "name": path.name,
            "template": template,
            "created": datetime.now().isoformat(),
            "components": []
        }
        (path / "project.json").write_text(json.dumps(config, indent=2))

    def save_project(self, name: str, html: str, css: str, js: str) -> bool:
        """Save project files"""
        try:
            project_path = self.base_path / name / "src"
            project_path.mkdir(parents=True, exist_ok=True)

            (project_path / "index.html").write_text(html)
            (project_path / "styles.css").write_text(css)
            (project_path / "script.js").write_text(js)

            return True
        except Exception as e:
            ErrorHandler.handle_error(e, "saving project")
            return False

    def load_project(self, name: str) -> Optional[Dict[str, str]]:
        """Load project files"""
        try:
            project_path = self.base_path / name / "src"
            if not project_path.exists():
                return None

            return {
                "html": (project_path / "index.html").read_text(),
                "css": (project_path / "styles.css").read_text(),
                "js": (project_path / "script.js").read_text()
            }
        except Exception as e:
            ErrorHandler.handle_error(e, "loading project")
            return None

class HTMLEnhancementApp:
    """Main application class"""
    
    def __init__(self):
        self._initialize_app()
        self._setup_ui()

    def _initialize_app(self):
        """Initialize application components"""
        # Initialize session state
        initialize_session_state()
        
        # Initialize Groq client
        self.groq_client = self._setup_groq()
        
        # Initialize components
        self.component_manager = ComponentManager()
        self.preview_system = PreviewSystem()
        self.version_control = VersionControl()
        self.project_manager = ProjectManager(Path("projects"))
        self.ai_integration = AIIntegration(self.groq_client)

    def _setup_groq(self) -> Optional[Groq]:
        """Setup Groq client"""
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                return Groq(api_key=api_key)
            else:
                st.warning("Groq API key not found in environment variables. AI features will be disabled.")
                return None
        except Exception as e:
            st.error(f"Failed to initialize Groq: {str(e)}")
            return None

    def _setup_ui(self):
        """Setup main UI structure"""
        UITheme.inject_styles()
        
        # Main layout
        self._render_sidebar()
        
        main_col1, main_col2 = st.columns([0.4, 0.6])
        
        with main_col1:
            self._render_component_area()
        
        with main_col2:
            self._render_preview_area()
        
        # Show any pending messages
        ErrorHandler.show_error()
        SuccessHandler.display_success()

    def _render_sidebar(self):
        """Render application sidebar"""
        with st.sidebar:
            st.title("Web Builder")
            
            # Project selection
            if st.session_state.projects:
                project = st.selectbox(
                    "Select Project",
                    options=list(st.session_state.projects.keys()),
                    index=0 if not st.session_state.app_state.current_project else 
                          list(st.session_state.projects.keys()).index(st.session_state.app_state.current_project)
                )
                if project != st.session_state.app_state.current_project:
                    self._handle_project_selection(project)
            
            # New project button
            if st.button("New Project"):
                self._show_new_project_dialog()
            
            st.divider()
            
            # Component library
            self.component_manager.render_component_selector()
            
            st.divider()
            
            # Settings and tools
            with st.expander("Settings"):
                st.session_state.app_state.auto_optimize = st.checkbox(
                    "Auto Optimize",
                    value=st.session_state.app_state.auto_optimize
                )
                st.session_state.app_state.live_preview = st.checkbox(
                    "Live Preview",
                    value=st.session_state.app_state.live_preview
                )
            
            with st.expander("Tools"):
                if st.button("Analyze Code"):
                    self._analyze_current_code()
                if st.button("Export"):
                    self._show_export_dialog()

    def _render_component_area(self):
        """Render component editing area"""
        # Code editors
        tabs = st.tabs(["HTML", "CSS", "JavaScript"])
        
        with tabs[0]:
            new_html = st.text_area(
                "HTML",
                value=st.session_state.app_state.current_html,
                height=400,
                key="html_editor"
            )
            
        with tabs[1]:
            new_css = st.text_area(
                "CSS",
                value=st.session_state.app_state.current_css,
                height=400,
                key="css_editor"
            )
            
        with tabs[2]:
            new_js = st.text_area(
                "JavaScript",
                value=st.session_state.app_state.current_js,
                height=400,
                key="js_editor"
            )
        
        # Control buttons
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button("Update"):
                self._handle_code_update(new_html, new_css, new_js)
        with col2:
            if st.button("Undo"):
                self._handle_undo()
        with col3:
            if st.button("Redo"):
                self._handle_redo()

    def _render_preview_area(self):
        """Render preview area"""
        self.preview_system.render_preview(
            st.session_state.app_state.current_html,
            st.session_state.app_state.current_css,
            st.session_state.app_state.current_js
        )

    def _handle_code_update(self, html: str, css: str, js: str):
        """Handle code updates"""
        # Save to version control
        self.version_control.save_state(html, css, js)
        
        # Update current state
        st.session_state.app_state.current_html = html
        st.session_state.app_state.current_css = css
        st.session_state.app_state.current_js = js
        
        # Auto optimize if enabled
        if st.session_state.app_state.auto_optimize:
            self._optimize_code()
        
        # Save project if one is selected
        if st.session_state.app_state.current_project:
            self.project_manager.save_project(
                st.session_state.app_state.current_project,
                html, css, js
            )
        
        # Update preview if live preview is enabled
        if st.session_state.app_state.live_preview:
            st.experimental_rerun()

    def _handle_project_selection(self, project_name: str):
        """Handle project selection"""
        project_data = self.project_manager.load_project(project_name)
        if project_data:
            st.session_state.app_state.current_project = project_name
            st.session_state.app_state.current_html = project_data["html"]
            st.session_state.app_state.current_css = project_data["css"]
            st.session_state.app_state.current_js = project_data["js"]
            SuccessHandler.show_success(f"Loaded project: {project_name}")
            st.experimental_rerun()

    def _handle_undo(self):
        """Handle undo action"""
        state = self.version_control.undo()
        if state:
            st.session_state.app_state.current_html = state["html"]
            st.session_state.app_state.current_css = state["css"]
            st.session_state.app_state.current_js = state["js"]
            st.experimental_rerun()

    def _handle_redo(self):
        """Handle redo action"""
        state = self.version_control.redo()
        if state:
            st.session_state.app_state.current_html = state["html"]
            st.session_state.app_state.current_css = state["css"]
            st.session_state.app_state.current_js = state["js"]
            st.experimental_rerun()

    def _optimize_code(self):
        """Optimize current code"""
        st.session_state.app_state.current_html = self._optimize_html(st.session_state.app_state.current_html)
        st.session_state.app_state.current_css = self._optimize_css(st.session_state.app_state.current_css)
        st.session_state.app_state.current_js = self._optimize_js(st.session_state.app_state.current_js)

    @staticmethod
    def _optimize_html(html: str) -> str:
        """Optimize HTML code"""
        soup = BeautifulSoup(html, 'html.parser')
        return soup.prettify()

    @staticmethod
    def _optimize_css(css: str) -> str:
        """Optimize CSS code"""
        # Remove comments and unnecessary whitespace
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        css = re.sub(r'\s+', ' ', css)
        return css.strip()

    @staticmethod
    def _optimize_js(js: str) -> str:
        """Optimize JavaScript code"""
        # Remove comments and unnecessary whitespace
        js = re.sub(r'//.*?\n|/\*.*?\*/', '', js, flags=re.DOTALL)
        js = re.sub(r'\s+', ' ', js)
        return js.strip()

    def _show_new_project_dialog(self):
        """Show new project creation dialog"""
        with st.form("new_project"):
            name = st.text_input("Project Name")
            template = st.selectbox(
                "Template",
                options=["blank", "landing-page", "portfolio"]
            )
            submitted = st.form_submit_button("Create")
            
            if submitted and name:
                if self.project_manager.create_project(name, template):
                    SuccessHandler.show_success(f"Created project: {name}")
                    self._handle_project_selection(name)

    def _show_export_dialog(self):
        """Show export options dialog"""
        with st.form("export"):
            export_type = st.selectbox(
                "Export As",
                options=["Single File", "Component", "Project"]
            )
            submitted = st.form_submit_button("Export")
            
            if submitted:
                if export_type == "Single File":
                    self._export_as_single_file()
                elif export_type == "Component":
                    self._export_as_component()
                else:
                    self._export_as_project()

    def _export_as_single_file(self):
        """Export as single HTML file"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
{st.session_state.app_state.current_css}
    </style>
</head>
<body>
{st.session_state.app_state.current_html}
    <script>
{st.session_state.app_state.current_js}
    </script>
</body>
</html>
"""
        st.download_button(
            "Download HTML",
            html,
            file_name="component.html",
            mime="text/html"
        )

class CodeAnalyzer:
    """Analyze and optimize code"""
    
    @staticmethod
    def analyze_html(html: str) -> Dict[str, Any]:
        """Analyze HTML structure and accessibility"""
        soup = BeautifulSoup(html, 'html.parser')
        return {
            "elements": len(soup.find_all()),
            "headings": len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            "images": len(soup.find_all('img')),
            "links": len(soup.find_all('a')),
            "forms": len(soup.find_all('form')),
            "missing_alts": len([img for img in soup.find_all('img') if not img.get('alt')]),
            "semantic_elements": len(soup.find_all(['header', 'nav', 'main', 'article', 'section', 'aside', 'footer']))
        }

    @staticmethod
    def analyze_css(css: str) -> Dict[str, Any]:
        """Analyze CSS complexity and usage"""
        selectors = re.findall(r'([^{]+){', css)
        properties = re.findall(r'([^:]+):', css)
        return {
            "selectors": len(selectors),
            "properties": len(properties),
            "file_size": len(css.encode('utf-8')),
            "media_queries": len(re.findall(r'@media', css)),
            "colors": len(set(re.findall(r'#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)', css)))
        }

    @staticmethod
    def analyze_js(js: str) -> Dict[str, Any]:
        """Analyze JavaScript complexity"""
        return {
            "file_size": len(js.encode('utf-8')),
            "functions": len(re.findall(r'function\s+\w+\s*\(|const\s+\w+\s*=\s*\([^)]*\)\s*=>', js)),
            "event_listeners": len(re.findall(r'addEventListener', js)),
            "variables": len(re.findall(r'var\s+\w+|let\s+\w+|const\s+\w+', js))
        }

class ExportManager:
    """Handle code export in various formats"""
    
    @staticmethod
    def export_as_component(html: str, css: str, js: str, name: str) -> Dict[str, str]:
        """Export as reusable component"""
        return {
            f"{name}.html": html,
            f"{name}.css": css,
            f"{name}.js": js,
            f"{name}.json": json.dumps({
                "name": name,
                "created": datetime.now().isoformat(),
                "dependencies": ExportManager._extract_dependencies(html, css, js)
            }, indent=2)
        }

    @staticmethod
    def export_as_project(html: str, css: str, js: str, name: str) -> Dict[str, str]:
        """Export as complete project"""
        return {
            "index.html": f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
{html}
    <script src="script.js"></script>
</body>
</html>""",
            "styles.css": css,
            "script.js": js,
            "README.md": f"""
# {name}

Generated with Web Component Builder

## Structure
- `index.html`: Main HTML file
- `styles.css`: Stylesheet
- `script.js`: JavaScript code

## Usage
Open `index.html` in a web browser to view the component.
"""
        }

    @staticmethod
    def _extract_dependencies(html: str, css: str, js: str) -> List[str]:
        """Extract external dependencies from code"""
        deps = []
        
        # Check for external stylesheets
        for link in re.findall(r'<link[^>]+href=["\'](.*?)["\']', html):
            if not link.startswith(('data:', '#')):
                deps.append(link)
        
        # Check for external scripts
        for script in re.findall(r'<script[^>]+src=["\'](.*?)["\']', html):
            if not script.startswith(('data:', '#')):
                deps.append(script)
        
        # Check for CSS imports
        deps.extend(re.findall(r'@import\s+["\']([^"\']+)["\']', css))
        
        return list(set(deps))

class Utilities:
    """General utility functions"""
    
    @staticmethod
    def generate_component_id() -> str:
        """Generate unique component ID"""
        return hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Sanitize filename for safe saving"""
        return re.sub(r'[^\w\-\.]', '_', name)

    @staticmethod
    def format_file_size(size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} GB"

    @staticmethod
    def create_zip_file(files: Dict[str, str]) -> bytes:
        """Create ZIP file from dictionary of files"""
        import io
        import zipfile
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in files.items():
                zip_file.writestr(filename, content)
        
        return zip_buffer.getvalue()

# Add these methods to HTMLEnhancementApp class
def _analyze_current_code(self):
    """Analyze current code and show results"""
    html_analysis = CodeAnalyzer.analyze_html(st.session_state.app_state.current_html)
    css_analysis = CodeAnalyzer.analyze_css(st.session_state.app_state.current_css)
    js_analysis = CodeAnalyzer.analyze_js(st.session_state.app_state.current_js)
    
    st.write("### Code Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("#### HTML")
        for key, value in html_analysis.items():
            st.write(f"- {key.replace('_', ' ').title()}: {value}")
    
    with col2:
        st.write("#### CSS")
        for key, value in css_analysis.items():
            if key == 'file_size':
                value = Utilities.format_file_size(value)
            st.write(f"- {key.replace('_', ' ').title()}: {value}")
    
    with col3:
        st.write("#### JavaScript")
        for key, value in js_analysis.items():
            if key == 'file_size':
                value = Utilities.format_file_size(value)
            st.write(f"- {key.replace('_', ' ').title()}: {value}")

def _export_as_component(self):
    """Export current code as component"""
    name = st.text_input("Component Name", "my_component")
    if name:
        files = ExportManager.export_as_component(
            st.session_state.app_state.current_html,
            st.session_state.app_state.current_css,
            st.session_state.app_state.current_js,
            Utilities.sanitize_filename(name)
        )
        
        st.download_button(
            "Download Component",
            data=Utilities.create_zip_file(files),
            file_name=f"{name}.zip",
            mime="application/zip"
        )

def _export_as_project(self):
    """Export current code as project"""
    name = st.text_input("Project Name", "my_project")
    if name:
        files = ExportManager.export_as_project(
            st.session_state.app_state.current_html,
            st.session_state.app_state.current_css,
            st.session_state.app_state.current_js,
            Utilities.sanitize_filename(name)
        )
        
        st.download_button(
            "Download Project",
            data=Utilities.create_zip_file(files),
            file_name=f"{name}.zip",
            mime="application/zip"
        )

# Run the application
if __name__ == "__main__":
    app = HTMLEnhancementApp()