from typing import Dict, List, Any, Optional, Tuple
from .base_analyzers import BaseAnalyzer, AnalysisResult

class CodeAnalyzer:
    """Main analyzer that coordinates all other analyzers"""
    
    def __init__(self):
        """Initialize all analyzers"""
        try:
            from .accessibility import AccessibilityAnalyzer
            from .validator import CodeValidator
            from .performance import PerformanceAnalyzer
            from .responsive import ResponsiveAnalyzer
            from .typography import TypographyAnalyzer
            from .color_system import ColorAnalyzer
            from .layout_analyzer import LayoutAnalyzer
            from .interaction import InteractionAnalyzer
            from .animation import AnimationAnalyzer

            self.analyzers = {
                'accessibility': AccessibilityAnalyzer(),
                'validator': CodeValidator(),
                'performance': PerformanceAnalyzer(),
                'responsive': ResponsiveAnalyzer(),
                'typography': TypographyAnalyzer(),
                'color': ColorAnalyzer(),
                'layout': LayoutAnalyzer(),
                'interaction': InteractionAnalyzer(),
                'animation': AnimationAnalyzer()
            }
        except Exception as e:
            print(f"Error initializing analyzers: {str(e)}")
            self.analyzers = {}

    async def analyze_code(self, html: str, css: str, js: Optional[str] = None) -> Dict[str, AnalysisResult]:
        """Analyze code using all available analyzers"""
        try:
            results = {}
            for name, analyzer in self.analyzers.items():
                try:
                    result = await analyzer.analyze(html, css, js)
                    if isinstance(result, AnalysisResult):
                        results[name] = result
                    else:
                        print(f"Invalid result from {name} analyzer")
                        results[name] = AnalysisResult(
                            overall_score=0,
                            issues=[{
                                'severity': 'high',
                                'message': f'Invalid result from {name} analyzer',
                                'suggestion': 'Please check analyzer implementation'
                            }]
                        )
                except Exception as e:
                    print(f"Error in {name} analyzer: {str(e)}")
                    results[name] = AnalysisResult(
                        overall_score=0,
                        issues=[{
                            'severity': 'high',
                            'message': f'Error in {name} analysis: {str(e)}',
                            'suggestion': 'Please check your code syntax'
                        }]
                    )
            return results
        except Exception as e:
            print(f"Error in code analysis: {str(e)}")
            return {'error': AnalysisResult(
                overall_score=0,
                issues=[{
                    'severity': 'high',
                    'message': f'Analysis error: {str(e)}',
                    'suggestion': 'Please check your code'
                }]
            )}

    def _create_error_result(self, analyzer_name: str, error_message: str) -> AnalysisResult:
        """Create an error result for failed analyzers"""
        return AnalysisResult(
            overall_score=0,
            issues=[{
                'severity': 'high',
                'message': f'Error in {analyzer_name} analysis: {error_message}',
                'suggestion': 'Please check your code syntax and try again'
            }],
            suggestions=[]
        )