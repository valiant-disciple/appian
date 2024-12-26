from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from .llm_client import LLMClient
import json

@dataclass
class Suggestion:
    id: str
    type: str  # 'aesthetic', 'codebase', 'feature', 'component'
    title: str
    description: str
    preview_code: Dict[str, str]
    implementation: str
    applied: bool = False

class InteractiveSuggestions:
    def __init__(self):
        self.llm_client = LLMClient()

    async def analyze_component(self, component_type: str, current_code: Dict[str, str]) -> List[Suggestion]:
        """Analyze and suggest improvements for specific component"""
        prompt = f"""
Analyze this {component_type} component:
{json.dumps(current_code, indent=2)}

Suggest improvements for:
1. Functionality
2. User experience
3. Accessibility
4. Performance
5. Best practices

Return as JSON array with:
- title
- description
- preview_code (with html, css, js)
- implementation steps
"""
        response = await self.llm_client.generate_response(prompt, current_code)
        try:
            suggestions = json.loads(response)
            return [
                Suggestion(
                    id=f"component_{i}",
                    type="component",
                    title=s.get('title', ''),
                    description=s.get('description', ''),
                    preview_code=s.get('preview_code', {}),
                    implementation=s.get('implementation', '')
                )
                for i, s in enumerate(suggestions)
            ]
        except:
            return []

    async def generate_preview(self, current_code: Dict[str, str], suggestion: str) -> Dict[str, str]:
        """Generate preview code for a suggestion"""
        prompt = f"""
Given this code:
HTML: {current_code.get('html', '')}
CSS: {current_code.get('css', '')}
JS: {current_code.get('js', '')}

Generate the modified code to implement this suggestion:
{suggestion}

Return as JSON with html, css, and js keys.
"""
        response = await self.llm_client.generate_response(prompt, current_code)
        try:
            return json.loads(response)
        except:
            return current_code

    async def get_all_suggestions(self, code: Dict[str, str]) -> List[Suggestion]:
        """Get both aesthetic and codebase suggestions"""
        aesthetic = await self.get_aesthetic_suggestions(code)
        codebase = await self.get_codebase_suggestions(code)
        return aesthetic + codebase

    async def get_aesthetic_suggestions(self, code: Dict[str, str]) -> List[Suggestion]:
        """Get aesthetic improvement suggestions"""
        prompt = f"""
Analyze this code for visual improvements:
HTML: {code.get('html', '')}
CSS: {code.get('css', '')}

Generate 5 specific visual improvement suggestions.
For each suggestion, provide:
1. A title
2. Detailed description
3. Implementation steps
4. Preview code changes

Return as JSON array.
"""
        response = await self.llm_client.generate_response(prompt, code)
        try:
            suggestions = json.loads(response)
            return [
                Suggestion(
                    id=f"aesthetic_{i}",
                    type="aesthetic",
                    title=s.get('title', ''),
                    description=s.get('description', ''),
                    preview_code=s.get('preview_code', {}),
                    implementation=s.get('implementation', '')
                )
                for i, s in enumerate(suggestions)
            ]
        except:
            return []

    async def get_codebase_suggestions(self, code: Dict[str, str]) -> List[Suggestion]:
        """Get codebase improvement suggestions"""
        prompt = f"""
Analyze this code for technical improvements:
HTML: {code.get('html', '')}
CSS: {code.get('css', '')}
JS: {code.get('js', '')}

Generate 5 specific code improvement suggestions.
For each suggestion, provide:
1. A title
2. Detailed description
3. Implementation steps
4. Preview code changes

Return as JSON array.
"""
        response = await self.llm_client.generate_response(prompt, code)
        try:
            suggestions = json.loads(response)
            return [
                Suggestion(
                    id=f"codebase_{i}",
                    type="codebase",
                    title=s.get('title', ''),
                    description=s.get('description', ''),
                    preview_code=s.get('preview_code', {}),
                    implementation=s.get('implementation', '')
                )
                for i, s in enumerate(suggestions)
            ]
        except:
            return [] 