from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class TypographyScale:
    """Typography scale configuration"""
    base_size: float
    scale_ratio: float
    levels: Dict[str, float]
    font_families: Dict[str, str]
    line_heights: Dict[str, float]

@dataclass
class ColorPalette:
    """Color palette configuration"""
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    variants: Dict[str, List[str]]

@dataclass
class SpacingScale:
    """Spacing scale configuration"""
    base_unit: float
    scale_ratio: float
    levels: Dict[str, float]

@dataclass
class StyleConfig:
    """Complete style configuration"""
    typography: TypographyScale
    colors: ColorPalette
    spacing: SpacingScale
    breakpoints: Dict[str, int]
    border_radius: Dict[str, str]
    shadows: Dict[str, str]

@dataclass
class TemplateConfig:
    """Template configuration"""
    name: str
    description: str
    style: StyleConfig
    layout: Dict[str, Any]
    components: Dict[str, Any]

@dataclass
class ValidationResult:
    """Validation result"""
    is_valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]

@dataclass
class AnalysisMetrics:
    """Analysis metrics"""
    score: float
    issues: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    details: Dict[str, Any] 