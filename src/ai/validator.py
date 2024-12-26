from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
import re
from .base_analyzers import BaseAnalyzer, AnalysisResult

@dataclass
class ValidationResult(AnalysisResult):
    """Structure for code validation results"""
    html_errors: List[Dict[str, Any]] = field(default_factory=list)
    css_errors: List[Dict[str, Any]] = field(default_factory=list)
    js_errors: List[Dict[str, Any]] = field(default_factory=list)

class CodeValidator(BaseAnalyzer):
    async def _analyze(self, html: str, css: str, js: Optional[str] = None) -> ValidationResult:
        """Validate HTML, CSS, and JavaScript code"""
        try:
            issues = []
            suggestions = []
            html_errors = []
            css_errors = []
            js_errors = []
            
            # Validate HTML
            try:
                soup = BeautifulSoup(html, 'html.parser')
                
                # Check for basic HTML structure
                if not soup.find('html'):
                    html_errors.append({
                        'type': 'structure',
                        'message': 'Missing html tag'
                    })
                
                if not soup.find('head'):
                    html_errors.append({
                        'type': 'structure',
                        'message': 'Missing head tag'
                    })
                    
                if not soup.find('body'):
                    html_errors.append({
                        'type': 'structure',
                        'message': 'Missing body tag'
                    })
                    
            except Exception as e:
                html_errors.append({
                    'type': 'parsing',
                    'message': f'HTML parsing error: {str(e)}'
                })
            
            # Validate CSS
            try:
                # Check for basic CSS syntax
                if '{' in css and '}' not in css:
                    css_errors.append({
                        'type': 'syntax',
                        'message': 'Unmatched opening brace'
                    })
                    
                if '}' in css and '{' not in css:
                    css_errors.append({
                        'type': 'syntax',
                        'message': 'Unmatched closing brace'
                    })
                    
            except Exception as e:
                css_errors.append({
                    'type': 'parsing',
                    'message': f'CSS parsing error: {str(e)}'
                })
            
            # Validate JavaScript
            if js:
                try:
                    # Basic JS syntax checks
                    if '(' in js and ')' not in js:
                        js_errors.append({
                            'type': 'syntax',
                            'message': 'Unmatched opening parenthesis'
                        })
                        
                    if ')' in js and '(' not in js:
                        js_errors.append({
                            'type': 'syntax',
                            'message': 'Unmatched closing parenthesis'
                        })
                        
                except Exception as e:
                    js_errors.append({
                        'type': 'parsing',
                        'message': f'JavaScript parsing error: {str(e)}'
                    })
            
            # Add validation issues to main issues list
            for error in html_errors + css_errors + js_errors:
                issues.append({
                    'severity': 'high',
                    'message': error['message'],
                    'suggestion': 'Fix syntax error'
                })
            
            # Calculate overall score
            overall_score = max(0, 1 - (len(issues) * 0.2))
            
            return ValidationResult(
                overall_score=overall_score,
                issues=issues,
                suggestions=suggestions,
                html_errors=html_errors,
                css_errors=css_errors,
                js_errors=js_errors
            )
            
        except Exception as e:
            print(f"Error in code validation: {str(e)}")
            return ValidationResult(
                overall_score=0,
                issues=[{
                    'severity': 'high',
                    'message': f'Validation error: {str(e)}',
                    'suggestion': 'Please check your code syntax'
                }]
            ) 