from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import base64
from pathlib import Path
import tempfile
from PIL import Image
from playwright.async_api import async_playwright
from .responsive import ResponsiveAnalyzer

@dataclass
class PreviewConfig:
    """Structure for preview configuration"""
    viewport_width: int
    viewport_height: int
    scale_factor: float
    background_color: str
    include_interactions: bool
    include_animations: bool

@dataclass
class PreviewMetrics:
    """Structure for preview metrics"""
    render_time: float
    paint_time: float
    layout_time: float
    memory_usage: float
    node_count: int

@dataclass
class PreviewResult:
    """Structure for preview results"""
    image: str  # Base64 encoded image
    metrics: PreviewMetrics
    viewport: Dict[str, int]
    timestamp: float

class PreviewGenerator:
    def __init__(self):
        """Initialize the preview generator"""
        self.responsive_analyzer = ResponsiveAnalyzer()
        self.default_config = PreviewConfig(
            viewport_width=1440,
            viewport_height=900,
            scale_factor=1.0,
            background_color='#FFFFFF',
            include_interactions=True,
            include_animations=True
        )
        
        self.viewport_sizes = {
            'mobile': {'width': 375, 'height': 667},
            'tablet': {'width': 768, 'height': 1024},
            'desktop': {'width': 1440, 'height': 900}
        }

    async def generate_preview(self,
                             html: str,
                             css: str,
                             js: Optional[str] = None,
                             config: Optional[PreviewConfig] = None) -> PreviewResult:
        """Generate preview for component"""
        try:
            # Use default config if none provided
            if not config:
                config = self.default_config
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.html', mode='w+') as html_file, \
                 tempfile.NamedTemporaryFile(suffix='.css', mode='w+') as css_file:
                
                # Write component code to files
                html_content = self._generate_preview_html(
                    html,
                    css,
                    js,
                    config
                )
                html_file.write(html_content)
                html_file.flush()
                
                css_file.write(css)
                css_file.flush()
                
                # Generate preview using Playwright
                async with async_playwright() as p:
                    browser = await p.chromium.launch()
                    page = await browser.new_page(
                        viewport={
                            'width': config.viewport_width,
                            'height': config.viewport_height
                        },
                        device_scale_factor=config.scale_factor
                    )
                    
                    # Load component
                    await page.goto(f'file://{html_file.name}')
                    
                    # Wait for rendering
                    await page.wait_for_load_state('networkidle')
                    
                    # Collect metrics
                    metrics = await self._collect_metrics(page)
                    
                    # Capture screenshot
                    screenshot = await page.screenshot(
                        type='png',
                        full_page=True
                    )
                    
                    # Convert to base64
                    image_base64 = base64.b64encode(screenshot).decode('utf-8')
                    
                    await browser.close()
                    
                    return PreviewResult(
                        image=image_base64,
                        metrics=metrics,
                        viewport={
                            'width': config.viewport_width,
                            'height': config.viewport_height
                        },
                        timestamp=metrics.render_time
                    )
            
        except Exception as e:
            print(f"Error generating preview: {str(e)}")
            raise

    async def generate_responsive_previews(self,
                                         html: str,
                                         css: str,
                                         js: Optional[str] = None) -> Dict[str, PreviewResult]:
        """Generate previews for different viewport sizes"""
        try:
            previews = {}
            
            # Generate preview for each viewport size
            for device, viewport in self.viewport_sizes.items():
                config = PreviewConfig(
                    viewport_width=viewport['width'],
                    viewport_height=viewport['height'],
                    scale_factor=1.0,
                    background_color='#FFFFFF',
                    include_interactions=True,
                    include_animations=True
                )
                
                preview = await self.generate_preview(
                    html,
                    css,
                    js,
                    config
                )
                previews[device] = preview
            
            return previews
            
        except Exception as e:
            print(f"Error generating responsive previews: {str(e)}")
            raise

    async def generate_interaction_preview(self,
                                        html: str,
                                        css: str,
                                        js: str,
                                        interaction: str) -> PreviewResult:
        """Generate preview for specific interaction state"""
        try:
            config = PreviewConfig(
                viewport_width=self.default_config.viewport_width,
                viewport_height=self.default_config.viewport_height,
                scale_factor=1.0,
                background_color='#FFFFFF',
                include_interactions=True,
                include_animations=True
            )
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.html', mode='w+') as html_file, \
                 tempfile.NamedTemporaryFile(suffix='.css', mode='w+') as css_file, \
                 tempfile.NamedTemporaryFile(suffix='.js', mode='w+') as js_file:
                
                # Write component code to files
                html_content = self._generate_preview_html(
                    html,
                    css,
                    js,
                    config
                )
                html_file.write(html_content)
                html_file.flush()
                
                css_file.write(css)
                css_file.flush()
                
                js_file.write(js)
                js_file.flush()
                
                # Generate preview using Playwright
                async with async_playwright() as p:
                    browser = await p.chromium.launch()
                    page = await browser.new_page(
                        viewport={
                            'width': config.viewport_width,
                            'height': config.viewport_height
                        },
                        device_scale_factor=config.scale_factor
                    )
                    
                    # Load component
                    await page.goto(f'file://{html_file.name}')
                    
                    # Wait for rendering
                    await page.wait_for_load_state('networkidle')
                    
                    # Trigger interaction
                    await self._trigger_interaction(page, interaction)
                    
                    # Wait for animation
                    await asyncio.sleep(0.5)
                    
                    # Collect metrics
                    metrics = await self._collect_metrics(page)
                    
                    # Capture screenshot
                    screenshot = await page.screenshot(
                        type='png',
                        full_page=True
                    )
                    
                    # Convert to base64
                    image_base64 = base64.b64encode(screenshot).decode('utf-8')
                    
                    await browser.close()
                    
                    return PreviewResult(
                        image=image_base64,
                        metrics=metrics,
                        viewport={
                            'width': config.viewport_width,
                            'height': config.viewport_height
                        },
                        timestamp=metrics.render_time
                    )
            
        except Exception as e:
            print(f"Error generating interaction preview: {str(e)}")
            raise

    # Helper methods
    def _generate_preview_html(self,
                             html: str,
                             css: str,
                             js: Optional[str],
                             config: PreviewConfig) -> str:
        """Generate HTML for preview"""
        try:
            return f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {{
                            margin: 0;
                            padding: 20px;
                            background-color: {config.background_color};
                        }}
                        {css}
                    </style>
                    {f'<script>{js}</script>' if js else ''}
                </head>
                <body>
                    {html}
                </body>
                </html>
            """
        except Exception as e:
            print(f"Error generating preview HTML: {str(e)}")
            raise

    async def _collect_metrics(self, page: Any) -> PreviewMetrics:
        """Collect rendering metrics"""
        try:
            # Get performance metrics
            perf_metrics = await page.evaluate("""() => {
                const timing = window.performance.timing;
                const paint = window.performance.getEntriesByType('paint');
                return {
                    renderTime: timing.loadEventEnd - timing.navigationStart,
                    paintTime: paint.find(p => p.name === 'first-paint')?.duration || 0,
                    layoutTime: paint.find(p => p.name === 'first-contentful-paint')?.duration || 0
                };
            }""")
            
            # Get memory usage
            memory = await page.evaluate("() => performance.memory.usedJSHeapSize")
            
            # Get DOM node count
            node_count = await page.evaluate("() => document.getElementsByTagName('*').length")
            
            return PreviewMetrics(
                render_time=perf_metrics['renderTime'],
                paint_time=perf_metrics['paintTime'],
                layout_time=perf_metrics['layoutTime'],
                memory_usage=memory,
                node_count=node_count
            )
            
        except Exception as e:
            print(f"Error collecting metrics: {str(e)}")
            raise

    async def _trigger_interaction(self, page: Any, interaction: str):
        """Trigger interaction state"""
        try:
            if interaction == 'hover':
                await page.hover('.component')
            elif interaction == 'focus':
                await page.focus('.component')
            elif interaction == 'active':
                await page.click('.component', delay=100)
            # Add more interaction handlers as needed
            
        except Exception as e:
            print(f"Error triggering interaction: {str(e)}")
            raise

    def _optimize_image(self, image_data: bytes) -> bytes:
        """Optimize preview image"""
        try:
            # Open image
            image = Image.open(image_data)
            
            # Optimize
            optimized = image.copy()
            optimized.thumbnail((1200, 1200))  # Max dimensions
            
            # Save optimized image
            with tempfile.BytesIO() as output:
                optimized.save(
                    output,
                    format='PNG',
                    optimize=True,
                    quality=85
                )
                return output.getvalue()
                
        except Exception as e:
            print(f"Error optimizing image: {str(e)}")
            return image_data 