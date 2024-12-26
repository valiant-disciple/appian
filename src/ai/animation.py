from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import re
from .base_analyzers import BaseAnalyzer, AnalysisResult
from .utils import parse_size_value

@dataclass
class AnimationResult(AnalysisResult):
    """Structure for animation analysis results"""
    overall_score: float = 0.0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[Dict[str, Any]] = field(default_factory=list)
    performance_score: float = 0.0
    timing_functions: List[str] = field(default_factory=list)
    duration_consistency: float = 0.0

class AnimationAnalyzer(BaseAnalyzer):
    async def analyze(self, html: str, css: str, js: Optional[str] = None) -> AnimationResult:
        try:
            issues = []
            suggestions = []
            timing_functions = []
            durations = []
            
            # Extract animation properties
            animation_matches = re.findall(r'animation:\s*([^;]+);', css)
            transition_matches = re.findall(r'transition:\s*([^;]+);', css)
            
            # Analyze animations
            for animation in animation_matches:
                parts = animation.split()
                if len(parts) >= 2:
                    duration = parse_size_value(parts[1])
                    if duration:
                        durations.append(duration)
                        if duration > 1:
                            issues.append({
                                'severity': 'medium',
                                'message': 'Long animation duration',
                                'suggestion': 'Keep animations under 1 second'
                            })
                    
                    if 'ease' in animation:
                        timing_functions.append('ease')
                    elif 'linear' in animation:
                        timing_functions.append('linear')
            
            # Analyze transitions
            for transition in transition_matches:
                if 'all' in transition:
                    issues.append({
                        'severity': 'medium',
                        'message': 'Transition on all properties',
                        'suggestion': 'Specify exact properties to transition'
                    })
            
            # Check for hardware acceleration
            if 'transform' not in css and (animation_matches or transition_matches):
                suggestions.append({
                    'severity': 'medium',
                    'message': 'No hardware acceleration',
                    'suggestion': 'Use transform for better performance'
                })
            
            # Calculate metrics
            performance_score = 1.0 - (len(issues) * 0.2)
            duration_consistency = len(set(durations)) / len(durations) if durations else 1
            
            # Calculate overall score
            overall_score = max(0, (performance_score + duration_consistency) / 2)
            
            return AnimationResult(
                overall_score=overall_score,
                issues=issues,
                suggestions=suggestions,
                performance_score=performance_score,
                timing_functions=timing_functions,
                duration_consistency=duration_consistency
            )
            
        except Exception as e:
            print(f"Error in animation analysis: {str(e)}")
            return AnimationResult(
                overall_score=0,
                issues=[{
                    'severity': 'high',
                    'message': f'Animation analysis error: {str(e)}',
                    'suggestion': 'Please check your CSS syntax'
                }],
                suggestions=[],
                performance_score=0,
                timing_functions=[],
                duration_consistency=0
            ) 