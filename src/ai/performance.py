from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
import re
from .base_analyzers import BaseAnalyzer, AnalysisResult

@dataclass
class PerformanceResult(AnalysisResult):
    """Structure for performance analysis results"""
    load_time: float = 0.0
    resource_size: Dict[str, int] = field(default_factory=dict)
    optimization_suggestions: List[Dict[str, Any]] = field(default_factory=list)

class PerformanceAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__()

    async def _analyze(self, html: str, css: str, js: Optional[str] = None) -> PerformanceResult:
        issues = []
        suggestions = []
        optimization_suggestions = []
        
        # Calculate resource sizes
        html_size = len(html.encode('utf-8'))
        css_size = len(css.encode('utf-8'))
        js_size = len(js.encode('utf-8')) if js else 0
        
        # Check file sizes
        if css_size > 50000:
            issues.append({
                'severity': 'medium',
                'message': 'Large CSS file size',
                'suggestion': 'Consider minifying CSS and removing unused styles'
            })
            optimization_suggestions.append({
                'type': 'css',
                'suggestion': 'Minify CSS'
            })
        
        if js and js_size > 100000:
            issues.append({
                'severity': 'high',
                'message': 'Large JavaScript file size',
                'suggestion': 'Consider code splitting and minification'
            })
            optimization_suggestions.append({
                'type': 'js',
                'suggestion': 'Split JavaScript into smaller chunks'
            })
        
        # Check for unoptimized images
        soup = BeautifulSoup(html, 'html.parser')
        images = soup.find_all('img')
        for img in images:
            if not img.get('loading') == 'lazy':
                issues.append({
                    'severity': 'medium',
                    'message': 'Image missing lazy loading',
                    'suggestion': f'Add loading="lazy" to image: {img}'
                })
        
        # Estimate load time (very rough estimation)
        total_size = html_size + css_size + js_size
        estimated_load_time = total_size / 1024 / 100  # Rough estimate in seconds
        
        # Calculate overall score
        overall_score = max(0, 1 - (len(issues) * 0.2))
        
        return PerformanceResult(
            overall_score=overall_score,
            issues=issues,
            suggestions=suggestions,
            load_time=estimated_load_time,
            resource_size={
                'html': html_size,
                'css': css_size,
                'js': js_size
            },
            optimization_suggestions=optimization_suggestions
        )
        
    async def analyze(self, html: str, css: str, js: Optional[str] = None) -> PerformanceResult:
        try:
            return await self._analyze(html, css, js)
            
        except Exception as e:
            print(f"Error in performance analysis: {str(e)}")
            return PerformanceResult(
                overall_score=0,
                issues=[{
                    'severity': 'high',
                    'message': f'Performance analysis error: {str(e)}',
                    'suggestion': 'Please check your code syntax'
                }],
                suggestions=[],
                load_time=0,
                resource_size={},
                optimization_suggestions=[]
            ) 