from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from .base_analyzers import BaseAnalyzer, AnalysisResult
from .utils import normalize_color, calculate_contrast_ratio

@dataclass
class AccessibilityResult(AnalysisResult):
    """Structure for accessibility analysis results"""
    wcag_score: float = 0.0
    contrast_issues: List[Dict[str, Any]] = field(default_factory=list)
    aria_issues: List[Dict[str, Any]] = field(default_factory=list)

class AccessibilityAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__()

    async def _analyze(self, html: str, css: str, js: Optional[str] = None) -> AccessibilityResult:
        issues = []
        suggestions = []
        contrast_issues = []
        aria_issues = []
        
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Check for alt text
        images = soup.find_all('img')
        for img in images:
            if not img.get('alt'):
                aria_issues.append({
                    'element': 'img',
                    'issue': 'Missing alt text'
                })
                issues.append({
                    'severity': 'high',
                    'message': 'Image missing alt text',
                    'suggestion': f'Add alt text to image: {img}'
                })
        
        # Check for ARIA labels
        interactive = soup.find_all(['button', 'a', 'input'])
        for element in interactive:
            if not (element.get('aria-label') or element.get('aria-labelledby')):
                aria_issues.append({
                    'element': element.name,
                    'issue': 'Missing ARIA label'
                })
                issues.append({
                    'severity': 'medium',
                    'message': f'Interactive element missing ARIA label',
                    'suggestion': f'Add aria-label to {element.name}'
                })
        
        # Check color contrast
        if 'color' in css and 'background' in css:
            text_color = normalize_color(css.split('color:')[1].split(';')[0].strip())
            bg_color = normalize_color(css.split('background:')[1].split(';')[0].strip())
            if text_color and bg_color:
                contrast = calculate_contrast_ratio(text_color, bg_color)
                if contrast < 4.5:
                    contrast_issues.append({
                        'colors': [text_color, bg_color],
                        'contrast_ratio': contrast
                    })
                    issues.append({
                        'severity': 'high',
                        'message': 'Insufficient color contrast',
                        'suggestion': 'Increase contrast ratio to at least 4.5:1'
                    })
        
        # Calculate scores
        wcag_score = max(0, 1 - (len(issues) * 0.2))
        overall_score = wcag_score
        
        return AccessibilityResult(
            overall_score=overall_score,
            issues=issues,
            suggestions=suggestions,
            wcag_score=wcag_score,
            contrast_issues=contrast_issues,
            aria_issues=aria_issues
        )
        
    async def analyze(self, html: str, css: str, js: Optional[str] = None) -> AccessibilityResult:
        try:
            return await self._analyze(html, css, js)
        except Exception as e:
            print(f"Error in accessibility analysis: {str(e)}")
            return AccessibilityResult(
                overall_score=0,
                issues=[{
                    'severity': 'high',
                    'message': f'Accessibility analysis error: {str(e)}',
                    'suggestion': 'Please check your HTML and CSS syntax'
                }],
                suggestions=[],
                wcag_score=0,
                contrast_issues=[],
                aria_issues=[]
            ) 