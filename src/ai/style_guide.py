from typing import Dict, List, Any, Optional, Tuple
from .data_types import (
    TypographyScale,
    ColorPalette,
    SpacingScale,
    StyleConfig
)

class StyleGuide:
    """Style guide generator and manager"""
    
    def __init__(self):
        self.current_style: Optional[StyleConfig] = None

    def _generate_typography_scale(self, base_typography: Dict[str, Any]) -> TypographyScale:
        """Generate typography scale from base settings"""
        base_size = base_typography.get('base_size', 16)
        scale_ratio = base_typography.get('scale_ratio', 1.25)
        
        levels = {
            'xs': base_size * (scale_ratio ** -1),
            'sm': base_size * (scale_ratio ** -0.5),
            'base': base_size,
            'lg': base_size * scale_ratio,
            'xl': base_size * (scale_ratio ** 2),
            'xxl': base_size * (scale_ratio ** 3),
        }
        
        return TypographyScale(
            base_size=base_size,
            scale_ratio=scale_ratio,
            levels=levels,
            font_families=base_typography.get('font_families', {}),
            line_heights=base_typography.get('line_heights', {})
        )

    def _generate_color_palette(self, base_colors: Dict[str, str]) -> ColorPalette:
        """Generate color palette from base colors"""
        return ColorPalette(
            primary=base_colors.get('primary', '#000000'),
            secondary=base_colors.get('secondary', '#ffffff'),
            accent=base_colors.get('accent', '#0000ff'),
            background=base_colors.get('background', '#ffffff'),
            text=base_colors.get('text', '#000000'),
            variants={}
        )

    def _generate_spacing_scale(self, base_spacing: Dict[str, Any]) -> SpacingScale:
        """Generate spacing scale from base settings"""
        base_unit = base_spacing.get('base_unit', 4)
        scale_ratio = base_spacing.get('scale_ratio', 2)
        
        levels = {
            'xs': base_unit,
            'sm': base_unit * scale_ratio,
            'md': base_unit * (scale_ratio ** 2),
            'lg': base_unit * (scale_ratio ** 3),
            'xl': base_unit * (scale_ratio ** 4),
        }
        
        return SpacingScale(
            base_unit=base_unit,
            scale_ratio=scale_ratio,
            levels=levels
        )

    def generate_style_config(self, base_config: Dict[str, Any]) -> StyleConfig:
        """Generate complete style configuration"""
        typography = self._generate_typography_scale(base_config.get('typography', {}))
        colors = self._generate_color_palette(base_config.get('colors', {}))
        spacing = self._generate_spacing_scale(base_config.get('spacing', {}))
        
        return StyleConfig(
            typography=typography,
            colors=colors,
            spacing=spacing,
            breakpoints=base_config.get('breakpoints', {}),
            border_radius=base_config.get('border_radius', {}),
            shadows=base_config.get('shadows', {})
        ) 