from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ComponentTemplate:
    """Template for common web components"""
    name: str
    description: str
    html_template: str
    css_template: str
    js_template: str
    props: Dict[str, str] = None
    requirements: List[str] = None

class AIPrompts:
    """Enhanced AI prompt system"""
    
    # Master system prompt for setting AI behavior
    SYSTEM_PROMPT = """You are an expert web developer and designer with deep understanding of modern web technologies.
Your primary role is to help users create exactly what they envision by:

1. Understanding Requirements:
- Extract specific requirements from user descriptions
- Ask clarifying questions when needed
- Identify design patterns and components
- Consider user experience implications

2. Code Generation:
- Generate pixel-perfect implementations
- Use modern, semantic HTML
- Write efficient, maintainable CSS
- Implement interactive features with JavaScript
- Follow accessibility guidelines
- Ensure responsive design
- Optimize performance

3. Component Understanding:
- Navigation menus
- Hero sections
- Cards and grids
- Forms and inputs
- Modals and popups
- Carousels and sliders
- Tables and data displays
- Authentication flows
- Shopping carts
- Payment integrations
- Social media features
- Search functionality
- Filters and sorting
- Comments and ratings
- User profiles
- File upload/download
- Maps and location features
- Analytics integration
- API integration
- Real-time features

4. Design Patterns:
- Responsive layouts
- Mobile-first design
- Progressive enhancement
- Atomic design principles
- Component-based architecture
- State management
- Event handling
- Data validation
- Error handling
- Loading states
- Animation patterns
- Interaction patterns

5. Best Practices:
- Clean, maintainable code
- Performance optimization
- Security considerations
- Cross-browser compatibility
- Progressive enhancement
- Accessibility (WCAG 2.1)
- SEO optimization
- Documentation
- Testing strategies

When generating code:
1. Provide complete, working solutions
2. Include all necessary HTML, CSS, and JavaScript
3. Add detailed comments explaining functionality
4. Consider edge cases and error states
5. Include responsive design
6. Implement accessibility features
7. Add appropriate animations/transitions
8. Include loading states
9. Handle errors gracefully
10. Optimize for performance

Format your responses as structured suggestions:
{
    "type": "component|feature|modification",
    "description": "Brief description",
    "explanation": "Detailed explanation",
    "requirements": ["list", "of", "requirements"],
    "code": {
        "html": "HTML code",
        "css": "CSS code",
        "js": "JavaScript code"
    },
    "alternatives": [{
        "description": "Alternative approach",
        "code": {
            "html": "...",
            "css": "...",
            "js": "..."
        }
    }],
    "testing": ["test cases"],
    "accessibility": ["a11y considerations"],
    "browser_support": ["browser compatibility notes"],
    "performance": ["performance considerations"]
}
"""

    # Common component templates
    COMPONENTS = {
        "navigation": ComponentTemplate(
            name="Navigation",
            description="Responsive navigation menu",
            html_template="""
<nav class="nav-container">
    <div class="nav-brand">
        <a href="#" class="nav-logo">{logo}</a>
    </div>
    <button class="nav-toggle" aria-label="Toggle navigation">
        <span class="nav-toggle-icon"></span>
    </button>
    <div class="nav-menu">
        {menu_items}
    </div>
</nav>
""",
            css_template="""
.nav-container {
    /* Navigation styles */
}
""",
            js_template="""
// Navigation functionality
document.querySelector('.nav-toggle').addEventListener('click', function() {
    document.querySelector('.nav-menu').classList.toggle('active');
});
"""
        ),
        # Add more component templates...
    }

    @staticmethod
    def get_analysis_prompt(html: str, css: str, js: str) -> str:
        """Generate comprehensive analysis prompt"""
        return f"""Please analyze this code and provide detailed improvements:

Current Code:
HTML:
{html}
CSS:
{css}
JavaScript:
{js}
Please provide:
1. Component identification
2. Design pattern analysis
3. Performance optimization opportunities
4. Accessibility improvements
5. Responsive design enhancements
6. Interactive feature suggestions
7. Visual enhancement ideas
8. Code organization improvements
9. Error handling recommendations
10. Testing strategies

Format your response using the standard suggestion structure."""

    @staticmethod
    def get_implementation_prompt(request: str, existing_code: Optional[Dict[str, str]] = None) -> str:
        """Generate implementation prompt for user request"""
        context = ""
        if existing_code:
            context = "\n".join([
                "Existing Code:",
                f"HTML:\n{existing_code.get('html', '')}",
                f"CSS:\n{existing_code.get('css', '')}",
                f"JavaScript:\n{existing_code.get('js', '')}"
            ])

        return f"""User Request: {request}

{context}

Please provide a complete implementation that:
1. Exactly matches the user's requirements
2. Uses modern best practices
3. Is fully responsive
4. Includes necessary interactions
5. Handles all states (loading, error, empty)
6. Is accessible
7. Is optimized for performance
8. Includes appropriate animations
9. Has error handling
10. Is well-documented

Format your response using the standard suggestion structure."""

    @staticmethod
    def get_modification_prompt(request: str, current_code: Dict[str, str]) -> str:
        """Generate prompt for code modification"""
        return f"""Modification Request: {request}

Current Code:
HTML:
{current_code.get('html', '')}
CSS:
{current_code.get('css', '')}
JavaScript:
{current_code.get('js', '')}

Please provide modifications that:
1. Implement the requested changes
2. Maintain existing functionality
3. Preserve code structure
4. Follow consistent style
5. Consider performance impact
6. Maintain accessibility
7. Include transition animations
8. Handle edge cases
9. Update documentation
10. Include testing considerations

Format your response using the standard suggestion structure."""

    # Add more specialized prompts...