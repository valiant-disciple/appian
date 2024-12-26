from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
import re
from .base_analyzers import BaseAnalyzer, AnalysisResult

@dataclass
class ResponsiveResult(AnalysisResult):
    """Structure for responsive design analysis results"""
    breakpoints: List[Dict[str, Any]] = field(default_factory=list)
    viewport_issues: List[Dict[str, Any]] = field(default_factory=list)

class ResponsiveAnalyzer(BaseAnalyzer):
    async def _analyze(self, html: str, css: str, js: Optional[str] = None) -> ResponsiveResult:
        try:
            issues = []
            suggestions = []
            breakpoints = []
            viewport_issues = []
            
            # Check viewport meta tag
            soup = BeautifulSoup(html, 'html.parser')
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            if not viewport:
                viewport_issues.append({
                    'type': 'missing',
                    'element': 'viewport meta'
                })
                issues.append({
                    'severity': 'high',
                    'message': 'Missing viewport meta tag',
                    'suggestion': 'Add <meta name="viewport" content="width=device-width, initial-scale=1.0">'
                })
            
            # Extract media queries
            media_queries = re.findall(r'@media[^{]+\{', css)
            if not media_queries:
                issues.append({
                    'severity': 'medium',
                    'message': 'No media queries found',
                    'suggestion': 'Add media queries for responsive design'
                })
            
            # Calculate overall score
            overall_score = max(0, 1 - (len(issues) * 0.2))
            
            return ResponsiveResult(
                overall_score=overall_score,
                issues=issues,
                suggestions=suggestions,
                breakpoints=breakpoints,
                viewport_issues=viewport_issues
            )
            
        except Exception as e:
            print(f"Error in responsive analysis: {str(e)}")
            return ResponsiveResult(
                overall_score=0,
                issues=[{
                    'severity': 'high',
                    'message': f'Responsive analysis error: {str(e)}',
                    'suggestion': 'Please check your code syntax'
                }]
            ) 