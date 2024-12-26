from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
import re
from .base_analyzers import BaseAnalyzer, AnalysisResult

@dataclass
class InteractionResult(AnalysisResult):
    """Structure for interaction analysis results"""
    overall_score: float = 0.0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[Dict[str, Any]] = field(default_factory=list)
    accessibility_score: float = 0.0
    feedback_score: float = 0.0
    event_coverage: Dict[str, int] = field(default_factory=dict)

class InteractionAnalyzer(BaseAnalyzer):
    async def analyze(self, html: str, css: str, js: Optional[str] = None) -> InteractionResult:
        try:
            issues = []
            suggestions = []
            events = {}
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check interactive elements
            interactive = soup.find_all(['button', 'a', 'input', 'select', 'textarea'])
            
            # Analyze hover states
            hover_states = len(re.findall(r':hover', css))
            if hover_states < len(interactive):
                issues.append({
                    'severity': 'medium',
                    'message': 'Missing hover states',
                    'suggestion': 'Add hover effects for interactive elements'
                })
            
            # Analyze focus states
            focus_states = len(re.findall(r':focus', css))
            if focus_states < len(interactive):
                issues.append({
                    'severity': 'high',
                    'message': 'Missing focus states',
                    'suggestion': 'Add focus styles for accessibility'
                })
            
            # Analyze JavaScript events
            if js:
                click_events = len(re.findall(r'addEventListener\([\'"]click[\'"]', js))
                keyboard_events = len(re.findall(r'addEventListener\([\'"]key', js))
                events = {
                    'click': click_events,
                    'keyboard': keyboard_events
                }
                
                if keyboard_events < click_events:
                    issues.append({
                        'severity': 'high',
                        'message': 'Insufficient keyboard support',
                        'suggestion': 'Add keyboard event handlers for accessibility'
                    })
            
            # Calculate metrics
            accessibility_score = 1.0 - (len([i for i in issues if i['severity'] == 'high']) * 0.3)
            feedback_score = min(1.0, (hover_states + focus_states) / (len(interactive) * 2)) if interactive else 1.0
            
            # Calculate overall score
            overall_score = max(0, (accessibility_score + feedback_score) / 2)
            
            return InteractionResult(
                overall_score=overall_score,
                issues=issues,
                suggestions=suggestions,
                accessibility_score=accessibility_score,
                feedback_score=feedback_score,
                event_coverage=events
            )
            
        except Exception as e:
            print(f"Error in interaction analysis: {str(e)}")
            return InteractionResult(
                overall_score=0,
                issues=[{
                    'severity': 'high',
                    'message': f'Interaction analysis error: {str(e)}',
                    'suggestion': 'Please check your code syntax'
                }],
                suggestions=[],
                accessibility_score=0,
                feedback_score=0,
                event_coverage={}
            ) 