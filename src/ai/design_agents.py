from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
from PIL import Image
import base64
import io
from groq import AsyncGroq
from .analyzer import CodeAnalyzer
from .style_guide import StyleGuideManager
from .design_patterns import DesignPatternManager

@dataclass
class DesignSuggestion:
    """Structure for design suggestions"""
    category: str
    priority: str
    description: str
    implementation: Dict[str, Any]
    preview: Optional[Dict[str, str]] = None

class DesignAgent:
    """Base class for design agents"""
    def __init__(self, name: str, expertise: str, client: AsyncGroq):
        self.name = name
        self.expertise = expertise
        self.client = client
        self.conversation_history = []
        self.style_guide_manager = StyleGuideManager()
        self.pattern_manager = DesignPatternManager()

    async def analyze(self, message: str) -> str:
        """Analyze based on expertise"""
        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are {self.name}, an expert in {self.expertise}. {self.get_persona_prompt()}"},
                    *self.conversation_history,
                    {"role": "user", "content": message}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=2048
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in agent analysis: {str(e)}")
            raise

    def get_persona_prompt(self) -> str:
        """Get persona-specific prompt"""
        raise NotImplementedError("Subclasses must implement get_persona_prompt")

class VisualDesignExpert(DesignAgent):
    """Visual design expert agent"""
    def get_persona_prompt(self) -> str:
        return """
        You are a senior visual designer with expertise in:
        - Color theory and harmony
        - Typography and visual hierarchy
        - Layout composition and grid systems
        - Visual balance and whitespace
        - Modern design trends
        - Brand consistency
        
        Analyze designs and provide specific, actionable feedback focusing on visual aesthetics.
        Use clear examples and explain the reasoning behind your suggestions.
        """

    async def analyze_screenshot(self, screenshot: Image.Image) -> Dict[str, Any]:
        """Analyze screenshot for visual design aspects"""
        try:
            # Convert image to base64
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Get visual analysis
            analysis = await self.analyze(f"""
            Analyze this website screenshot for visual design quality:
            [Image: {img_str}]
            
            Focus on:
            1. Color harmony and contrast
            2. Typography hierarchy and readability
            3. Layout balance and composition
            4. Use of whitespace
            5. Visual consistency
            6. Modern design principles
            
            Provide specific, actionable feedback for each aspect.
            Format your response as JSON with the following structure:
            {{
                "color_analysis": {{ "score": float, "issues": [], "suggestions": [] }},
                "typography_analysis": {{ "score": float, "issues": [], "suggestions": [] }},
                "layout_analysis": {{ "score": float, "issues": [], "suggestions": [] }},
                "whitespace_analysis": {{ "score": float, "issues": [], "suggestions": [] }},
                "consistency_analysis": {{ "score": float, "issues": [], "suggestions": [] }},
                "overall_score": float,
                "priority_improvements": []
            }}
            """)
            
            import json
            return json.loads(analysis)
            
        except Exception as e:
            print(f"Error in visual analysis: {str(e)}")
            raise

class UXExpert(DesignAgent):
    """UX expert agent"""
    def get_persona_prompt(self) -> str:
        return """
        You are a senior UX designer with expertise in:
        - User flow optimization
        - Information architecture
        - Interaction design
        - Accessibility (WCAG guidelines)
        - Mobile responsiveness
        - User psychology
        
        Analyze designs from a user experience perspective and provide specific, actionable feedback.
        Focus on usability, accessibility, and user flow improvements.
        """

    async def analyze_interactions(self, screenshot: Image.Image, html: str) -> Dict[str, Any]:
        """Analyze UX aspects"""
        try:
            # Convert image to base64
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Get UX analysis
            analysis = await self.analyze(f"""
            Analyze this website's UX design:
            [Image: {img_str}]
            
            HTML Structure:
            {html[:1000]}  # First 1000 chars for context
            
            Focus on:
            1. Navigation and user flow
            2. Information hierarchy
            3. Interaction feedback
            4. Accessibility compliance
            5. Mobile responsiveness
            6. Call-to-action effectiveness
            
            Format your response as JSON with the following structure:
            {{
                "navigation_analysis": {{ "score": float, "issues": [], "suggestions": [] }},
                "hierarchy_analysis": {{ "score": float, "issues": [], "suggestions": [] }},
                "interaction_analysis": {{ "score": float, "issues": [], "suggestions": [] }},
                "accessibility_analysis": {{ "score": float, "issues": [], "suggestions": [] }},
                "responsive_analysis": {{ "score": float, "issues": [], "suggestions": [] }},
                "cta_analysis": {{ "score": float, "issues": [], "suggestions": [] }},
                "overall_score": float,
                "priority_improvements": []
            }}
            """)
            
            import json
            return json.loads(analysis)
            
        except Exception as e:
            print(f"Error in UX analysis: {str(e)}")
            raise

class UIImplementer(DesignAgent):
    """UI implementation expert agent"""
    def __init__(self, name: str, expertise: str, client: AsyncGroq):
        super().__init__(name, expertise, client)
        self.code_analyzer = CodeAnalyzer()

    def get_persona_prompt(self) -> str:
        return """
        You are a senior UI developer with expertise in:
        - Modern HTML/CSS/JS practices
        - Responsive design implementation
        - Performance optimization
        - Cross-browser compatibility
        - Animation and transitions
        - Component-based architecture
        
        Provide specific code implementations for design improvements.
        Focus on maintainable, performant, and accessible code.
        """

    async def create_implementation_plan(self, 
                                      design_suggestions: List[Dict[str, Any]],
                                      priorities: List[str]) -> List[Dict[str, Any]]:
        """Create implementation plan for design changes"""
        try:
            # Convert suggestions to implementation steps
            implementation_plan = []
            
            for priority in priorities:
                relevant_suggestions = [s for s in design_suggestions 
                                     if s['category'].lower() == priority.lower()]
                
                for suggestion in relevant_suggestions:
                    # Get appropriate design pattern
                    pattern = self.pattern_manager.suggest_patterns(
                        suggestion['category'],
                        suggestion.get('constraints', {})
                    )
                    
                    if pattern:
                        implementation = await self._create_implementation_step(
                            suggestion,
                            pattern[0]['pattern']  # Use best matching pattern
                        )
                        implementation_plan.append(implementation)
            
            return implementation_plan
            
        except Exception as e:
            print(f"Error creating implementation plan: {str(e)}")
            raise

    async def implement_single_change(self, 
                                    change: Dict[str, Any],
                                    current_code: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Implement a single design change"""
        try:
            # Get implementation details
            implementation = await self.analyze(f"""
            Implement this design change:
            {change['description']}
            
            Current code:
            HTML: {current_code['html'][:500]}
            CSS: {current_code['css'][:500]}
            JS: {current_code.get('js', '')[:500]}
            
            Provide specific code changes in JSON format:
            {{
                "html_changes": {{ "selector": "string", "code": "string" }},
                "css_changes": {{ "selector": "string", "code": "string" }},
                "js_changes": {{ "code": "string" }} (optional)
            }}
            """)
            
            import json
            changes = json.loads(implementation)
            
            # Apply changes to code
            updated_code = self._apply_code_changes(current_code, changes)
            
            return {
                'code': updated_code,
                'changes': changes,
                'preview': None  # Preview will be generated separately
            }
            
        except Exception as e:
            print(f"Error implementing change: {str(e)}")
            return None

    async def _create_implementation_step(self, 
                                        suggestion: Dict[str, Any],
                                        pattern_name: str) -> Dict[str, Any]:
        """Create implementation step from suggestion and pattern"""
        try:
            # Get pattern implementation
            pattern_implementation = self.pattern_manager.apply_pattern(
                pattern_name,
                suggestion.get('context', {})
            )
            
            return {
                'description': suggestion['description'],
                'pattern': pattern_name,
                'implementation': pattern_implementation,
                'type': suggestion['category'],
                'priority': suggestion.get('priority', 'medium')
            }
            
        except Exception as e:
            print(f"Error creating implementation step: {str(e)}")
            raise

    def _apply_code_changes(self, 
                          current_code: Dict[str, str],
                          changes: Dict[str, Any]) -> Dict[str, str]:
        """Apply code changes to current code"""
        try:
            from bs4 import BeautifulSoup
            import cssutils
            
            # Apply HTML changes
            if 'html_changes' in changes:
                soup = BeautifulSoup(current_code['html'], 'html.parser')
                elements = soup.select(changes['html_changes']['selector'])
                for element in elements:
                    element.replace_with(BeautifulSoup(changes['html_changes']['code'], 'html.parser'))
                current_code['html'] = str(soup)
            
            # Apply CSS changes
            if 'css_changes' in changes:
                stylesheet = cssutils.parseString(current_code['css'])
                # Add new CSS rules
                stylesheet.add(changes['css_changes']['code'])
                current_code['css'] = stylesheet.cssText.decode()
            
            # Apply JS changes
            if 'js_changes' in changes:
                current_code['js'] = current_code.get('js', '') + '\n' + changes['js_changes']['code']
            
            return current_code
            
        except Exception as e:
            print(f"Error applying code changes: {str(e)}")
            raise 