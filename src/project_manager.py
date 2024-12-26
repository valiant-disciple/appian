import streamlit as st
from pathlib import Path
from typing import Dict, Optional, Any, List
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from .state import ErrorHandler, SuccessHandler

@dataclass
class ProjectTemplate:
    """Project template structure"""
    html: str 
    css: str
    js: str

@dataclass
class ProjectConfig:
    """Project configuration structure"""
    name: str
    description: str
    created: datetime
    modified: datetime
    template: str
    components: List[str]
    settings: Dict[str, Any]
    author: str = ""
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            **asdict(self),
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat()
        }

@dataclass
class Project:
    """Project structure"""
    config: ProjectConfig
    html: str
    css: str
    js: str
    assets: Dict[str, bytes] = None
    
    def __post_init__(self):
        if self.assets is None:
            self.assets = {}

class ProjectManager:
    """Manage project files and settings"""
    
    TEMPLATES: Dict[str, ProjectTemplate] = {
        "blank": ProjectTemplate(
            html="""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>New Project</title>
                </head>
                <body>
                    <h1>Welcome to your new project!</h1>
                </body>
                </html>
            """,
            css="""
                body {
                    font-family: system-ui, -apple-system, sans-serif;
                    line-height: 1.5;
                    padding: 2rem;
                }
                
                h1 {
                    color: #2563eb;
                }
            """,
            js="""
                console.log('Project initialized');
            """
        ),
        "landing": ProjectTemplate(
            html="""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Landing Page</title>
                </head>
                <body>
                    <header class="hero">
                        <nav class="nav">
                            <div class="logo">Logo</div>
                            <div class="nav-links">
                                <a href="#features">Features</a>
                                <a href="#about">About</a>
                                <a href="#contact">Contact</a>
                            </div>
                        </nav>
                        <div class="hero-content">
                            <h1>Welcome to Our Platform</h1>
                            <p>The best solution for your needs</p>
                            <button class="cta-button">Get Started</button>
                        </div>
                    </header>
                </body>
                </html>
            """,
            css="""
                :root {
                    --primary-color: #2563eb;
                    --text-color: #1f2937;
                    --background-color: #f8fafc;
                }
                
                body {
                    margin: 0;
                    font-family: system-ui, -apple-system, sans-serif;
                    color: var(--text-color);
                    background: var(--background-color);
                }
                
                .hero {
                    min-height: 100vh;
                    padding: 2rem;
                    display: flex;
                    flex-direction: column;
                }
                
                .nav {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1rem 0;
                }
                
                .nav-links {
                    display: flex;
                    gap: 2rem;
                }
                
                .nav-links a {
                    color: var(--text-color);
                    text-decoration: none;
                    transition: color 0.3s ease;
                }
                
                .nav-links a:hover {
                    color: var(--primary-color);
                }
                
                .hero-content {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    text-align: center;
                    max-width: 800px;
                    margin: 0 auto;
                }
                
                .hero-content h1 {
                    font-size: 3rem;
                    margin-bottom: 1rem;
                }
                
                .cta-button {
                    margin-top: 2rem;
                    padding: 1rem 2rem;
                    background: var(--primary-color);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 1.1rem;
                    cursor: pointer;
                    transition: transform 0.3s ease;
                }
                
                .cta-button:hover {
                    transform: translateY(-2px);
                }
            """,
            js="""
                document.querySelector('.cta-button').addEventListener('click', () => {
                    console.log('CTA clicked');
                });
            """
        )
    }
    
    def __init__(self, base_path: Path):
        """Initialize project manager"""
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        if 'projects' not in st.session_state:
            st.session_state.projects = {}
        self._load_projects()

    def _load_projects(self) -> None:
        """Load existing projects"""
        try:
            for project_dir in self.base_path.iterdir():
                if project_dir.is_dir():
                    config_file = project_dir / "project.json"
                    if config_file.exists():
                        config_data = json.loads(config_file.read_text())
                        config_data['created'] = datetime.fromisoformat(config_data['created'])
                        config_data['modified'] = datetime.fromisoformat(config_data['modified'])
                        st.session_state.projects[project_dir.name] = ProjectConfig(**config_data)
        except Exception as e:
            ErrorHandler.handle_error(e, "loading projects")

    def create_project(self, name: str, description: str = "", template: str = "blank") -> bool:
        """Create new project"""
        try:
            project_path = self.base_path / name
            if project_path.exists():
                ErrorHandler.handle_error(Exception(f"Project {name} already exists"))
                return False

            # Create project structure
            project_path.mkdir(parents=True)
            (project_path / "src").mkdir()
            (project_path / "assets").mkdir()
            
            # Get template content
            template_content = self.TEMPLATES.get(template, self.TEMPLATES["blank"])
            
            # Create project config
            config = ProjectConfig(
                name=name,
                description=description,
                created=datetime.now(),
                modified=datetime.now(),
                template=template,
                components=[],
                settings={}
            )
            
            # Save project files
            self._save_project_files(project_path, template_content, config)
            
            # Update session state
            st.session_state.projects[name] = config
            
            SuccessHandler.show_success(f"Created project: {name}")
            return True
            
        except Exception as e:
            ErrorHandler.handle_error(e, "creating project")
            return False

    def _save_project_files(self, path: Path, template: ProjectTemplate, config: ProjectConfig) -> None:
        """Save project files"""
        src_path = path / "src"
        
        # Save source files
        (src_path / "index.html").write_text(template.html.strip())
        (src_path / "styles.css").write_text(template.css.strip())
        (src_path / "script.js").write_text(template.js.strip())
        
        # Save config
        (path / "project.json").write_text(json.dumps(config.to_dict(), indent=2))

    def load_project(self, name: str) -> Optional[Project]:
        """Load project files"""
        try:
            project_path = self.base_path / name
            if not project_path.exists():
                return None

            # Load config
            config_data = json.loads((project_path / "project.json").read_text())
            config_data['created'] = datetime.fromisoformat(config_data['created'])
            config_data['modified'] = datetime.fromisoformat(config_data['modified'])
            config = ProjectConfig(**config_data)
            
            # Load source files
            src_path = project_path / "src"
            project = Project(
                config=config,
                html=(src_path / "index.html").read_text(),
                css=(src_path / "styles.css").read_text(),
                js=(src_path / "script.js").read_text()
            )
            
            return project
            
        except Exception as e:
            ErrorHandler.handle_error(e, "loading project")
            return None

    def save_project(self, name: str, html: str, css: str, js: str) -> bool:
        """Save project files"""
        try:
            project_path = self.base_path / name
            if not project_path.exists():
                return False

            src_path = project_path / "src"
            
            # Update source files
            (src_path / "index.html").write_text(html)
            (src_path / "styles.css").write_text(css)
            (src_path / "script.js").write_text(js)
            
            # Update config
            if config := st.session_state.projects.get(name):
                config.modified = datetime.now()
                (project_path / "project.json").write_text(
                    json.dumps(config.to_dict(), indent=2)
                )
            
            SuccessHandler.show_success(f"Saved project: {name}")
            return True
            
        except Exception as e:
            ErrorHandler.handle_error(e, "saving project")
            return False

    def delete_project(self, name: str) -> bool:
        """Delete project"""
        try:
            project_path = self.base_path / name
            if project_path.exists():
                import shutil
                shutil.rmtree(project_path)
                del st.session_state.projects[name]
                SuccessHandler.show_success(f"Deleted project: {name}")
                return True
            return False
            
        except Exception as e:
            ErrorHandler.handle_error(e, "deleting project")
            return False

    def get_project_list(self) -> List[ProjectConfig]:
        """Get list of all projects"""
        return list(st.session_state.projects.values())

    def project_exists(self, name: str) -> bool:
        """Check if project exists"""
        return name in st.session_state.projects