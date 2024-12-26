from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from .llm_client import LLMClient
from .base_analyzers import BaseAnalyzer, AnalysisResult

@dataclass
class AestheticsResult(AnalysisResult):
    """Structure for aesthetics analysis results"""
    design_score: float = 0.0
    color_harmony: float = 0.0
    typography_score: float = 0.0
    layout_balance: float = 0.0
    suggested_improvements: List[Dict[str, str]] = field(default_factory=list)

class AestheticsEnhancementAgent(BaseAnalyzer):
    """Agent for analyzing and improving design aesthetics"""
    
    def __init__(self):
        super().__init__()
        self.llm_client = LLMClient()

    async def _analyze(self, html: str, css: str, js: Optional[str] = None) -> AestheticsResult:
        """Analyze design aesthetics"""
        try:
            issues = []
            suggestions = []
            
            # Analyze current design
            design_analysis = await self._analyze_design(html, css)
            color_analysis = await self._analyze_colors(css)
            typography_analysis = await self._analyze_typography(css)
            layout_analysis = await self._analyze_layout(html, css)
            
            # Generate improvement suggestions
            suggested_improvements = await self._generate_improvements(
                design_analysis,
                color_analysis,
                typography_analysis,
                layout_analysis
            )
            
            # Calculate scores
            design_score = design_analysis.get('score', 0.0)
            color_harmony = color_analysis.get('harmony', 0.0)
            typography_score = typography_analysis.get('score', 0.0)
            layout_balance = layout_analysis.get('balance', 0.0)
            
            overall_score = (design_score + color_harmony + typography_score + layout_balance) / 4
            
            return AestheticsResult(
                overall_score=overall_score,
                issues=issues,
                suggestions=suggestions,
                design_score=design_score,
                color_harmony=color_harmony,
                typography_score=typography_score,
                layout_balance=layout_balance,
                suggested_improvements=suggested_improvements
            )
            
        except Exception as e:
            print(f"Error in aesthetics analysis: {str(e)}")
            return AestheticsResult(
                overall_score=0,
                issues=[{
                    'severity': 'high',
                    'message': f'Aesthetics analysis error: {str(e)}',
                    'suggestion': 'Please check your code syntax'
                }]
            )

    async def _analyze_design(self, html: str, css: str) -> Dict[str, float]:
        """Analyze overall design aesthetics"""
        prompt = f"""
Analyze the overall design aesthetics of this code:

HTML:
{html}

CSS:
{css}

Focus on:
1. Visual hierarchy
2. Consistency
3. White space usage
4. Design principles
5. Modern design trends

Return a score between 0 and 1.
""".strip()

        response = await self.llm_client.generate_response(prompt, {'html': html, 'css': css})
        return {'score': float(response) if response.replace('.','').isdigit() else 0.5}

    async def _analyze_colors(self, css: str) -> Dict[str, float]:
        """Analyze color harmony and usage"""
        prompt = f"""
Analyze the color usage in this CSS:

{css}

Focus on:
1. Color harmony
2. Contrast
3. Brand consistency
4. Accessibility
5. Emotional impact

Return a harmony score between 0 and 1.
""".strip()

        response = await self.llm_client.generate_response(prompt, {'css': css})
        return {'harmony': float(response) if response.replace('.','').isdigit() else 0.5}

    async def _analyze_typography(self, css: str) -> Dict[str, float]:
        """Analyze typography aesthetics"""
        prompt = f"""
Analyze the typography in this CSS:

{css}

Focus on:
1. Font choices
2. Hierarchy
3. Readability
4. Spacing
5. Responsiveness

Return a score between 0 and 1.
""".strip()

        response = await self.llm_client.generate_response(prompt, {'css': css})
        return {'score': float(response) if response.replace('.','').isdigit() else 0.5}

    async def _analyze_layout(self, html: str, css: str) -> Dict[str, float]:
        """Analyze layout aesthetics"""
        prompt = f"""
Analyze the layout aesthetics:

HTML:
{html}

CSS:
{css}

Focus on:
1. Balance
2. Proportion
3. Unity
4. Emphasis
5. Rhythm

Return a balance score between 0 and 1.
""".strip()

        response = await self.llm_client.generate_response(prompt, {'html': html, 'css': css})
        return {'balance': float(response) if response.replace('.','').isdigit() else 0.5}

    async def _generate_improvements(
        self,
        design_analysis: Dict[str, float],
        color_analysis: Dict[str, float],
        typography_analysis: Dict[str, float],
        layout_analysis: Dict[str, float]
    ) -> List[Dict[str, str]]:
        """Generate specific improvement suggestions"""
        prompt = f"""
Based on the following analysis scores:
- Design: {design_analysis.get('score', 0)}
- Color Harmony: {color_analysis.get('harmony', 0)}
- Typography: {typography_analysis.get('score', 0)}
- Layout: {layout_analysis.get('balance', 0)}

Please suggest specific improvements for:
1. Visual hierarchy
2. Color scheme
3. Typography
4. Layout
5. Modern design elements

Format each suggestion as:
{{
    "category": "category_name",
    "suggestion": "detailed_suggestion",
    "implementation": "implementation_steps"
}}
""".strip()

        response = await self.llm_client.generate_response(prompt, None)
        try:
            import json
            return json.loads(response)
        except:
            return [{"category": "general", "suggestion": response, "implementation": "See suggestion"}]

    async def suggest_design_improvements(self, html: str, css: str) -> List[Dict[str, str]]:
        """Generate specific design improvement suggestions"""
        result = await self._analyze(html, css)
        return result.suggested_improvements 