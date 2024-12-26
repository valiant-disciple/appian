import streamlit as st
from typing import Dict, Any, Optional, List
import hashlib
from datetime import datetime
from .state import StateManager, SuccessHandler, ErrorHandler
from dataclasses import dataclass

@dataclass
class Component:
    """Component structure"""
    id: str
    name: str
    html: str
    css: str
    js: str
    category: str
    created: datetime
    description: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class ComponentTemplate:
    """Component template structure"""
    html: str
    css: str
    js: str
    category: str
    description: str
    tags: List[str]

class ComponentManager:
    """Manage component library and templates"""
    
    # Default component templates
    DEFAULT_COMPONENTS: Dict[str, ComponentTemplate] = {
        "modern_button": ComponentTemplate(
            html="""
                <button class="modern-button">
                    <span class="button-text">Click Me</span>
                    <span class="button-icon">→</span>
                </button>
            """,
            css="""
                .modern-button {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    padding: 12px 24px;
                    background: linear-gradient(45deg, #6366f1, #8b5cf6);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                
                .modern-button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
                }
                
                .button-icon {
                    transition: transform 0.3s ease;
                }
                
                .modern-button:hover .button-icon {
                    transform: translateX(4px);
                }
            """,
            js="""
                document.querySelector('.modern-button').addEventListener('click', function() {
                    this.classList.add('clicked');
                    setTimeout(() => this.classList.remove('clicked'), 200);
                });
            """,
            category="buttons",
            description="Modern gradient button with hover effects",
            tags=["button", "interactive", "gradient"]
        ),
        
        "card_component": ComponentTemplate(
            html="""
                <div class="card">
                    <div class="card-image">
                        <img src="https://picsum.photos/300/200" alt="Card image">
                    </div>
                    <div class="card-content">
                        <h3 class="card-title">Card Title</h3>
                        <p class="card-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
                        <button class="card-button">Learn More</button>
                    </div>
                </div>
            """,
            css="""
                .card {
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                    max-width: 300px;
                }
                
                .card:hover {
                    transform: translateY(-4px);
                }
                
                .card-image img {
                    width: 100%;
                    height: 200px;
                    object-fit: cover;
                }
                
                .card-content {
                    padding: 1.5rem;
                }
                
                .card-title {
                    margin: 0 0 0.5rem;
                    color: #1a1a1a;
                }
                
                .card-text {
                    color: #666;
                    line-height: 1.5;
                    margin-bottom: 1rem;
                }
                
                .card-button {
                    background: #3b82f6;
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 6px;
                    cursor: pointer;
                    transition: background 0.3s ease;
                }
                
                .card-button:hover {
                    background: #2563eb;
                }
            """,
            js="""
                document.querySelector('.card-button').addEventListener('click', () => {
                    console.log('Card button clicked');
                });
            """,
            category="cards",
            description="Modern card component with image and hover effects",
            tags=["card", "container", "interactive"]
        )
    }

    def __init__(self):
        """Initialize component manager"""
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize default components"""
        if 'components' not in st.session_state:
            st.session_state.components = {}
        
        # Add default components if they don't exist
        for name, template in self.DEFAULT_COMPONENTS.items():
            if name not in st.session_state.components:
                self.add_component(
                    name=name,
                    html=template.html.strip(),
                    css=template.css.strip(),
                    js=template.js.strip(),
                    category=template.category,
                    description=template.description,
                    tags=template.tags
                )

    def add_component(self, name: str, html: str, css: str, js: str, 
                     category: str, description: str = "", tags: List[str] = None) -> bool:
        """Add new component to library"""
        try:
            component_id = hashlib.md5(f"{name}_{datetime.now().timestamp()}".encode()).hexdigest()[:8]
            
            component = Component(
                id=component_id,
                name=name,
                html=html,
                css=css,
                js=js,
                category=category,
                created=datetime.now(),
                description=description,
                tags=tags or []
            )
            
            st.session_state.components[name] = vars(component)
            return True
            
        except Exception as e:
            ErrorHandler.handle_error(e, "adding component")
            return False

    def render_component_selector(self) -> None:
        """Render component selection interface"""
        # Group components by category
        categories = self._group_components_by_category()
        
        # Search box
        search_query = st.text_input("Search components", key="component_search").lower()
        
        # Render categories and components
        for category, components in sorted(categories.items()):
            # Filter components based on search
            if search_query:
                components = [
                    (name, comp) for name, comp in components
                    if search_query in name.lower() or
                       search_query in comp.get('description', '').lower() or
                       any(search_query in tag.lower() for tag in comp.get('tags', []))
                ]
                if not components:
                    continue
            
            with st.expander(f"{category.title()} ({len(components)})"):
                for name, component in sorted(components):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        if st.button(
                            name,
                            key=f"component_{component['id']}",
                            help=component.get('description', '')
                        ):
                            self._handle_component_selection(name)
                    with col2:
                        st.markdown(
                            " ".join(f"`{tag}`" for tag in component.get('tags', []))
                        )

    def _group_components_by_category(self) -> Dict[str, List[tuple]]:
        """Group components by their categories"""
        categories: Dict[str, List[tuple]] = {}
        for name, component in st.session_state.components.items():
            category = component["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append((name, component))
        return categories

    def _handle_component_selection(self, name: str) -> None:
        """Handle component selection"""
        component = st.session_state.components.get(name)
        if component:
            StateManager.update_state(
                current_html=component["html"],
                current_css=component["css"],
                current_js=component["js"],
                current_component=name
            )
            SuccessHandler.show_success(f"Loaded component: {name}")
            st.experimental_rerun()

    def get_component(self, name: str) -> Optional[Component]:
        """Get component by name"""
        if data := st.session_state.components.get(name):
            return Component(**data)
        return None

    def delete_component(self, name: str) -> bool:
        """Delete component from library"""
        try:
            if name in st.session_state.components:
                del st.session_state.components[name]
                return True
            return False
        except Exception as e:
            ErrorHandler.handle_error(e, "deleting component")
            return False