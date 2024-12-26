from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
from bs4 import BeautifulSoup
import cssutils
from .typography import TypographyAnalyzer
from .color_system import ColorAnalyzer
from .layout_analyzer import LayoutAnalyzer
from .interaction import InteractionAnalyzer

@dataclass
class ComponentStructure:
    """Structure for component structure"""
    type: str
    elements: List[str]
    hierarchy: Dict[str, List[str]]
    dependencies: List[str]
    variants: List[str]

@dataclass
class ComponentMetrics:
    """Structure for component metrics"""
    complexity: float
    reusability: float
    maintainability: float
    performance: float
    accessibility: float

@dataclass
class ComponentAnalysis:
    """Structure for component analysis"""
    structure: ComponentStructure
    metrics: ComponentMetrics
    typography: Dict[str, Any]
    colors: Dict[str, Any]
    layout: Dict[str, Any]
    interactions: Dict[str, Any]
    suggestions: List[Dict[str, Any]]

class ComponentAnalyzer:
    def __init__(self):
        """Initialize the component analyzer"""
        self.typography_analyzer = TypographyAnalyzer()
        self.color_analyzer = ColorAnalyzer()
        self.layout_analyzer = LayoutAnalyzer()
        self.interaction_analyzer = InteractionAnalyzer()
        self.css_parser = cssutils.CSSParser()
        
        self.complexity_thresholds = {
            'elements': 15,
            'depth': 4,
            'variants': 5
        }

    async def analyze_component(self,
                              html: str,
                              css: str,
                              js: Optional[str] = None,
                              context: Optional[Dict[str, Any]] = None) -> ComponentAnalysis:
        """Analyze component structure and metrics"""
        try:
            # Extract component structure
            structure = self._extract_component_structure(html, css, js)
            
            # Calculate base metrics
            metrics = self._calculate_component_metrics(structure, html, css, js)
            
            # Analyze typography
            typography = await self.typography_analyzer.analyze_typography(
                html, css, context.get('background_colors', {}) if context else {}
            )
            
            # Analyze colors
            colors = await self.color_analyzer.analyze_colors(
                context.get('screenshot') if context else None,
                css
            )
            
            # Analyze layout
            layout = await self.layout_analyzer.analyze_layout(
                html,
                css,
                context.get('viewport_width', 1440) if context else 1440
            )
            
            # Analyze interactions
            interactions = await self.interaction_analyzer.analyze_interactions(
                html,
                css,
                js
            )
            
            # Generate suggestions
            suggestions = self._generate_component_suggestions(
                structure,
                metrics,
                typography,
                colors,
                layout,
                interactions
            )
            
            return ComponentAnalysis(
                structure=structure,
                metrics=metrics,
                typography=typography.__dict__,
                colors=colors.__dict__,
                layout=layout.__dict__,
                interactions=interactions.__dict__,
                suggestions=suggestions
            )
            
        except Exception as e:
            print(f"Error analyzing component: {str(e)}")
            raise

    def _extract_component_structure(self,
                                  html: str,
                                  css: str,
                                  js: Optional[str] = None) -> ComponentStructure:
        """Extract component structure from code"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Determine component type
            component_type = self._determine_component_type(soup)
            
            # Extract elements
            elements = self._extract_elements(soup)
            
            # Build hierarchy
            hierarchy = self._build_element_hierarchy(soup)
            
            # Find dependencies
            dependencies = self._find_dependencies(html, css, js)
            
            # Identify variants
            variants = self._identify_variants(soup, css)
            
            return ComponentStructure(
                type=component_type,
                elements=elements,
                hierarchy=hierarchy,
                dependencies=dependencies,
                variants=variants
            )
            
        except Exception as e:
            print(f"Error extracting component structure: {str(e)}")
            raise

    def _calculate_component_metrics(self,
                                  structure: ComponentStructure,
                                  html: str,
                                  css: str,
                                  js: Optional[str] = None) -> ComponentMetrics:
        """Calculate component metrics"""
        try:
            # Calculate complexity
            complexity = self._calculate_complexity_score(structure)
            
            # Calculate reusability
            reusability = self._calculate_reusability_score(
                structure,
                html,
                css,
                js
            )
            
            # Calculate maintainability
            maintainability = self._calculate_maintainability_score(
                structure,
                html,
                css,
                js
            )
            
            # Calculate performance
            performance = self._calculate_performance_score(
                structure,
                html,
                css,
                js
            )
            
            # Calculate accessibility
            accessibility = self._calculate_accessibility_score(
                structure,
                html,
                css,
                js
            )
            
            return ComponentMetrics(
                complexity=complexity,
                reusability=reusability,
                maintainability=maintainability,
                performance=performance,
                accessibility=accessibility
            )
            
        except Exception as e:
            print(f"Error calculating component metrics: {str(e)}")
            raise

    def _generate_component_suggestions(self,
                                     structure: ComponentStructure,
                                     metrics: ComponentMetrics,
                                     typography: Any,
                                     colors: Any,
                                     layout: Any,
                                     interactions: Any) -> List[Dict[str, Any]]:
        """Generate component improvement suggestions"""
        suggestions = []
        
        try:
            # Check complexity issues
            if metrics.complexity > 0.7:
                suggestions.extend(self._generate_complexity_suggestions(structure))
            
            # Check reusability issues
            if metrics.reusability < 0.7:
                suggestions.extend(self._generate_reusability_suggestions(
                    structure,
                    metrics
                ))
            
            # Check maintainability issues
            if metrics.maintainability < 0.7:
                suggestions.extend(self._generate_maintainability_suggestions(
                    structure,
                    metrics
                ))
            
            # Incorporate analyzer suggestions
            suggestions.extend(typography.suggestions)
            suggestions.extend(colors.suggestions)
            suggestions.extend(layout.suggestions)
            suggestions.extend(interactions.suggestions)
            
            return sorted(suggestions,
                        key=lambda x: x.get('priority', 0),
                        reverse=True)
            
        except Exception as e:
            print(f"Error generating component suggestions: {str(e)}")
            return []

    # Helper methods
    def _determine_component_type(self, soup: BeautifulSoup) -> str:
        """Determine component type from structure"""
        # Implementation would include component type detection
        pass

    def _extract_elements(self, soup: BeautifulSoup) -> List[str]:
        """Extract component elements"""
        # Implementation would include element extraction
        pass

    def _build_element_hierarchy(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Build element hierarchy"""
        # Implementation would include hierarchy building
        pass

    def _find_dependencies(self,
                         html: str,
                         css: str,
                         js: Optional[str]) -> List[str]:
        """Find component dependencies"""
        # Implementation would include dependency detection
        pass

    def _identify_variants(self,
                         soup: BeautifulSoup,
                         css: str) -> List[str]:
        """Identify component variants"""
        # Implementation would include variant detection
        pass

    def _calculate_complexity_score(self, structure: ComponentStructure) -> float:
        """Calculate component complexity score"""
        try:
            scores = []
            
            # Check element count
            element_count = len(structure.elements)
            scores.append(min(1.0, element_count / self.complexity_thresholds['elements']))
            
            # Check hierarchy depth
            max_depth = self._calculate_max_depth(structure.hierarchy)
            scores.append(min(1.0, max_depth / self.complexity_thresholds['depth']))
            
            # Check variant count
            variant_count = len(structure.variants)
            scores.append(min(1.0, variant_count / self.complexity_thresholds['variants']))
            
            # Check dependency count
            dependency_score = min(1.0, len(structure.dependencies) / 5)
            scores.append(dependency_score)
            
            return sum(scores) / len(scores)
            
        except Exception as e:
            print(f"Error calculating complexity score: {str(e)}")
            return 0.0

    def _calculate_reusability_score(self,
                                   structure: ComponentStructure,
                                   html: str,
                                   css: str,
                                   js: Optional[str]) -> float:
        """Calculate component reusability score"""
        # Implementation would include reusability calculation
        pass

    def _calculate_maintainability_score(self,
                                       structure: ComponentStructure,
                                       html: str,
                                       css: str,
                                       js: Optional[str]) -> float:
        """Calculate component maintainability score"""
        # Implementation would include maintainability calculation
        pass

    def _calculate_performance_score(self,
                                   structure: ComponentStructure,
                                   html: str,
                                   css: str,
                                   js: Optional[str]) -> float:
        """Calculate component performance score"""
        # Implementation would include performance calculation
        pass

    def _calculate_accessibility_score(self,
                                    structure: ComponentStructure,
                                    html: str,
                                    css: str,
                                    js: Optional[str]) -> float:
        """Calculate component accessibility score"""
        # Implementation would include accessibility calculation
        pass

    def _calculate_max_depth(self, hierarchy: Dict[str, List[str]]) -> int:
        """Calculate maximum hierarchy depth"""
        # Implementation would include depth calculation
        pass

    def _generate_complexity_suggestions(self,
                                      structure: ComponentStructure) -> List[Dict[str, Any]]:
        """Generate complexity improvement suggestions"""
        # Implementation would include complexity suggestions
        pass

    def _generate_reusability_suggestions(self,
                                        structure: ComponentStructure,
                                        metrics: ComponentMetrics) -> List[Dict[str, Any]]:
        """Generate reusability improvement suggestions"""
        # Implementation would include reusability suggestions
        pass

    def _generate_maintainability_suggestions(self,
                                            structure: ComponentStructure,
                                            metrics: ComponentMetrics) -> List[Dict[str, Any]]:
        """Generate maintainability improvement suggestions"""
        # Implementation would include maintainability suggestions
        pass 