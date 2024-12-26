from typing import Dict, List, Any, Optional, Tuple
import re
import colorsys
import math
from bs4 import BeautifulSoup
import cssutils

# Suppress cssutils warning logs
import logging
cssutils.log.setLevel(logging.CRITICAL)

def parse_size_value(value: str) -> Optional[float]:
    """Parse CSS size values into normalized numbers"""
    if not value:
        return None
        
    try:
        # Remove whitespace and convert to lowercase
        value = value.strip().lower()
        
        # Extract number and unit
        match = re.match(r'^([-+]?[0-9]*\.?[0-9]+)([a-z%]*)$', value)
        if not match:
            return None
            
        number, unit = match.groups()
        number = float(number)
        
        # Convert to pixels (approximate)
        if unit == 'px':
            return number
        elif unit == 'rem':
            return number * 16
        elif unit == 'em':
            return number * 16
        elif unit == '%':
            return number / 100 * 16
        elif unit == 'pt':
            return number * 1.333
        else:
            return number
            
    except Exception:
        return None

def normalize_color(color: str) -> Optional[str]:
    """Normalize color values to hex format"""
    if not color:
        return None
        
    try:
        # Remove whitespace
        color = color.strip().lower()
        
        # Handle hex colors
        if color.startswith('#'):
            if len(color) == 4:  # Convert #RGB to #RRGGBB
                return f'#{color[1]*2}{color[2]*2}{color[3]*2}'
            return color
            
        # Handle rgb/rgba
        rgb_match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)', color)
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            return f'#{r:02x}{g:02x}{b:02x}'
            
        # Handle named colors (basic set)
        color_map = {
            'black': '#000000',
            'white': '#ffffff',
            'red': '#ff0000',
            'green': '#00ff00',
            'blue': '#0000ff'
        }
        return color_map.get(color)
            
    except Exception:
        return None

def calculate_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate WCAG contrast ratio between two colors"""
    try:
        # Convert colors to RGB values
        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
        # Calculate relative luminance
        def get_luminance(rgb: Tuple[int, int, int]) -> float:
            r, g, b = [x/255 for x in rgb]
            r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055) ** 2.4
            g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055) ** 2.4
            b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
            
        # Get RGB values
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        # Calculate luminance
        l1 = get_luminance(rgb1)
        l2 = get_luminance(rgb2)
        
        # Calculate contrast ratio
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)
        
    except Exception:
        return 1.0

def analyze_layout_balance(containers: List[Any]) -> float:
    """Analyze visual balance of layout containers"""
    try:
        if not containers:
            return 1.0
            
        # Count nested elements
        element_counts = [len(container.find_all()) for container in containers]
        
        # Calculate balance score
        avg_elements = sum(element_counts) / len(element_counts)
        max_diff = max(abs(count - avg_elements) for count in element_counts)
        balance_score = 1.0 - (max_diff / avg_elements if avg_elements > 0 else 0)
        
        return max(0.0, min(1.0, balance_score))
        
    except Exception:
        return 1.0

def analyze_color_harmony(colors: List[str]) -> Tuple[str, float]:
    """Analyze color harmony and return type and score"""
    try:
        if len(colors) < 2:
            return 'monochromatic', 1.0
            
        # Convert colors to HSV
        def hex_to_hsv(hex_color: str) -> Tuple[float, float, float]:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))
            return colorsys.rgb_to_hsv(*rgb)
            
        # Get HSV values
        hsv_colors = [hex_to_hsv(color) for color in colors]
        hues = [hsv[0] for hsv in hsv_colors]
        
        # Calculate hue differences
        hue_diffs = [abs(h1 - h2) for i, h1 in enumerate(hues) 
                    for h2 in hues[i+1:]]
        
        # Determine harmony type
        avg_diff = sum(hue_diffs) / len(hue_diffs) if hue_diffs else 0
        
        if avg_diff < 0.1:
            return 'monochromatic', 1.0
        elif 0.3 < avg_diff < 0.4:
            return 'complementary', 0.8
        elif 0.15 < avg_diff < 0.25:
            return 'analogous', 0.9
        else:
            return 'custom', 0.7
            
    except Exception:
        return 'unknown', 0.5 