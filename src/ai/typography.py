from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
import re
from .base_analyzers import BaseAnalyzer, AnalysisResult
from .utils import parse_size_value

@dataclass
class TypographyResult(AnalysisResult):
    """Structure for typography analysis results"""
    font_consistency: float = 0.0
    size_hierarchy: Dict[str, List[float]] = field(default_factory=lambda: {'heading': [], 'body': []})
    line_height_ratio: float = 0.0

class TypographyAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__()

    async def _analyze(self, html: str, css: str, js: Optional[str] = None) -> TypographyResult:
        try:
            issues = []
            suggestions = []
            font_families = set()
            font_sizes = []
            line_heights = []
            
            # Extract typography-related CSS
            font_family_matches = re.findall(r'font-family:\s*([^;]+);', css)
            font_size_matches = re.findall(r'font-size:\s*([^;]+);', css)
            line_height_matches = re.findall(r'line-height:\s*([^;]+);', css)
            
            # Analyze font families
            for family in font_family_matches:
                font_families.update(f.strip().strip("'\"") for f in family.split(','))
            
            if len(font_families) > 3:
                issues.append({
                    'severity': 'medium',
                    'message': 'Too many font families',
                    'suggestion': 'Limit font families to 2-3 for better consistency'
                })
            
            # Analyze font sizes
            for size in font_size_matches:
                parsed_size = parse_size_value(size)
                if parsed_size:
                    font_sizes.append(parsed_size)
            
            # Check size hierarchy
            if font_sizes:
                min_size = min(font_sizes)
                max_size = max(font_sizes)
                if max_size / min_size < 1.5:
                    issues.append({
                        'severity': 'medium',
                        'message': 'Limited size hierarchy',
                        'suggestion': 'Create better visual hierarchy with more distinct font sizes'
                    })
            
            # Analyze line heights
            for height in line_height_matches:
                parsed_height = parse_size_value(height)
                if parsed_height:
                    line_heights.append(parsed_height)
            
            # Calculate metrics
            font_consistency = 1.0 - (len(font_families) - 1) * 0.2
            size_hierarchy = {
                'heading': [s for s in font_sizes if s > 16],
                'body': [s for s in font_sizes if s <= 16]
            }
            line_height_ratio = sum(line_heights) / len(line_heights) if line_heights else 1.5
            
            # Calculate overall score
            overall_score = max(0, 1 - (len(issues) * 0.2))
            
            return TypographyResult(
                overall_score=overall_score,
                issues=issues,
                suggestions=suggestions,
                font_consistency=font_consistency,
                size_hierarchy=size_hierarchy,
                line_height_ratio=line_height_ratio
            )
            
        except Exception as e:
            print(f"Error in typography analysis: {str(e)}")
            return TypographyResult(
                overall_score=0,
                issues=[{
                    'severity': 'high',
                    'message': f'Typography analysis error: {str(e)}',
                    'suggestion': 'Please check your CSS syntax'
                }],
                suggestions=[],
                font_consistency=0,
                size_hierarchy={'heading': [], 'body': []},
                line_height_ratio=0
            ) 