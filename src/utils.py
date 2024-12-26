from typing import Dict, Any, Optional, List
import hashlib
from datetime import datetime
import re
from pathlib import Path
import json
from dataclasses import dataclass

class FileUtils:
    """File handling utilities"""
    
    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Sanitize filename for safe saving"""
        # Replace invalid characters with underscore
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Remove leading/trailing spaces and dots
        name = name.strip('. ')
        return name if name else 'untitled'

    @staticmethod
    def format_file_size(size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} GB"

    @staticmethod
    def read_json_file(path: Path) -> Optional[Dict[str, Any]]:
        """Read and parse JSON file"""
        try:
            if path.exists():
                return json.loads(path.read_text())
            return None
        except Exception as e:
            print(f"Error reading JSON file: {e}")
            return None

    @staticmethod
    def write_json_file(path: Path, data: Dict[str, Any], indent: int = 2) -> bool:
        """Write data to JSON file"""
        try:
            path.write_text(json.dumps(data, indent=indent))
            return True
        except Exception as e:
            print(f"Error writing JSON file: {e}")
            return False

    @staticmethod
    def ensure_directory(path: Path) -> bool:
        """Ensure directory exists"""
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False

class HashUtils:
    """Hash generation utilities"""
    
    @staticmethod
    def generate_file_hash(content: str) -> str:
        """Generate hash from file content"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:8]

    @staticmethod
    def generate_id(prefix: str = "") -> str:
        """Generate unique ID"""
        timestamp = datetime.now().timestamp()
        hash_input = f"{prefix}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:8]

class CodeUtils:
    """Code manipulation utilities"""
    
    @staticmethod
    def extract_css_variables(css: str) -> Dict[str, str]:
        """Extract CSS custom properties"""
        variables = {}
        for match in re.finditer(r'--([^:]+):\s*([^;]+);', css):
            name, value = match.groups()
            variables[name.strip()] = value.strip()
        return variables

    @staticmethod
    def replace_css_variables(css: str, variables: Dict[str, str]) -> str:
        """Replace CSS custom properties"""
        for name, value in variables.items():
            css = re.sub(
                f'var\\(--{name}\\)',
                value,
                css
            )
        return css

    @staticmethod
    def extract_js_functions(js: str) -> List[str]:
        """Extract function names from JavaScript"""
        functions = []
        for match in re.finditer(r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)', js):
            functions.append(match.group(1))
        return functions

    @staticmethod
    def format_html(html: str, indent: int = 2) -> str:
        """Format HTML with proper indentation"""
        from bs4 import BeautifulSoup
        return BeautifulSoup(html, 'html.parser').prettify(indent_width=indent)

    @staticmethod
    def format_css(css: str) -> str:
        """Format CSS with proper spacing"""
        # Remove extra spaces
        css = re.sub(r'\s+', ' ', css)
        # Add newlines after closing braces
        css = re.sub(r'}', '}\n', css)
        # Add newlines after semicolons
        css = re.sub(r';', ';\n    ', css)
        # Add space after property colons
        css = re.sub(r':\s*', ': ', css)
        return css.strip()

    @staticmethod
    def format_js(js: str) -> str:
        """Format JavaScript with proper spacing"""
        # Add space after keywords
        js = re.sub(r'(if|for|while|function|return|var|let|const)\(', r'\1 (', js)
        # Add space around operators
        js = re.sub(r'([=+\-*/<>])', r' \1 ', js)
        # Remove extra spaces
        js = re.sub(r'\s+', ' ', js)
        # Add newlines after semicolons
        js = re.sub(r';', ';\n', js)
        # Add newlines after closing braces
        js = re.sub(r'}', '}\n', js)
        return js.strip()

class Templates:
    """Code templates and snippets"""
    
    @staticmethod
    def get_template(name: str) -> Dict[str, str]:
        """Get template by name"""
        templates = {
            "modal": {
                "html": """
                    <div class="modal">
                        <div class="modal-content">
                            <button class="modal-close">&times;</button>
                            <h2 class="modal-title">Modal Title</h2>
                            <div class="modal-body">
                                Modal content goes here
                            </div>
                        </div>
                    </div>
                    <button class="modal-trigger">Open Modal</button>
                """,
                "css": """
                    .modal {
                        display: none;
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(0, 0, 0, 0.5);
                        align-items: center;
                        justify-content: center;
                    }
                    
                    .modal.active {
                        display: flex;
                    }
                    
                    .modal-content {
                        background: white;
                        padding: 2rem;
                        border-radius: 8px;
                        position: relative;
                        max-width: 500px;
                        width: 90%;
                    }
                    
                    .modal-close {
                        position: absolute;
                        top: 1rem;
                        right: 1rem;
                        background: none;
                        border: none;
                        font-size: 1.5rem;
                        cursor: pointer;
                    }
                    
                    .modal-title {
                        margin-top: 0;
                    }
                    
                    .modal-trigger {
                        padding: 0.5rem 1rem;
                        background: #007bff;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    }
                """,
                "js": """
                    const modal = document.querySelector('.modal');
                    const modalTrigger = document.querySelector('.modal-trigger');
                    const modalClose = document.querySelector('.modal-close');
                    
                    modalTrigger.addEventListener('click', () => {
                        modal.classList.add('active');
                    });
                    
                    modalClose.addEventListener('click', () => {
                        modal.classList.remove('active');
                    });
                    
                    modal.addEventListener('click', (e) => {
                        if (e.target === modal) {
                            modal.classList.remove('active');
                        }
                    });
                """
            }
        }
        
        return templates.get(name, {
            "html": "",
            "css": "",
            "js": ""
        })

    @staticmethod
    def get_snippet(name: str) -> str:
        """Get code snippet by name"""
        snippets = {
            "flex_center": """
                display: flex;
                align-items: center;
                justify-content: center;
            """,
            "media_query": """
                @media (max-width: 768px) {
                    /* Mobile styles */
                }
            """,
            "event_listener": """
                element.addEventListener('event', (e) => {
                    // Handle event
                });
            """
        }
        return snippets.get(name, "")

    @staticmethod
    def get_component_structure() -> Dict[str, List[str]]:
        """Get recommended component structure"""
        return {
            "required": [
                "index.html",
                "styles.css",
                "script.js"
            ],
            "optional": [
                "README.md",
                "assets/",
                "tests/",
                "docs/"
            ]
        }