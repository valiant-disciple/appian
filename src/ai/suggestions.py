from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
from bs4 import BeautifulSoup
import cssutils

@dataclass
class SuggestionImpact:
    """Structure for suggestion impact"""
    performance: float
    accessibility: float
    maintainability: float
    user_experience: float
    overall: float

@dataclass
class CodeSuggestion:
    """Structure for code suggestions"""
    type: str
    severity: str
    description: str
    rationale: str
    impact: SuggestionImpact
    before_code: Optional[str]
    after_code: Optional[str]
    implementation_notes: List[str]
    references: List[str]

@dataclass
class SuggestionGroup:
    """Structure for suggestion groups"""
    category: str
    priority: float
    suggestions: List[CodeSuggestion]
    combined_impact: SuggestionImpact

class SuggestionGenerator:
    def __init__(self):
        """Initialize the suggestion generator"""
        self.css_parser = cssutils.CSSParser()
        
        self.suggestion_categories = [
            'performance',
            'accessibility',
            'responsive',
            'maintainability',
            'best_practices',
            'user_experience'
        ]
        
        self.severity_weights = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.5,
            'low': 0.3,
            'info': 0.1
        }

    async def generate_suggestions(self,
                                 analysis_results: Dict[str, Any],
                                 context: Optional[Dict[str, Any]] = None) -> List[SuggestionGroup]:
        """Generate and prioritize suggestions"""
        try:
            # Initialize suggestion groups
            groups = {
                category: []
                for category in self.suggestion_categories
            }
            
            # Process performance suggestions
            if 'performance' in analysis_results:
                performance_suggestions = self._generate_performance_suggestions(
                    analysis_results['performance']
                )
                groups['performance'].extend(performance_suggestions)
            
            # Process accessibility suggestions
            if 'accessibility' in analysis_results:
                accessibility_suggestions = self._generate_accessibility_suggestions(
                    analysis_results['accessibility']
                )
                groups['accessibility'].extend(accessibility_suggestions)
            
            # Process responsive suggestions
            if 'responsive' in analysis_results:
                responsive_suggestions = self._generate_responsive_suggestions(
                    analysis_results['responsive']
                )
                groups['responsive'].extend(responsive_suggestions)
            
            # Process maintainability suggestions
            if 'components' in analysis_results:
                maintainability_suggestions = self._generate_maintainability_suggestions(
                    analysis_results['components']
                )
                groups['maintainability'].extend(maintainability_suggestions)
            
            # Process best practices suggestions
            best_practice_suggestions = self._generate_best_practice_suggestions(
                analysis_results
            )
            groups['best_practices'].extend(best_practice_suggestions)
            
            # Process user experience suggestions
            if 'interactions' in analysis_results:
                ux_suggestions = self._generate_ux_suggestions(
                    analysis_results['interactions']
                )
                groups['user_experience'].extend(ux_suggestions)
            
            # Create suggestion groups with priorities
            prioritized_groups = []
            for category, suggestions in groups.items():
                if suggestions:
                    # Calculate combined impact
                    combined_impact = self._calculate_combined_impact(suggestions)
                    
                    # Calculate priority
                    priority = self._calculate_group_priority(
                        category,
                        suggestions,
                        combined_impact
                    )
                    
                    prioritized_groups.append(SuggestionGroup(
                        category=category,
                        priority=priority,
                        suggestions=suggestions,
                        combined_impact=combined_impact
                    ))
            
            # Sort groups by priority
            return sorted(
                prioritized_groups,
                key=lambda x: x.priority,
                reverse=True
            )
            
        except Exception as e:
            print(f"Error generating suggestions: {str(e)}")
            raise

    def _generate_performance_suggestions(self,
                                       performance_results: Dict[str, Any]) -> List[CodeSuggestion]:
        """Generate performance-related suggestions"""
        suggestions = []
        
        try:
            # Check resource size issues
            if 'resources' in performance_results:
                for resource_type, metrics in performance_results['resources'].items():
                    if metrics.size > metrics.threshold:
                        suggestions.append(CodeSuggestion(
                            type='resource_size',
                            severity='high',
                            description=f'Optimize {resource_type} size',
                            rationale='Large resources impact load time and performance',
                            impact=SuggestionImpact(
                                performance=0.8,
                                accessibility=0.2,
                                maintainability=0.1,
                                user_experience=0.6,
                                overall=0.7
                            ),
                            before_code=None,
                            after_code=None,
                            implementation_notes=[
                                f'Current size: {metrics.size}',
                                f'Recommended: < {metrics.threshold}',
                                'Consider minification and compression'
                            ],
                            references=[
                                'https://web.dev/optimize-resource-size/',
                                'https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency'
                            ]
                        ))
            
            # Check rendering issues
            if 'rendering' in performance_results:
                render_metrics = performance_results['rendering']
                if render_metrics.reflows > render_metrics.threshold:
                    suggestions.append(CodeSuggestion(
                        type='layout_thrashing',
                        severity='high',
                        description='Reduce layout thrashing',
                        rationale='Excessive layout recalculations impact performance',
                        impact=SuggestionImpact(
                            performance=0.9,
                            accessibility=0.1,
                            maintainability=0.3,
                            user_experience=0.7,
                            overall=0.8
                        ),
                        before_code=None,
                        after_code=None,
                        implementation_notes=[
                            'Batch DOM operations',
                            'Use requestAnimationFrame',
                            'Minimize forced synchronous layouts'
                        ],
                        references=[
                            'https://web.dev/avoid-large-complex-layouts-and-layout-thrashing/',
                            'https://developers.google.com/web/fundamentals/performance/rendering'
                        ]
                    ))
            
            return suggestions
            
        except Exception as e:
            print(f"Error generating performance suggestions: {str(e)}")
            return suggestions

    def _generate_accessibility_suggestions(self,
                                         accessibility_results: Dict[str, Any]) -> List[CodeSuggestion]:
        """Generate accessibility-related suggestions"""
        # Implementation would include accessibility suggestion generation
        pass

    def _generate_responsive_suggestions(self,
                                      responsive_results: Dict[str, Any]) -> List[CodeSuggestion]:
        """Generate responsive-related suggestions"""
        # Implementation would include responsive suggestion generation
        pass

    def _generate_maintainability_suggestions(self,
                                           component_results: Dict[str, Any]) -> List[CodeSuggestion]:
        """Generate maintainability-related suggestions"""
        # Implementation would include maintainability suggestion generation
        pass

    def _generate_best_practice_suggestions(self,
                                          analysis_results: Dict[str, Any]) -> List[CodeSuggestion]:
        """Generate best practice suggestions"""
        # Implementation would include best practice suggestion generation
        pass

    def _generate_ux_suggestions(self,
                               interaction_results: Dict[str, Any]) -> List[CodeSuggestion]:
        """Generate user experience suggestions"""
        # Implementation would include UX suggestion generation
        pass

    def _calculate_combined_impact(self,
                                 suggestions: List[CodeSuggestion]) -> SuggestionImpact:
        """Calculate combined impact of suggestions"""
        try:
            if not suggestions:
                return SuggestionImpact(
                    performance=0.0,
                    accessibility=0.0,
                    maintainability=0.0,
                    user_experience=0.0,
                    overall=0.0
                )
            
            # Calculate average impacts
            performance = sum(s.impact.performance for s in suggestions) / len(suggestions)
            accessibility = sum(s.impact.accessibility for s in suggestions) / len(suggestions)
            maintainability = sum(s.impact.maintainability for s in suggestions) / len(suggestions)
            user_experience = sum(s.impact.user_experience for s in suggestions) / len(suggestions)
            
            # Calculate overall impact
            overall = (performance + accessibility + maintainability + user_experience) / 4
            
            return SuggestionImpact(
                performance=performance,
                accessibility=accessibility,
                maintainability=maintainability,
                user_experience=user_experience,
                overall=overall
            )
            
        except Exception as e:
            print(f"Error calculating combined impact: {str(e)}")
            return SuggestionImpact(
                performance=0.0,
                accessibility=0.0,
                maintainability=0.0,
                user_experience=0.0,
                overall=0.0
            )

    def _calculate_group_priority(self,
                                category: str,
                                suggestions: List[CodeSuggestion],
                                impact: SuggestionImpact) -> float:
        """Calculate priority for suggestion group"""
        try:
            # Base priority on category
            base_priority = {
                'performance': 0.9,
                'accessibility': 0.8,
                'responsive': 0.7,
                'maintainability': 0.6,
                'best_practices': 0.5,
                'user_experience': 0.7
            }.get(category, 0.5)
            
            # Factor in severity
            severity_factor = sum(
                self.severity_weights[s.severity]
                for s in suggestions
            ) / len(suggestions)
            
            # Factor in impact
            impact_factor = impact.overall
            
            # Calculate final priority
            return (base_priority + severity_factor + impact_factor) / 3
            
        except Exception as e:
            print(f"Error calculating group priority: {str(e)}")
            return 0.0