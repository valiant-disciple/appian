from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
from pathlib import Path
from .style_guide import StyleGuide

@dataclass
class DesignPattern:
    """Structure for design patterns"""
    name: str
    category: str
    description: str
    html_template: str
    css_template: str
    js_template: Optional[str]
    variables: Dict[str, Any]
    constraints: Dict[str, Any]
    best_practices: List[str]

class DesignPatternManager:
    def __init__(self, style_guide: Optional[StyleGuide] = None):
        """Initialize the design pattern manager"""
        self.patterns_path = Path("design_patterns")
        self.patterns_path.mkdir(exist_ok=True)
        self.style_guide = style_guide
        self.loaded_patterns: Dict[str, DesignPattern] = {}
        self._load_patterns()

    def _load_patterns(self):
        """Load all available design patterns"""
        try:
            pattern_files = self.patterns_path.glob("*.json")
            for file in pattern_files:
                with open(file, 'r') as f:
                    data = json.load(f)
                    self.loaded_patterns[data['name']] = DesignPattern(**data)
        except Exception as e:
            print(f"Error loading patterns: {str(e)}")

    def apply_pattern(self, pattern_name: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Apply a design pattern with given context"""
        if pattern_name not in self.loaded_patterns:
            raise ValueError(f"Pattern {pattern_name} not found")
            
        pattern = self.loaded_patterns[pattern_name]
        
        try:
            # Validate context against constraints
            self._validate_context(pattern, context)
            
            # Apply style guide if available
            if self.style_guide:
                context = self._apply_style_guide(pattern, context)
            
            # Generate code
            html = self._generate_html(pattern, context)
            css = self._generate_css(pattern, context)
            js = self._generate_js(pattern, context) if pattern.js_template else ""
            
            return {
                'html': html,
                'css': css,
                'js': js,
                'pattern_info': {
                    'name': pattern.name,
                    'category': pattern.category,
                    'best_practices': pattern.best_practices
                }
            }
            
        except Exception as e:
            print(f"Error applying pattern: {str(e)}")
            raise

    def suggest_patterns(self, content_type: str, constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest appropriate patterns based on content type and constraints"""
        suggestions = []
        
        try:
            for pattern in self.loaded_patterns.values():
                score = self._calculate_pattern_match(pattern, content_type, constraints)
                if score > 0.6:  # Minimum match threshold
                    suggestions.append({
                        'pattern': pattern.name,
                        'score': score,
                        'rationale': self._generate_suggestion_rationale(pattern, content_type, constraints),
                        'preview': self._generate_pattern_preview(pattern)
                    })
            
            return sorted(suggestions, key=lambda x: x['score'], reverse=True)
            
        except Exception as e:
            print(f"Error suggesting patterns: {str(e)}")
            return []

    def create_pattern(self, pattern_data: Dict[str, Any]) -> DesignPattern:
        """Create a new design pattern"""
        try:
            # Validate pattern data
            required_fields = ['name', 'category', 'description', 'html_template', 'css_template']
            for field in required_fields:
                if field not in pattern_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create pattern
            pattern = DesignPattern(
                name=pattern_data['name'],
                category=pattern_data['category'],
                description=pattern_data['description'],
                html_template=pattern_data['html_template'],
                css_template=pattern_data['css_template'],
                js_template=pattern_data.get('js_template'),
                variables=pattern_data.get('variables', {}),
                constraints=pattern_data.get('constraints', {}),
                best_practices=pattern_data.get('best_practices', [])
            )
            
            # Save pattern
            self._save_pattern(pattern)
            self.loaded_patterns[pattern.name] = pattern
            
            return pattern
            
        except Exception as e:
            print(f"Error creating pattern: {str(e)}")
            raise

    def _validate_context(self, pattern: DesignPattern, context: Dict[str, Any]):
        """Validate context against pattern constraints"""
        for key, constraint in pattern.constraints.items():
            if key in context:
                value = context[key]
                
                # Type validation
                if 'type' in constraint:
                    if not isinstance(value, eval(constraint['type'])):
                        raise ValueError(f"Invalid type for {key}")
                
                # Range validation
                if 'range' in constraint:
                    min_val, max_val = constraint['range']
                    if not min_val <= value <= max_val:
                        raise ValueError(f"Value for {key} out of range")
                
                # Pattern validation
                if 'pattern' in constraint:
                    import re
                    if not re.match(constraint['pattern'], str(value)):
                        raise ValueError(f"Invalid format for {key}")

    def _apply_style_guide(self, pattern: DesignPattern, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply style guide to context"""
        if not self.style_guide:
            return context
            
        updated_context = context.copy()
        
        # Apply color scheme
        if 'colors' in pattern.variables:
            updated_context['colors'] = {
                'primary': self.style_guide.colors.primary[0],
                'secondary': self.style_guide.colors.secondary[0],
                'accent': self.style_guide.colors.accent[0]
            }
        
        # Apply typography
        if 'typography' in pattern.variables:
            updated_context['typography'] = {
                'headings': self.style_guide.typography.headings,
                'body': self.style_guide.typography.body
            }
        
        # Apply spacing
        if 'spacing' in pattern.variables:
            updated_context['spacing'] = self.style_guide.spacing.components['normal']
        
        return updated_context

    def _generate_html(self, pattern: DesignPattern, context: Dict[str, Any]) -> str:
        """Generate HTML from pattern template"""
        try:
            from jinja2 import Template
            template = Template(pattern.html_template)
            return template.render(**context)
        except Exception as e:
            print(f"Error generating HTML: {str(e)}")
            raise

    def _generate_css(self, pattern: DesignPattern, context: Dict[str, Any]) -> str:
        """Generate CSS from pattern template"""
        try:
            from jinja2 import Template
            template = Template(pattern.css_template)
            return template.render(**context)
        except Exception as e:
            print(f"Error generating CSS: {str(e)}")
            raise

    def _generate_js(self, pattern: DesignPattern, context: Dict[str, Any]) -> str:
        """Generate JavaScript from pattern template"""
        if not pattern.js_template:
            return ""
            
        try:
            from jinja2 import Template
            template = Template(pattern.js_template)
            return template.render(**context)
        except Exception as e:
            print(f"Error generating JavaScript: {str(e)}")
            raise

    def _calculate_pattern_match(self, pattern: DesignPattern, 
                               content_type: str, 
                               constraints: Dict[str, Any]) -> float:
        """Calculate how well a pattern matches given requirements"""
        score = 0
        weights = {
            'category_match': 0.4,
            'constraint_match': 0.4,
            'complexity_match': 0.2
        }
        
        # Category match
        if pattern.category.lower() == content_type.lower():
            score += weights['category_match']
        
        # Constraint match
        constraint_scores = []
        for key, value in constraints.items():
            if key in pattern.constraints:
                if self._check_constraint_match(pattern.constraints[key], value):
                    constraint_scores.append(1)
                else:
                    constraint_scores.append(0)
        
        if constraint_scores:
            score += weights['constraint_match'] * (sum(constraint_scores) / len(constraint_scores))
        
        # Complexity match
        pattern_complexity = self._calculate_pattern_complexity(pattern)
        required_complexity = constraints.get('complexity', 'medium')
        if pattern_complexity == required_complexity:
            score += weights['complexity_match']
        
        return score

    def _check_constraint_match(self, pattern_constraint: Dict[str, Any], value: Any) -> bool:
        """Check if a value matches a pattern constraint"""
        try:
            if 'type' in pattern_constraint:
                if not isinstance(value, eval(pattern_constraint['type'])):
                    return False
            
            if 'range' in pattern_constraint:
                min_val, max_val = pattern_constraint['range']
                if not min_val <= value <= max_val:
                    return False
            
            if 'pattern' in pattern_constraint:
                import re
                if not re.match(pattern_constraint['pattern'], str(value)):
                    return False
            
            return True
            
        except Exception:
            return False

    def _calculate_pattern_complexity(self, pattern: DesignPattern) -> str:
        """Calculate pattern complexity"""
        # Count template variables
        var_count = len(pattern.variables)
        
        # Count template lines
        html_lines = pattern.html_template.count('\n')
        css_lines = pattern.css_template.count('\n')
        js_lines = pattern.js_template.count('\n') if pattern.js_template else 0
        
        total_lines = html_lines + css_lines + js_lines
        
        # Determine complexity
        if total_lines < 50 and var_count < 5:
            return 'simple'
        elif total_lines < 150 and var_count < 10:
            return 'medium'
        else:
            return 'complex'

    def _generate_suggestion_rationale(self, pattern: DesignPattern,
                                    content_type: str,
                                    constraints: Dict[str, Any]) -> str:
        """Generate explanation for pattern suggestion"""
        reasons = [f"This pattern is designed for {pattern.category} content"]
        
        # Add constraint-based reasons
        for key, value in constraints.items():
            if key in pattern.constraints:
                reasons.append(f"Supports {key} requirement: {value}")
        
        # Add complexity reason
        complexity = self._calculate_pattern_complexity(pattern)
        reasons.append(f"Pattern complexity: {complexity}")
        
        # Add best practices
        if pattern.best_practices:
            reasons.append("Follows best practices:")
            reasons.extend([f"- {practice}" for practice in pattern.best_practices])
        
        return "\n".join(reasons)

    def _generate_pattern_preview(self, pattern: DesignPattern) -> Dict[str, str]:
        """Generate preview of pattern with default values"""
        try:
            # Create default context
            default_context = {}
            for key, var_info in pattern.variables.items():
                default_context[key] = var_info.get('default')
            
            # Apply style guide if available
            if self.style_guide:
                default_context = self._apply_style_guide(pattern, default_context)
            
            # Generate preview code
            return {
                'html': self._generate_html(pattern, default_context),
                'css': self._generate_css(pattern, default_context),
                'js': self._generate_js(pattern, default_context) if pattern.js_template else ""
            }
            
        except Exception as e:
            print(f"Error generating pattern preview: {str(e)}")
            return {'html': "", 'css': "", 'js': ""}

    def _save_pattern(self, pattern: DesignPattern):
        """Save pattern to file"""
        try:
            pattern_path = self.patterns_path / f"{pattern.name}.json"
            with open(pattern_path, 'w') as f:
                json.dump(pattern.__dict__, f, indent=2)
        except Exception as e:
            print(f"Error saving pattern: {str(e)}")
            raise 