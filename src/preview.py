import streamlit as st
from typing import Optional, Dict
import html
from dataclasses import dataclass
import re

@dataclass
class PreviewConfig:
    """Preview configuration settings"""
    device_widths: Dict[str, int] = None
    auto_refresh: bool = True
    show_grid: bool = False
    show_breakpoints: bool = False
    theme: str = "light"
    
    def __post_init__(self):
        if self.device_widths is None:
            self.device_widths = {
                "desktop": 1200,
                "tablet": 768,
                "mobile": 375
            }

class PreviewSystem:
    """Handle live preview rendering"""

    def __init__(self):
        self.config = PreviewConfig()
        self._initialize_preview_state()

    def _initialize_preview_state(self):
        """Initialize preview-related session state"""
        if 'preview_config' not in st.session_state:
            st.session_state.preview_config = self.config

    def render_preview(self, html_code: str, css_code: str, js_code: str, 
                      device: str = "desktop", height: Optional[int] = None):
        """Render live preview of the code"""
        try:
            # Sanitize and prepare code
            html_code = self._sanitize_html(html_code)
            css_code = self._sanitize_css(css_code)
            js_code = self._sanitize_js(js_code)

            # Generate preview HTML
            preview_html = self._generate_preview_html(html_code, css_code, js_code, device)

            # Calculate preview height
            if not height:
                height = self._calculate_preview_height(html_code)

            # Render preview frame
            self._render_preview_frame(preview_html, device, height)

            # Show debug info if enabled
            if st.session_state.preview_config.show_breakpoints:
                self._show_debug_info(device)

        except Exception as e:
            st.error(f"Preview error: {str(e)}")

    def _sanitize_html(self, html_code: str) -> str:
        """Sanitize HTML code"""
        # Remove potentially harmful tags and attributes
        html_code = re.sub(r'<script.*?</script>', '', html_code, flags=re.DOTALL)
        html_code = re.sub(r'<link.*?>', '', html_code)
        html_code = re.sub(r'<meta.*?>', '', html_code)
        html_code = re.sub(r'<iframe.*?</iframe>', '', html_code, flags=re.DOTALL)
        
        return html_code

    def _sanitize_css(self, css_code: str) -> str:
        """Sanitize CSS code"""
        # Remove potentially harmful CSS
        css_code = re.sub(r'@import.*?;', '', css_code)
        css_code = re.sub(r'position:\s*fixed', 'position: relative', css_code)
        
        return css_code

    def _sanitize_js(self, js_code: str) -> str:
        """Sanitize JavaScript code"""
        # Remove potentially harmful JS
        js_code = re.sub(r'document\.cookie', 'null', js_code)
        js_code = re.sub(r'localStorage', 'null', js_code)
        js_code = re.sub(r'sessionStorage', 'null', js_code)
        js_code = re.sub(r'window\.location', 'null', js_code)
        
        return js_code

    def _generate_preview_html(self, html_code: str, css_code: str, js_code: str, device: str) -> str:
        """Generate complete HTML for preview"""
        device_width = self.config.device_widths[device]
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* Reset styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        /* Preview container */
        body {{
            width: {device_width}px;
            margin: 0 auto;
            font-family: system-ui, -apple-system, sans-serif;
        }}
        
        /* Grid overlay */
        {self._generate_grid_css() if st.session_state.preview_config.show_grid else ''}
        
        /* User CSS */
        {css_code}
    </style>
</head>
<body>
    {html_code}
    
    <script>
        // Sandbox setup
        const console = {{
            log: function(...args) {{
                window.parent.postMessage({{type: 'console', method: 'log', args}}, '*');
            }},
            error: function(...args) {{
                window.parent.postMessage({{type: 'console', method: 'error', args}}, '*');
            }}
        }};
        
        // User JavaScript
        try {{
            {js_code}
        }} catch (error) {{
            console.error('Preview JavaScript Error:', error);
        }}
    </script>
</body>
</html>
"""

    def _generate_grid_css(self) -> str:
        """Generate CSS for grid overlay"""
        return """
        body::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                linear-gradient(to right, rgba(255,0,0,0.1) 1px, transparent 1px) 0 0 / 100px 100%,
                linear-gradient(to bottom, rgba(255,0,0,0.1) 1px, transparent 1px) 0 0 / 100% 100px;
            pointer-events: none;
            z-index: 9999;
        }
        """

    def _calculate_preview_height(self, html_code: str) -> int:
        """Calculate appropriate preview height"""
        base_height = 400
        content_lines = len(html_code.split('\n'))
        return max(base_height, content_lines * 20)

    def _render_preview_frame(self, preview_html: str, device: str, height: int):
        """Render the preview iframe"""
        width = self.config.device_widths[device]
        
        # Create container with device frame
        with st.container():
            if device != "desktop":
                st.markdown(
                    f"""
                    <div style="
                        max-width: {width + 40}px;
                        margin: 0 auto;
                        padding: 20px;
                        background: #f0f0f0;
                        border-radius: 20px;
                        box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    ">
                    """,
                    unsafe_allow_html=True
                )

            # Render preview iframe
            st.components.v1.html(
                preview_html,
                height=height,
                width=width,
                scrolling=True
            )

            if device != "desktop":
                st.markdown("</div>", unsafe_allow_html=True)

    def _show_debug_info(self, device: str):
        """Show debug information"""
        st.markdown("### Debug Info")
        st.write({
            "Device": device,
            "Width": self.config.device_widths[device],
            "Grid": st.session_state.preview_config.show_grid,
            "Theme": st.session_state.preview_config.theme
        })

    def toggle_grid(self):
        """Toggle grid overlay"""
        st.session_state.preview_config.show_grid = not st.session_state.preview_config.show_grid

    def toggle_breakpoints(self):
        """Toggle breakpoint display"""
        st.session_state.preview_config.show_breakpoints = not st.session_state.preview_config.show_breakpoints

    def set_theme(self, theme: str):
        """Set preview theme"""
        st.session_state.preview_config.theme = theme

    def set_device_width(self, device: str, width: int):
        """Set custom device width"""
        self.config.device_widths[device] = width