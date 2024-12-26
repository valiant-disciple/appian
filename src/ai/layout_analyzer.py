from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
import re
import cssutils
from .base_analyzers import BaseAnalyzer, AnalysisResult
from .utils import parse_size_value, analyze_layout_balance

@dataclass
class LayoutResult(AnalysisResult):
    """Structure for layout analysis results"""
    balance_score: float = 0.0
    spacing_consistency: float = 0.0
    grid_alignment: float = 0.0

class LayoutAnalyzer(BaseAnalyzer):
    def __init__(self):
        """Initialize the analyzer"""
        super().__init__()
        self.css_parser = cssutils.CSSParser()

    async def _analyze(self, html: str, css: str, js: Optional[str] = None) -> LayoutResult:
        """Internal analyze method for layout structure and patterns"""
        issues = []
        suggestions = []
        
        # Parse HTML and CSS
        soup = BeautifulSoup(html, 'html.parser')
        
        # Analyze layout containers
        containers = soup.find_all(['div', 'section', 'main', 'article'])
        balance_score = analyze_layout_balance(containers)
        
        # Check spacing consistency
        spacing_values = []
        margin_matches = re.findall(r'margin:\s*([^;]+);', css)
        padding_matches = re.findall(r'padding:\s*([^;]+);', css)
        
        for value in margin_matches + padding_matches:
            if parsed := parse_size_value(value):
                spacing_values.append(parsed)
        
        spacing_consistency = len(set(spacing_values)) / len(spacing_values) if spacing_values else 1
        
        # Check grid alignment
        grid_matches = re.findall(r'display:\s*grid;', css)
        flex_matches = re.findall(r'display:\s*flex;', css)
        grid_alignment = 1.0 if grid_matches or flex_matches else 0.5
        
        # Calculate overall score
        overall_score = (balance_score + spacing_consistency + grid_alignment) / 3
        
        return LayoutResult(
            overall_score=overall_score,
            issues=issues,
            suggestions=suggestions,
            balance_score=balance_score,
            spacing_consistency=spacing_consistency,
            grid_alignment=grid_alignment
        )

class LayoutMetrics:
    """Structure for layout metrics"""
    type: str
    elements: int
    nesting: int
    spacing: Dict[str, float]
    alignment: Dict[str, int]
    distribution: Dict[str, float]

@dataclass
class SpacingSystem:
    """Structure for spacing system"""
    base: float
    scale: List[float]
    units: Dict[str, int]
    consistency: float

@dataclass
class LayoutIssue:
    """Structure for layout issues"""
    type: str
    severity: str
    element: str
    description: str
    impact: float
    fix_suggestion: str

@dataclass
class LayoutAnalysis:
    """Structure for layout analysis"""
    metrics: Dict[str, LayoutMetrics]
    spacing: SpacingSystem
    issues: List[LayoutIssue]
    structure_score: float
    spacing_score: float
    consistency_score: float
    suggestions: List[Dict[str, Any]]

class LayoutAnalyzer:
    def __init__(self):
        """Initialize the layout analyzer"""
        self.css_parser = cssutils.CSSParser()
        
        self.layout_types = {
            'flex': ['display: flex', 'flex-'],
            'grid': ['display: grid', 'grid-'],
            'float': ['float:', 'clear:'],
            'position': ['position:']
        }
        
        self.spacing_properties = {
            'margin',
            'padding',
            'gap',
            'grid-gap'
        }

    async def analyze_layout(self,
                           html: str,
                           css: str) -> LayoutAnalysis:
        """Analyze layout implementation"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            stylesheet = self.css_parser.parseString(css)
            
            # Analyze layout metrics
            metrics = self._analyze_layout_metrics(soup, stylesheet)
            
            # Analyze spacing system
            spacing = self._analyze_spacing_system(stylesheet)
            
            # Check for issues
            issues = []
            
            # Structure issues
            structure_issues = self._check_structure_issues(metrics)
            issues.extend(structure_issues)
            
            # Spacing issues
            spacing_issues = self._check_spacing_issues(spacing)
            issues.extend(spacing_issues)
            
            # Calculate scores
            structure_score = self._calculate_structure_score(metrics)
            spacing_score = self._calculate_spacing_score(spacing)
            consistency_score = self._calculate_consistency_score(metrics, spacing)
            
            # Generate suggestions
            suggestions = self._generate_layout_suggestions(
                metrics,
                spacing,
                issues,
                structure_score
            )
            
            return LayoutAnalysis(
                metrics=metrics,
                spacing=spacing,
                issues=issues,
                structure_score=structure_score,
                spacing_score=spacing_score,
                consistency_score=consistency_score,
                suggestions=suggestions
            )
            
        except Exception as e:
            print(f"Error analyzing layout: {str(e)}")
            raise

    def _analyze_layout_metrics(self,
                              soup: BeautifulSoup,
                              stylesheet: Any) -> Dict[str, LayoutMetrics]:
        """Analyze layout metrics for different layout types"""
        metrics = {}
        
        try:
            # Analyze each layout type
            for layout_type, patterns in self.layout_types.items():
                elements = []
                
                # Find elements using this layout type
                for rule in stylesheet.cssRules:
                    if rule.type == rule.STYLE_RULE:
                        if any(pattern in rule.style.cssText for pattern in patterns):
                            elements.extend(soup.select(rule.selectorText))
                
                if elements:
                    # Calculate metrics for this layout type
                    metrics[layout_type] = LayoutMetrics(
                        type=layout_type,
                        elements=len(elements),
                        nesting=self._calculate_nesting(elements),
                        spacing=self._analyze_spacing(elements, stylesheet),
                        alignment=self._analyze_alignment(elements, stylesheet),
                        distribution=self._analyze_distribution(elements, stylesheet)
                    )
            
            return metrics
            
        except Exception as e:
            print(f"Error analyzing layout metrics: {str(e)}")
            return metrics

    def _analyze_spacing_system(self, stylesheet: Any) -> SpacingSystem:
        """Analyze spacing system implementation"""
        try:
            spacing_values = []
            units = {}
            
            # Extract spacing values
            for rule in stylesheet.cssRules:
                if rule.type == rule.STYLE_RULE:
                    for prop in self.spacing_properties:
                        value = rule.style.getPropertyValue(prop)
                        if value:
                            # Extract numeric values and units
                            matches = re.findall(r'(\d*\.?\d+)(\w+|%)', value)
                            for number, unit in matches:
                                spacing_values.append(float(number))
                                units[unit] = units.get(unit, 0) + 1
            
            if not spacing_values:
                return SpacingSystem(
                    base=0,
                    scale=[],
                    units={},
                    consistency=0
                )
            
            # Calculate base value and scale
            base = min(spacing_values)
            scale = sorted(set(spacing_values))
            
            # Calculate consistency
            consistency = self._calculate_spacing_consistency(spacing_values, base)
            
            return SpacingSystem(
                base=base,
                scale=scale,
                units=units,
                consistency=consistency
            )
            
        except Exception as e:
            print(f"Error analyzing spacing system: {str(e)}")
            return SpacingSystem(
                base=0,
                scale=[],
                units={},
                consistency=0
            )

    def _check_structure_issues(self,
                              metrics: Dict[str, LayoutMetrics]) -> List[LayoutIssue]:
        """Check for layout structure issues"""
        issues = []
        
        try:
            for layout_type, layout_metrics in metrics.items():
                # Check nesting depth
                if layout_metrics.nesting > 5:
                    issues.append(LayoutIssue(
                        type='structure',
                        severity='medium',
                        element=f'{layout_type} container',
                        description=f'Deep nesting in {layout_type} layout ({layout_metrics.nesting} levels)',
                        impact=0.6,
                        fix_suggestion='Reduce nesting depth to improve maintainability'
                    ))
                
                # Check mixed layout types
                if layout_type in ['flex', 'grid'] and 'float' in metrics:
                    issues.append(LayoutIssue(
                        type='structure',
                        severity='high',
                        element='document',
                        description='Mixed modern and legacy layout methods',
                        impact=0.8,
                        fix_suggestion='Stick to modern layout methods (Flexbox/Grid)'
                    ))
                
                # Check alignment consistency
                if len(layout_metrics.alignment) > 2:
                    issues.append(LayoutIssue(
                        type='structure',
                        severity='low',
                        element=f'{layout_type} container',
                        description='Inconsistent alignment methods',
                        impact=0.4,
                        fix_suggestion='Standardize alignment approach'
                    ))
            
            return issues
            
        except Exception as e:
            print(f"Error checking structure issues: {str(e)}")
            return issues

    def _check_spacing_issues(self, spacing: SpacingSystem) -> List[LayoutIssue]:
        """Check for spacing system issues"""
        issues = []
        
        try:
            # Check unit consistency
            if len(spacing.units) > 2:
                issues.append(LayoutIssue(
                    type='spacing',
                    severity='medium',
                    element='document',
                    description=f'Multiple spacing units used ({len(spacing.units)})',
                    impact=0.6,
                    fix_suggestion='Standardize spacing units'
                ))
            
            # Check scale consistency
            if spacing.consistency < 0.7:
                issues.append(LayoutIssue(
                    type='spacing',
                    severity='medium',
                    element='document',
                    description='Inconsistent spacing scale',
                    impact=0.7,
                    fix_suggestion='Implement consistent spacing scale'
                ))
            
            # Check base unit
            if spacing.base and spacing.base < 4:
                issues.append(LayoutIssue(
                    type='spacing',
                    severity='low',
                    element='document',
                    description='Very small base spacing unit',
                    impact=0.3,
                    fix_suggestion='Consider using larger base spacing unit'
                ))
            
            return issues
            
        except Exception as e:
            print(f"Error checking spacing issues: {str(e)}")
            return issues

    def _calculate_structure_score(self,
                                metrics: Dict[str, LayoutMetrics]) -> float:
        """Calculate layout structure score"""
        try:
            if not metrics:
                return 0.0
            
            scores = []
            
            for layout_metrics in metrics.values():
                # Nesting score
                nesting_score = max(0, 1 - (layout_metrics.nesting - 3) * 0.2)
                scores.append(nesting_score)
                
                # Alignment score
                alignment_score = 1.0 if len(layout_metrics.alignment) <= 2 else 0.5
                scores.append(alignment_score)
                
                # Distribution score
                distribution_values = layout_metrics.distribution.values()
                if distribution_values:
                    distribution_score = sum(distribution_values) / len(distribution_values)
                    scores.append(distribution_score)
            
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            print(f"Error calculating structure score: {str(e)}")
            return 0.0

    def _calculate_spacing_score(self, spacing: SpacingSystem) -> float:
        """Calculate spacing system score"""
        try:
            scores = []
            
            # Unit consistency
            unit_score = 1.0 if len(spacing.units) <= 2 else 0.5
            scores.append(unit_score)
            
            # Scale consistency
            scores.append(spacing.consistency)
            
            # Base unit appropriateness
            base_score = 1.0 if spacing.base >= 4 else 0.7
            scores.append(base_score)
            
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            print(f"Error calculating spacing score: {str(e)}")
            return 0.0

    def _calculate_consistency_score(self,
                                  metrics: Dict[str, LayoutMetrics],
                                  spacing: SpacingSystem) -> float:
        """Calculate overall layout consistency score"""
        try:
            scores = []
            
            # Layout method consistency
            layout_score = 1.0
            if 'float' in metrics and ('flex' in metrics or 'grid' in metrics):
                layout_score = 0.5
            scores.append(layout_score)
            
            # Spacing consistency
            scores.append(spacing.consistency)
            
            # Alignment consistency
            alignment_counts = {}
            for layout_metrics in metrics.values():
                for alignment, count in layout_metrics.alignment.items():
                    alignment_counts[alignment] = alignment_counts.get(alignment, 0) + count
            
            alignment_score = 1.0 if len(alignment_counts) <= 3 else 0.5
            scores.append(alignment_score)
            
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            print(f"Error calculating consistency score: {str(e)}")
            return 0.0

    def _calculate_nesting(self, elements: List[Any]) -> int:
        """Calculate maximum nesting depth"""
        try:
            return max(len(list(el.parents)) for el in elements) if elements else 0
            
        except Exception as e:
            print(f"Error calculating nesting: {str(e)}")
            return 0

    def _analyze_spacing(self,
                        elements: List[Any],
                        stylesheet: Any) -> Dict[str, float]:
        """Analyze spacing patterns"""
        spacing = {}
        
        try:
            for element in elements:
                # Get computed spacing values
                for prop in self.spacing_properties:
                    value = self._get_computed_style(element, prop, stylesheet)
                    if value:
                        spacing[prop] = spacing.get(prop, 0) + 1
            
            # Normalize counts
            total = sum(spacing.values()) if spacing else 1
            return {prop: count / total for prop, count in spacing.items()}
            
        except Exception as e:
            print(f"Error analyzing spacing: {str(e)}")
            return spacing

    def _analyze_alignment(self,
                         elements: List[Any],
                         stylesheet: Any) -> Dict[str, int]:
        """Analyze alignment patterns"""
        alignment = {}
        
        try:
            alignment_props = [
                'justify-content',
                'align-items',
                'text-align'
            ]
            
            for element in elements:
                for prop in alignment_props:
                    value = self._get_computed_style(element, prop, stylesheet)
                    if value:
                        alignment[value] = alignment.get(value, 0) + 1
            
            return alignment
            
        except Exception as e:
            print(f"Error analyzing alignment: {str(e)}")
            return alignment

    def _analyze_distribution(self,
                            elements: List[Any],
                            stylesheet: Any) -> Dict[str, float]:
        """Analyze content distribution patterns"""
        distribution = {}
        
        try:
            # Analyze distribution properties
            props = {
                'flex': ['flex-grow', 'flex-shrink', 'flex-basis'],
                'grid': ['grid-template-columns', 'grid-template-rows']
            }
            
            for element in elements:
                for prop_type, prop_list in props.items():
                    values = [
                        self._get_computed_style(element, prop, stylesheet)
                        for prop in prop_list
                    ]
                    if any(values):
                        distribution[prop_type] = distribution.get(prop_type, 0) + 1
            
            # Normalize counts
            total = sum(distribution.values()) if distribution else 1
            return {prop: count / total for prop, count in distribution.items()}
            
        except Exception as e:
            print(f"Error analyzing distribution: {str(e)}")
            return distribution

    def _calculate_spacing_consistency(self,
                                    values: List[float],
                                    base: float) -> float:
        """Calculate spacing scale consistency"""
        try:
            if not values or not base:
                return 0.0
            
            # Check if values are multiples of base
            consistent_count = sum(
                1 for v in values
                if abs(v / base - round(v / base)) < 0.1
            )
            
            return consistent_count / len(values)
            
        except Exception as e:
            print(f"Error calculating spacing consistency: {str(e)}")
            return 0.0

    def _get_computed_style(self,
                          element: Any,
                          property_name: str,
                          stylesheet: Any) -> Optional[str]:
        """Get computed style value"""
        try:
            # Implementation would compute actual style value
            return None  # Default for now
            
        except Exception as e:
            print(f"Error getting computed style: {str(e)}")
            return None 