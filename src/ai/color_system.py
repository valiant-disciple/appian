from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import re
from .base_analyzers import BaseAnalyzer, AnalysisResult
from .utils import normalize_color, analyze_color_harmony

@dataclass
class ColorResult(AnalysisResult):
    """Structure for color analysis results"""
    palette: Dict[str, str] = field(default_factory=dict)
    contrast_ratios: Dict[str, float] = field(default_factory=dict)
    harmony_score: float = 0.0

class ColorAnalyzer(BaseAnalyzer):
    async def _analyze(self, html: str, css: str, js: Optional[str] = None) -> ColorResult:
        try:
            issues = []
            suggestions = []
            colors = set()
            
            # Extract colors from CSS
            color_matches = re.findall(r'(?:color|background|border):\s*([^;]+);', css)
            for match in color_matches:
                normalized = normalize_color(match)
                if normalized:
                    colors.add(normalized)
            
            # Analyze color count
            if len(colors) > 5:
                issues.append({
                    'severity': 'medium',
                    'message': 'Too many colors',
                    'suggestion': 'Limit color palette to 3-5 main colors'
                })
            
            # Create color palette
            palette = {
                'primary': next(iter(colors), '#000000'),
                'secondary': list(colors)[1] if len(colors) > 1 else '#ffffff',
                'accent': list(colors)[2] if len(colors) > 2 else '#0000ff'
            }
            
            # Calculate harmony score
            harmony_type, harmony_score = analyze_color_harmony(list(colors))
            
            # Calculate overall score
            overall_score = max(0, 1 - (len(issues) * 0.2))
            
            return ColorResult(
                overall_score=overall_score,
                issues=issues,
                suggestions=suggestions,
                palette=palette,
                contrast_ratios={},
                harmony_score=harmony_score
            )
            
        except Exception as e:
            print(f"Error in color analysis: {str(e)}")
            return ColorResult(
                overall_score=0,
                issues=[{
                    'severity': 'high',
                    'message': f'Color analysis error: {str(e)}',
                    'suggestion': 'Please check your CSS syntax'
                }]
            ) 