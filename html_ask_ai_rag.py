from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set, Union, Tuple
from bs4 import BeautifulSoup, Tag
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress
from rich.syntax import Syntax
from rich.panel import Panel
import os
import tempfile
import webbrowser
from groq import Groq
import re
import json
import logging
from pathlib import Path
from enum import Enum
import copy
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class StyleState:
    """Component style states"""
    normal: Dict[str, str] = field(default_factory=dict)
    hover: Dict[str, str] = field(default_factory=dict)
    active: Dict[str, str] = field(default_factory=dict)
    focus: Dict[str, str] = field(default_factory=dict)
    disabled: Dict[str, str] = field(default_factory=dict)

@dataclass
class Animation:
    """Animation configuration"""
    name: str
    keyframes: Dict[str, Dict[str, str]]
    duration: str = "0.3s"
    timing: str = "ease"
    delay: str = "0s"
    iteration: str = "1"
    direction: str = "normal"
    fill_mode: str = "forwards"

@dataclass
class Position:
    """Enhanced position handling"""
    type: str  # 'absolute', 'relative', 'fixed', 'sticky'
    target: str  # Selector or 'viewport'
    x: Union[int, str]  # Pixel value or percentage
    y: Union[int, str]
    z_index: Optional[int] = None
    anchor: str = 'top-left'  # top-left, center, bottom-right, etc.
    margin: Dict[str, str] = field(default_factory=dict)
    responsive: bool = True
    grid_area: Optional[str] = None

@dataclass
class ComponentTemplate:
    """Enhanced component template"""
    name: str
    html: str
    styles: Dict[str, StyleState]
    parameters: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, str] = field(default_factory=dict)
    events: Dict[str, str] = field(default_factory=dict)
    aria: Dict[str, str] = field(default_factory=dict)
    required_classes: List[str] = field(default_factory=list)
    responsive_rules: Dict[str, Dict[str, str]] = field(default_factory=dict)
    animations: Dict[str, Animation] = field(default_factory=dict)
    grid_area: Optional[str] = None
    relationships: Dict[str, List[str]] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate template completeness"""
        try:
            return all([
                bool(self.name),
                bool(self.html),
                isinstance(self.styles, dict),
                all(isinstance(state, StyleState) for state in self.styles.values())
            ])
        except Exception as e:
            logger.error(f"Template validation error: {str(e)}")
            return False

@dataclass
class ComponentAddition:
    """Component addition details"""
    template: ComponentTemplate
    position: Position
    parameters: Dict[str, Any]
    custom_styles: Dict[str, StyleState] = field(default_factory=dict)
    custom_classes: List[str] = field(default_factory=list)
    custom_attributes: Dict[str, str] = field(default_factory=dict)
    custom_events: Dict[str, str] = field(default_factory=dict)
    custom_aria: Dict[str, str] = field(default_factory=dict)
    animations: Dict[str, Animation] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate component addition"""
        return bool(self.template and self.template.validate())

@dataclass
class HTMLVariation:
    """Tracks HTML modifications"""
    html: str
    changes: List[str]
    components_added: List[ComponentAddition]
    styles_modified: Dict[str, Dict[str, str]]
    elements_removed: List[str]
    elements_modified: Dict[str, Dict[str, Any]]

    def validate(self) -> bool:
        """Validate variation completeness"""
        try:
            if not isinstance(self.changes, list):
                return False
            if not isinstance(self.components_added, list):
                return False
            if not isinstance(self.styles_modified, dict):
                return False
            if not isinstance(self.elements_removed, list):
                return False
            if not isinstance(self.elements_modified, dict):
                return False
            return True
        except Exception as e:
            logger.error(f"Variation validation error: {str(e)}")
            return False

@dataclass
class GridTemplate:
    """Grid layout template"""
    name: str
    areas: List[str]
    columns: str
    rows: str
    gap: str
    responsive: Dict[str, Dict[str, str]] = field(default_factory=dict)

@dataclass
class SiteTheme:
    """Enhanced site theme management"""
    colors: Dict[str, str] = field(default_factory=dict)
    fonts: Dict[str, Dict[str, str]] = field(default_factory=dict)
    spacing: Dict[str, str] = field(default_factory=dict)
    breakpoints: Dict[str, str] = field(default_factory=dict)
    shadows: Dict[str, str] = field(default_factory=dict)
    transitions: Dict[str, str] = field(default_factory=dict)
    z_indices: Dict[str, int] = field(default_factory=dict)
    border_radius: Dict[str, str] = field(default_factory=dict)
    components: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    grid_templates: Dict[str, GridTemplate] = field(default_factory=dict)
    animations: Dict[str, Animation] = field(default_factory=dict)

    def __post_init__(self):
        self._init_default_theme()

    def _init_default_theme(self):
        """Initialize comprehensive default theme"""
        # Colors with semantic meaning
        self.colors.update({
            'primary': '#3490dc',
            'secondary': '#6574cd',
            'success': '#38c172',
            'danger': '#e3342f',
            'warning': '#f6993f',
            'info': '#6cb2eb',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'background': '#ffffff',
            'text': '#2d3748',
            'muted': '#718096'
        })

        # Typography system
        self.fonts.update({
            'primary': {
                'family': 'system-ui, -apple-system, sans-serif',
                'weights': {
                    'light': '300',
                    'regular': '400',
                    'medium': '500',
                    'bold': '700'
                },
                'sizes': {
                    'xs': '0.75rem',
                    'sm': '0.875rem',
                    'base': '1rem',
                    'lg': '1.125rem',
                    'xl': '1.25rem'
                }
            },
            'heading': {
                'family': 'system-ui, -apple-system, sans-serif',
                'weights': {
                    'regular': '600',
                    'bold': '800'
                }
            },
            'mono': {
                'family': 'ui-monospace, monospace',
                'weights': {
                    'regular': '400',
                    'bold': '700'
                }
            }
        })

        # Spacing system
        self.spacing.update({
            'px': '1px',
            'xs': '0.25rem',
            'sm': '0.5rem',
            'md': '1rem',
            'lg': '1.5rem',
            'xl': '2rem',
            '2xl': '2.5rem',
            '3xl': '3rem'
        })

        # Responsive breakpoints
        self.breakpoints.update({
            'sm': '640px',
            'md': '768px',
            'lg': '1024px',
            'xl': '1280px',
            '2xl': '1536px'
        })

        # Shadow system
        self.shadows.update({
            'sm': '0 1px 2px rgba(0, 0, 0, 0.05)',
            'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
            'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
        })

        # Transition presets
        self.transitions.update({
            'fast': 'all 0.15s ease-in-out',
            'normal': 'all 0.3s ease-in-out',
            'slow': 'all 0.5s ease-in-out'
        })

        # Z-index scale
        self.z_indices.update({
            'below': -1,
            'base': 0,
            'above': 1,
            'dropdown': 1000,
            'sticky': 1100,
            'modal': 1200,
            'popover': 1300,
            'tooltip': 1400
        })

        # Border radius system
        self.border_radius.update({
            'none': '0',
            'sm': '0.125rem',
            'md': '0.25rem',
            'lg': '0.5rem',
            'xl': '1rem',
            'full': '9999px'
        })

class ComponentManager:
    """Enhanced component management system"""
    
    def __init__(self, theme: Optional[SiteTheme] = None):
        self.logger = logging.getLogger(__name__)
        self.theme = theme or SiteTheme()
        self.templates = self._initialize_templates()
        self.instances: Dict[str, List[Tag]] = {}
        self.relationships: Dict[str, Set[str]] = {}

    def _initialize_templates(self) -> Dict[str, ComponentTemplate]:
        """Initialize comprehensive component templates"""
        templates = {}
        
        # Button Component
        templates['button'] = ComponentTemplate(
            name="button",
            html='''
                <button 
                    type="{type}" 
                    class="custom-btn {size} {variant} {additional_classes}"
                    {additional_attributes}
                >
                    {text}
                    {icon}
                </button>
            ''',
            styles={
                "default": StyleState(
                    normal={
                        "display": "inline-flex",
                        "align-items": "center",
                        "justify-content": "center",
                        "padding": "0.75rem 1.5rem",
                        "font-weight": "500",
                        "border-radius": "0.375rem",
                        "transition": "all 0.2s",
                        "cursor": "pointer",
                        "outline": "none",
                        "border": "1px solid transparent"
                    },
                    hover={
                        "transform": "translateY(-1px)",
                        "box-shadow": "0 4px 6px rgba(0,0,0,0.1)"
                    },
                    active={
                        "transform": "translateY(0)",
                        "box-shadow": "0 2px 4px rgba(0,0,0,0.1)"
                    },
                    focus={
                        "ring": "2px",
                        "ring-offset": "2px",
                        "ring-color": "var(--primary-500)"
                    },
                    disabled={
                        "opacity": "0.6",
                        "cursor": "not-allowed",
                        "pointer-events": "none"
                    }
                )
            },
            parameters={
                "type": "button",
                "size": "medium",
                "variant": "primary",
                "text": "Button",
                "icon": ""
            },
            animations={
                "click": Animation(
                    name="button-click",
                    keyframes={
                        "0%": {"transform": "scale(1)"},
                        "50%": {"transform": "scale(0.95)"},
                        "100%": {"transform": "scale(1)"}
                    },
                    duration="0.2s"
                )
            }
        )
        
        # Input Component
        templates['input'] = ComponentTemplate(
            name="input",
            html='''
                <div class="input-wrapper {size} {additional_classes}">
                    {label}
                    <input 
                        type="{type}"
                        name="{name}"
                        placeholder="{placeholder}"
                        class="custom-input {variant}"
                        {additional_attributes}
                    />
                    {helper_text}
                </div>
            ''',
            styles={
                "input": StyleState(
                    normal={
                        "width": "100%",
                        "padding": "0.5rem 0.75rem",
                        "border": "1px solid var(--border-color)",
                        "border-radius": "0.375rem",
                        "transition": "all 0.2s",
                        "font-size": "1rem",
                        "line-height": "1.5"
                    },
                    focus={
                        "border-color": "var(--primary-500)",
                        "box-shadow": "0 0 0 2px var(--primary-100)"
                    },
                    disabled={
                        "background-color": "var(--gray-100)",
                        "cursor": "not-allowed"
                    }
                )
            },
            parameters={
                "type": "text",
                "name": "",
                "placeholder": "",
                "label": "",
                "helper_text": "",
                "size": "medium",
                "variant": "default"
            }
        )
        
        # Card Component
        templates['card'] = ComponentTemplate(
            name="card",
            html='''
                <div class="card {variant} {additional_classes}" {additional_attributes}>
                    {header}
                    <div class="card-body">
                        {content}
                    </div>
                    {footer}
                </div>
            ''',
            styles={
                "card": StyleState(
                    normal={
                        "background": "white",
                        "border-radius": "0.5rem",
                        "box-shadow": "0 4px 6px rgba(0,0,0,0.1)",
                        "overflow": "hidden"
                    }
                ),
                "card-body": StyleState(
                    normal={
                        "padding": "1.5rem"
                    }
                )
            },
            parameters={
                "variant": "default",
                "header": "",
                "content": "",
                "footer": ""
            },
            grid_area="card"
        )
        
        # Modal Component
        templates['modal'] = ComponentTemplate(
            name="modal",
            html='''
                <div class="modal-overlay {additional_classes}">
                    <div class="modal {size} {variant}" role="dialog" aria-modal="true">
                        <div class="modal-header">
                            {header}
                            <button class="modal-close" aria-label="Close modal">×</button>
                        </div>
                        <div class="modal-body">
                            {content}
                        </div>
                        <div class="modal-footer">
                            {footer}
                        </div>
                    </div>
                </div>
            ''',
            styles={
                "modal-overlay": StyleState(
                    normal={
                        "position": "fixed",
                        "top": "0",
                        "left": "0",
                        "right": "0",
                        "bottom": "0",
                        "background": "rgba(0,0,0,0.5)",
                        "display": "flex",
                        "align-items": "center",
                        "justify-content": "center",
                        "z-index": "var(--z-modal)"
                    }
                ),
                "modal": StyleState(
                    normal={
                        "background": "white",
                        "border-radius": "0.5rem",
                        "max-width": "500px",
                        "width": "100%",
                        "max-height": "90vh",
                        "overflow-y": "auto"
                    }
                )
            },
            parameters={
                "size": "medium",
                "variant": "default",
                "header": "",
                "content": "",
                "footer": ""
            },
            animations={
                "enter": Animation(
                    name="modal-enter",
                    keyframes={
                        "0%": {
                            "opacity": "0",
                            "transform": "scale(0.95)"
                        },
                        "100%": {
                            "opacity": "1",
                            "transform": "scale(1)"
                        }
                    },
                    duration="0.2s",
                    timing="cubic-bezier(0.4, 0, 0.2, 1)"
                ),
                "exit": Animation(
                    name="modal-exit",
                    keyframes={
                        "0%": {
                            "opacity": "1",
                            "transform": "scale(1)"
                        },
                        "100%": {
                            "opacity": "0",
                            "transform": "scale(0.95)"
                        }
                    },
                    duration="0.15s",
                    timing="cubic-bezier(0.4, 0, 0.2, 1)"
                )
            }
        )
        
        return templates

    def get_template(self, template_name: str) -> Optional[ComponentTemplate]:
        """Get component template by name"""
        return self.templates.get(template_name)

    def create_component(self, template_name: str, params: Dict[str, Any], position: Position) -> Optional[Tag]:
        """Create component with enhanced positioning and styling"""
        try:
            template = self.templates.get(template_name)
            if not template:
                self.logger.error(f"Template not found: {template_name}")
                return None
            
            # Merge parameters
            merged_params = {**template.parameters, **(params or {})}
            
            # Create component
            soup = BeautifulSoup(template.html.format(**merged_params), 'html.parser')
            component = soup.find()
            
            if not component:
                return None
            
            # Add position attributes
            if position.grid_area:
                component['style'] = f"grid-area: {position.grid_area};"
            
            # Track instance
            if template_name not in self.instances:
                self.instances[template_name] = []
            self.instances[template_name].append(component)
            
            # Handle relationships
            if template.relationships:
                self._handle_relationships(template_name, component)
            
            return component
            
        except Exception as e:
            self.logger.error(f"Error creating component {template_name}: {str(e)}")
            return None

    def _handle_relationships(self, template_name: str, component: Tag):
        """Handle component relationships"""
        template = self.templates[template_name]
        for rel_type, rel_components in template.relationships.items():
            for rel_comp in rel_components:
                if rel_comp not in self.relationships:
                    self.relationships[rel_comp] = set()
                self.relationships[rel_comp].add(template_name)

    def get_related_components(self, component_name: str) -> Set[str]:
        """Get components related to the given component"""
        return self.relationships.get(component_name, set())

    def update_component(self, component: Tag, updates: Dict[str, Any]) -> bool:
        """Update existing component"""
        try:
            for key, value in updates.items():
                if key == 'text':
                    component.string = value
                elif key == 'attributes':
                    for attr, attr_value in value.items():
                        component[attr] = attr_value
                elif key == 'styles':
                    current_style = component.get('style', '')
                    new_styles = '; '.join(f"{k}: {v}" for k, v in value.items())
                    component['style'] = f"{current_style}; {new_styles}"
            return True
        except Exception as e:
            self.logger.error(f"Error updating component: {str(e)}")
            return False

class PositionManager:
    """Enhanced position management with collision detection and grid support"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.viewport_positions = {}  # Track positions by z-index
        self.grid_positions = {}  # Track grid positions
        self.collision_buffer = 10  # Pixels to adjust for collision

    def position_element(self, soup: BeautifulSoup, element: Tag, position: Position) -> bool:
        """Position element with enhanced placement logic"""
        try:
            # Adjust position for collisions
            adjusted_position = self._check_and_adjust_position(position)
            
            if adjusted_position.type == 'grid' and adjusted_position.grid_area:
                return self._handle_grid_position(element, adjusted_position)
            elif adjusted_position.type == 'fixed':
                return self._handle_fixed_position(soup, element, adjusted_position)
            elif adjusted_position.type == 'absolute':
                return self._handle_absolute_position(soup, element, adjusted_position)
            elif adjusted_position.type == 'sticky':
                return self._handle_sticky_position(element, adjusted_position)
            else:  # relative or static
                return self._handle_flow_position(element, adjusted_position)
                
        except Exception as e:
            self.logger.error(f"Error positioning element: {str(e)}")
            return False

    def _check_and_adjust_position(self, position: Position) -> Position:
        """Check for collisions and adjust position"""
        if position.type not in ['fixed', 'absolute']:
            return position

        pos_key = (position.x, position.y)
        z_index = position.z_index or 0

        # Check for collision
        if pos_key in self.viewport_positions:
            existing_z = self.viewport_positions[pos_key]
            if z_index <= existing_z:
                # Create new position with adjusted coordinates
                new_position = copy.deepcopy(position)
                if isinstance(new_position.y, (int, float)):
                    new_position.y += self.collision_buffer
                else:
                    new_position.y = f"calc({position.y} + {self.collision_buffer}px)"
                new_position.z_index = existing_z + 1
                return new_position

        # Update position tracking
        self.viewport_positions[pos_key] = z_index
        return position

    def _generate_position_style(self, position: Position) -> str:
        """Generate CSS position style"""
        styles = [f"position: {position.type}"]
        
        # Handle coordinates
        if isinstance(position.x, (int, float)):
            styles.append(f"left: {position.x}px")
        else:
            styles.append(f"left: {position.x}")
            
        if isinstance(position.y, (int, float)):
            styles.append(f"top: {position.y}px")
        else:
            styles.append(f"top: {position.y}")
        
        # Add z-index if specified
        if position.z_index is not None:
            styles.append(f"z-index: {position.z_index}")
        
        # Add transform for anchor points
        if position.anchor != 'top-left':
            transform = self._get_anchor_transform(position.anchor)
            if transform:
                styles.append(f"transform: {transform}")
        
        # Add margins
        for side, value in position.margin.items():
            styles.append(f"margin-{side}: {value}")
        
        return '; '.join(styles)

    def _get_anchor_transform(self, anchor: str) -> Optional[str]:
        """Get transform for anchor points"""
        transforms = {
            'center': 'translate(-50%, -50%)',
            'top-center': 'translateX(-50%)',
            'bottom-center': 'translate(-50%, 100%)',
            'center-left': 'translateY(-50%)',
            'center-right': 'translate(100%, -50%)',
            'bottom-left': 'translateY(100%)',
            'bottom-right': 'translate(100%, 100%)',
            'top-right': 'translateX(100%)'
        }
        return transforms.get(anchor)

    def _handle_grid_position(self, element: Tag, position: Position) -> bool:
        """Handle grid positioning"""
        try:
            if not position.grid_area:
                return False
                
            element['style'] = f"{element.get('style', '')}; grid-area: {position.grid_area}"
            self.grid_positions[position.grid_area] = element
            return True
        except Exception as e:
            self.logger.error(f"Error handling grid position: {str(e)}")
            return False

    def _handle_fixed_position(self, soup: BeautifulSoup, element: Tag, position: Position) -> bool:
        """Handle fixed positioning"""
        try:
            style = self._generate_position_style(position)
            element['style'] = f"{element.get('style', '')}; {style}"
            return True
        except Exception as e:
            self.logger.error(f"Error handling fixed position: {str(e)}")
            return False

    def _handle_absolute_position(self, soup: BeautifulSoup, element: Tag, position: Position) -> bool:
        """Handle absolute positioning"""
        try:
            # Find target element
            target = soup.select_one(position.target) if position.target != 'viewport' else None
            
            if target:
                target['style'] = f"{target.get('style', '')}; position: relative"
                target.append(element)
            else:
                # Add to body if no target
                soup.body.append(element)
                
            style = self._generate_position_style(position)
            element['style'] = f"{element.get('style', '')}; {style}"
            return True
        except Exception as e:
            self.logger.error(f"Error handling absolute position: {str(e)}")
            return False

    def _handle_sticky_position(self, element: Tag, position: Position) -> bool:
        """Handle sticky positioning"""
        try:
            style = self._generate_position_style(position)
            element['style'] = f"{element.get('style', '')}; {style}"
            return True
        except Exception as e:
            self.logger.error(f"Error handling sticky position: {str(e)}")
            return False

    def _handle_flow_position(self, element: Tag, position: Position) -> bool:
        """Handle flow positioning"""
        try:
            style = self._generate_position_style(position)
            element['style'] = f"{element.get('style', '')}; {style}"
            return True
        except Exception as e:
            self.logger.error(f"Error handling flow position: {str(e)}")
            return False

class HTMLProcessor:
    """Enhanced HTML processing with comprehensive features"""
    
    def __init__(self, html: str):
        self.original_html = html
        self.soup = BeautifulSoup(html, 'html.parser')
        self.theme = SiteTheme()
        self.component_manager = ComponentManager(self.theme)
        self.position_manager = PositionManager()
        self.grid_system = GridSystem()
        self.animation_system = AnimationSystem()
        self.logger = logging.getLogger(__name__)
        self.undo_stack = []
        self.redo_stack = []
        self._init_document_head()

    def _init_document_head(self):
        """Initialize document head with required elements"""
        if not self.soup.head:
            self.soup.html.insert(0, self.soup.new_tag('head'))

        # Add style tag if not present
        if not self.soup.head.find('style'):
            style_tag = self.soup.new_tag('style')
            self.soup.head.append(style_tag)

    def apply_variation(self, variation: HTMLVariation) -> str:
        """Apply comprehensive HTML variations"""
        try:
            # Save current state for undo
            self._save_state()
            
            # Create fresh soup for modifications
            self.soup = BeautifulSoup(self.original_html, 'html.parser')
            
            # Apply all changes
            for component in variation.components_added:
                self._add_component(component)
            
            for selector, styles in variation.styles_modified.items():
                self._apply_styles(selector, styles)
            
            for selector in variation.elements_removed:
                self._remove_element(selector)
            
            for selector, modifications in variation.elements_modified.items():
                self._modify_element(selector, modifications)
            
            # Apply grid layouts
            self._apply_grid_layouts()
            
            # Apply animations
            self._apply_animations()
            
            # Update styles
            self._update_document_styles()
            
            return str(self.soup.prettify())
            
        except Exception as e:
            self.logger.error(f"Error applying variation: {str(e)}")
            raise

    def _add_component(self, component: ComponentAddition) -> bool:
        """Add new component with comprehensive setup"""
        try:
            # Create component
            element = self.component_manager.create_component(
                component.template.name,
                component.parameters,
                component.position
            )
            
            if not element:
                return False
            
            # Add custom attributes
            for key, value in component.custom_attributes.items():
                element[key] = value
            
            # Add ARIA attributes
            for key, value in component.custom_aria.items():
                element[f'aria-{key}'] = value
            
            # Add event handlers
            for event, handler in component.custom_events.items():
                element[f'on{event}'] = handler
            
            # Add animations if specified
            for anim_name, anim in component.animations.items():
                self.animation_system.apply_animation(element, anim_name)
            
            # Position the element
            return self.position_manager.position_element(
                self.soup,
                element,
                component.position
            )
            
        except Exception as e:
            self.logger.error(f"Error adding component: {str(e)}")
            return False

    def _apply_styles(self, selector: str, styles: Dict[str, str]):
        """Apply styles with inheritance and cascading"""
        try:
            elements = self.soup.select(selector)
            for element in elements:
                current_style = element.get('style', '')
                new_styles = '; '.join(f"{k}: {v}" for k, v in styles.items())
                
                if current_style:
                    element['style'] = f"{current_style}; {new_styles}"
                else:
                    element['style'] = new_styles
                    
        except Exception as e:
            self.logger.error(f"Error applying styles to {selector}: {str(e)}")

    def _apply_grid_layouts(self):
        """Apply grid layouts to document"""
        try:
            for template_name, template in self.grid_system.templates.items():
                container = self.soup.select_one(f'.grid-{template_name}')
                if container:
                    styles = self.grid_system.generate_template_styles(template_name)
                    if styles:
                        current_style = container.get('style', '')
                        container['style'] = f"{current_style}; {styles}"
                    
        except Exception as e:
            self.logger.error(f"Error applying grid layouts: {str(e)}")

    def _apply_animations(self):
        """Apply animations to document"""
        try:
            # Get all animation CSS
            animation_css = self.animation_system.get_active_animations_css()
            if animation_css:
                style_tag = self.soup.head.find('style')
                if style_tag:
                    current_css = style_tag.string or ''
                    style_tag.string = f"{current_css}\n{animation_css}"
                    
        except Exception as e:
            self.logger.error(f"Error applying animations: {str(e)}")

    def _update_document_styles(self):
        """Update document styles with theme and components"""
        try:
            style_tag = self.soup.head.find('style')
            if not style_tag:
                return

            css_text = []
            
            # Add theme variables
            css_text.append(":root {")
            for color_name, color_value in self.theme.colors.items():
                css_text.append(f"  --color-{color_name}: {color_value};")
            css_text.append("}")
            
            # Add component styles
            for template in self.component_manager.templates.values():
                for selector, state in template.styles.items():
                    # Normal state
                    css_text.append(f".{template.name}-{selector} {{")
                    for prop, value in state.normal.items():
                        css_text.append(f"  {prop}: {value};")
                    css_text.append("}")
                    
                    # Hover state
                    if state.hover:
                        css_text.append(f".{template.name}-{selector}:hover {{")
                        for prop, value in state.hover.items():
                            css_text.append(f"  {prop}: {value};")
                        css_text.append("}")
                    
                    # Other states...
            
            # Update style tag
            style_tag.string = '\n'.join(css_text)
            
        except Exception as e:
            self.logger.error(f"Error updating document styles: {str(e)}")

    def _save_state(self):
        """Save current state for undo/redo"""
        self.undo_stack.append(str(self.soup))
        self.redo_stack.clear()

    def undo(self) -> bool:
        """Restore previous state"""
        if not self.undo_stack:
            return False
            
        self.redo_stack.append(str(self.soup))
        self.soup = BeautifulSoup(self.undo_stack.pop(), 'html.parser')
        return True

    def redo(self) -> bool:
        """Restore next state"""
        if not self.redo_stack:
            return False
            
        self.undo_stack.append(str(self.soup))
        self.soup = BeautifulSoup(self.redo_stack.pop(), 'html.parser')
        return True

class AIRequestProcessor:
    """Enhanced AI request processing with LLM integration"""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.logger = logging.getLogger(__name__)
        self.component_manager = ComponentManager()
        self.context_window = []
        self.max_context_items = 5

    def process_request(self, request: str, html: str, current_theme: Dict[str, Any]) -> HTMLVariation:
        """Process user request with enhanced context awareness"""
        try:
            # Update context window
            self._update_context(request)
            
            # Create system message
            system_message = self._create_system_message(current_theme)
            
            # Create user message with context
            user_message = self._create_user_message(request, html)
            
            # Get LLM response
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse and validate response
            variation = self._parse_llm_response(response.choices[0].message.content)
            if not variation.validate():
                raise ValueError("Invalid variation generated")
                
            return variation
            
        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}")
            raise

    def _update_context(self, request: str):
        """Update context window"""
        self.context_window.append(request)
        if len(self.context_window) > self.max_context_items:
            self.context_window.pop(0)

    def _create_system_message(self, current_theme: Dict[str, Any]) -> str:
        """Create enhanced system message"""
        return f"""You are an expert web developer AI. Parse user requests and return JSON describing exact HTML modifications.
        
        Available components: {', '.join(self.component_manager.templates.keys())}
        Current theme: {json.dumps(current_theme, indent=2)}
        
        Previous context: {' | '.join(self.context_window)}
        
        Return JSON format:
        {{
            "components_added": [
                {{
                    "template": "component_name",
                    "position": {{
                        "type": "fixed|absolute|relative|grid",
                        "target": "selector",
                        "x": "value",
                        "y": "value",
                        "grid_area": "area_name"
                    }},
                    "parameters": {{}},
                    "animations": []
                }}
            ],
            "styles_modified": {{}},
            "elements_removed": [],
            "elements_modified": {{}}
        }}"""

    def _create_user_message(self, request: str, html: str) -> str:
        """Create enhanced user message"""
        return f"""Request: {request}
        
        Current HTML:
        {html}
        
        Return only the JSON response describing the exact changes needed."""

    def _parse_llm_response(self, response: str) -> HTMLVariation:
        """Parse LLM response with enhanced validation"""
        try:
            # Extract JSON from response
            json_str = re.search(r'({.*})', response.strip(), re.DOTALL)
            if not json_str:
                raise ValueError("No valid JSON found in response")
            
            data = json.loads(json_str.group(1))
            
            # Create variation with comprehensive validation
            variation = HTMLVariation(
                html="",  # Will be set by processor
                changes=[f"Request: {self.context_window[-1]}"],
                components_added=[],
                styles_modified=data.get('styles_modified', {}),
                elements_removed=data.get('elements_removed', []),
                elements_modified=data.get('elements_modified', {})
            )
            
            # Process components with enhanced validation
            for comp_data in data.get('components_added', []):
                template = self.component_manager.get_template(comp_data['template'])
                if template:
                    position = Position(**comp_data['position'])
                    component = ComponentAddition(
                        template=template,
                        position=position,
                        parameters=comp_data.get('parameters', {}),
                        animations=comp_data.get('animations', [])
                    )
                    if component.validate():
                        variation.components_added.append(component)
                    else:
                        self.logger.warning(f"Invalid component configuration: {comp_data}")
            
            return variation
            
        except Exception as e:
            self.logger.error(f"Error parsing LLM response: {str(e)}")
            raise

class HTMLEnhancementCLI:
    """Enhanced CLI interface with comprehensive features"""
    
    def __init__(self, api_key: str):
        self.console = Console()
        self.processor = AIRequestProcessor(api_key)
        self.logger = logging.getLogger(__name__)
        self.temp_dir = tempfile.mkdtemp()
        self.current_html = None
        self.html_processor = None
        self.theme = SiteTheme()

    def run(self):
        """Main CLI execution loop"""
        try:
            self.console.print("[bold blue]HTML Enhancement Tool[/bold blue]")
            
            # Get initial HTML
            self.current_html = self._get_initial_html()
            if not self.current_html:
                return
            
            self.html_processor = HTMLProcessor(self.current_html)
            
            while True:
                self._show_menu()
                choice = Prompt.ask(
                    "Choose an option",
                    choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
                )
                
                if choice == "1":
                    self._handle_add_component()
                elif choice == "2":
                    self._handle_modify_element()
                elif choice == "3":
                    self._handle_remove_element()
                elif choice == "4":
                    self._handle_grid_layout()
                elif choice == "5":
                    self._handle_animation()
                elif choice == "6":
                    self._handle_theme()
                elif choice == "7":
                    self._handle_preview()
                elif choice == "8":
                    self._handle_undo()
                elif choice == "9":
                    self._handle_save()
                elif choice == "10":
                    break
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Operation cancelled[/yellow]")
        finally:
            self._cleanup()

    def _get_initial_html(self) -> Optional[str]:
        """Get initial HTML content"""
        source = Prompt.ask(
            "Enter HTML source",
            choices=["file", "paste", "template"],
            default="file"
        )
        
        if source == "file":
            path = Prompt.ask("Enter path to HTML file")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                self.console.print(f"[red]Error reading file: {str(e)}[/red]")
                return None
        elif source == "template":
            return self._get_template_html()
        else:
            return Prompt.ask("Paste HTML content")

    def _get_template_html(self) -> str:
        """Get HTML from template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced HTML</title>
</head>
<body>
    <div class="container">
    </div>
</body>
</html>
"""

    def _show_menu(self):
        """Show enhanced main menu"""
        self.console.print("\n[green]Available Actions:[/green]")
        self.console.print("1. Add Component")
        self.console.print("2. Modify Element")
        self.console.print("3. Remove Element")
        self.console.print("4. Grid Layout")
        self.console.print("5. Animation")
        self.console.print("6. Theme Settings")
        self.console.print("7. Preview")
        self.console.print("8. Undo")
        self.console.print("9. Save")
        self.console.print("10. Exit")

    def _handle_add_component(self):
        """Handle component addition with enhanced options"""
        try:
            # Show available components
            self.console.print("\n[blue]Available Components:[/blue]")
            for name in self.html_processor.component_manager.templates.keys():
                self.console.print(f"  • {name}")
            
            # Get component details
            component = Prompt.ask("Enter component name")
            request = Prompt.ask("Describe the component configuration")
            
            # Process request
            variation = self.processor.process_request(
                f"Add {component}: {request}",
                self.html_processor.soup.prettify(),
                self.theme.__dict__
            )
            
            if variation and variation.validate():
                self._show_changes(variation)
                if Confirm.ask("Apply these changes?"):
                    self.current_html = self.html_processor.apply_variation(variation)
                    self.console.print("[green]Component added successfully[/green]")
            else:
                self.console.print("[red]Invalid component configuration[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def _handle_grid_layout(self):
        """Handle grid layout configuration"""
        try:
            self.console.print("\n[blue]Grid Layout Configuration[/blue]")
            
            # Get grid template details
            name = Prompt.ask("Enter grid template name")
            columns = Prompt.ask("Enter grid columns (e.g., '1fr 1fr 1fr')")
            rows = Prompt.ask("Enter grid rows (e.g., 'auto 1fr auto')")
            gap = Prompt.ask("Enter grid gap", default="1rem")
            
            # Create grid template
            template = GridTemplate(
                name=name,
                areas=[],  # Will be configured based on components
                columns=columns,
                rows=rows,
                gap=gap
            )
            
            if self.html_processor.grid_system.create_template(template):
                self.console.print("[green]Grid template created successfully[/green]")
            else:
                self.console.print("[red]Error creating grid template[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def _handle_animation(self):
        """Handle animation configuration"""
        try:
            self.console.print("\n[blue]Animation Configuration[/blue]")
            
            # Get animation details
            name = Prompt.ask("Enter animation name")
            duration = Prompt.ask("Enter duration", default="0.3s")
            timing = Prompt.ask("Enter timing function", default="ease")
            
            # Get keyframes
            keyframes = {}
            while Confirm.ask("Add keyframe?"):
                step = Prompt.ask("Enter step (e.g., '0%', '50%', '100%')")
                properties = {}
                while Confirm.ask("Add property?"):
                    prop = Prompt.ask("Enter property name")
                    value = Prompt.ask("Enter property value")
                    properties[prop] = value
                keyframes[step] = properties
            
            # Create animation
            animation = Animation(
                name=name,
                keyframes=keyframes,
                duration=duration,
                timing=timing
            )
            
            if self.html_processor.animation_system.add_animation(animation):
                self.console.print("[green]Animation created successfully[/green]")
            else:
                self.console.print("[red]Error creating animation[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def _handle_theme(self):
        """Handle theme configuration"""
        try:
            self.console.print("\n[blue]Theme Configuration[/blue]")
            
            # Show current theme
            self.console.print("\nCurrent Theme:")
            self.console.print(Panel(
                Syntax(
                    json.dumps(self.theme.__dict__, indent=2),
                    "json",
                    theme="monokai"
                )
            ))
            
            # Get theme section to modify
            section = Prompt.ask(
                "Enter section to modify",
                choices=["colors", "fonts", "spacing", "breakpoints"]
            )
            
            # Modify section
            if section == "colors":
                self._modify_theme_colors()
            elif section == "fonts":
                self._modify_theme_fonts()
            elif section == "spacing":
                self._modify_theme_spacing()
            elif section == "breakpoints":
                self._modify_theme_breakpoints()
                
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")

    def _modify_theme_colors(self):
        """Modify theme colors"""
        while Confirm.ask("Add/modify color?"):
            name = Prompt.ask("Enter color name")
            value = Prompt.ask("Enter color value")
            self.theme.colors[name] = value
            self.console.print(f"[green]Color {name} updated[/green]")

    def _handle_preview(self):
        """Handle preview with enhanced features"""
        if not self.current_html:
            self.console.print("[yellow]No HTML to preview[/yellow]")
            return
            
        preview_path = Path(self.temp_dir) / "preview.html"
        
        # Add required styles
        soup = BeautifulSoup(self.current_html, 'html.parser')
        
        # Add theme variables
        style_tag = soup.new_tag('style')
        style_tag.string = self._generate_theme_css()
        soup.head.append(style_tag)
        
        # Write to file
        preview_path.write_text(str(soup))
        webbrowser.open(str(preview_path))

    def _generate_theme_css(self) -> str:
        """Generate CSS from theme"""
        css = [":root {"]
        
        # Colors
        for name, value in self.theme.colors.items():
            css.append(f"  --color-{name}: {value};")
        
        # Fonts
        for name, font in self.theme.fonts.items():
            css.append(f"  --font-{name}: {font['family']};")
        
        # Spacing
        for name, value in self.theme.spacing.items():
            css.append(f"  --spacing-{name}: {value};")
        
        css.append("}")
        return '\n'.join(css)

    def _handle_save(self):
        """Handle save with enhanced options"""
        if not self.current_html:
            self.console.print("[yellow]No HTML to save[/yellow]")
            return
            
        # Get save options
        format_type = Prompt.ask(
            "Choose format",
            choices=["html", "component", "template"],
            default="html"
        )
        
        path = Prompt.ask("Enter path to save file", default="output.html")
        
        try:
            if format_type == "html":
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.current_html)
            elif format_type == "component":
                self._save_as_component(path)
            else:
                self._save_as_template(path)
                
            self.console.print(f"[green]File saved to {path}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error saving file: {str(e)}[/red]")

    def _save_as_component(self, path: str):
        """Save current HTML as reusable component"""
        component_name = Prompt.ask("Enter component name")
        
        component = ComponentTemplate(
            name=component_name,
            html=self.current_html,
            styles={},  # Extract styles from HTML
            parameters={}  # Extract parameters from HTML
        )
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(component.__dict__, f, indent=2)

    def _cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            self.logger.error(f"Error cleaning up: {str(e)}")

def main():
    """Enhanced main entry point"""
    try:
        console = Console()
        
        # Show welcome message
        console.print(Panel(
            "[bold blue]HTML Enhancement Tool[/bold blue]\n"
            "An AI-powered tool for HTML manipulation and enhancement",
            title="Welcome"
        ))
        
        # Get API key
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            api_key = Prompt.ask(
                "Enter your Groq API key",
                password=True
            )
            if not api_key:
                console.print("[red]API key is required[/red]")
                return

        # Run CLI
        cli = HTMLEnhancementCLI(api_key)
        with Progress() as progress:
            task = progress.add_task("[cyan]Initializing...", total=100)
            progress.update(task, advance=50)
            cli.run()
            progress.update(task, completed=100)
        
    except Exception as e:
        console.print(f"[red]An error occurred: {str(e)}[/red]")
        logger.exception("Application error")

if __name__ == "__main__":
    main()