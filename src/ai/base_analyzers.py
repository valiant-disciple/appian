from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class AnalysisResult:
    """Base class for analysis results"""
    overall_score: float = 0.0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[Dict[str, Any]] = field(default_factory=list)

class BaseAnalyzer:
    """Base class for all analyzers"""
    
    async def analyze(self, html: str, css: str, js: Optional[str] = None) -> AnalysisResult:
        """Base analyze method that must be implemented by all analyzers"""
        try:
            return await self._analyze(html, css, js)
        except Exception as e:
            print(f"Error in {self.__class__.__name__}: {str(e)}")
            return AnalysisResult(
                overall_score=0,
                issues=[{
                    'severity': 'high',
                    'message': f'Analysis error in {self.__class__.__name__}: {str(e)}',
                    'suggestion': 'Please check your code syntax'
                }]
            )

    async def _analyze(self, html: str, css: str, js: Optional[str] = None) -> AnalysisResult:
        """Internal analyze method to be implemented by subclasses"""
        raise NotImplementedError(f"{self.__class__.__name__} must implement _analyze method")