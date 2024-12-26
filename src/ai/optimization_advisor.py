from typing import Dict, List, Optional
from .llm_client import LLMClient

class OptimizationAdvisor:
    """Provides optimization suggestions using LLM"""
    
    def __init__(self):
        self.llm_client = LLMClient()

    async def suggest_performance_improvements(self, code: Dict[str, str]) -> str:
        """Suggest performance improvements"""
        prompt = f"""
Analyze this code for performance improvements:

HTML:
{code.get('html', '')}

CSS:
{code.get('css', '')}

JavaScript:
{code.get('js', '')}

Focus on:
1. Loading speed
2. Resource optimization
3. Rendering performance
4. Code efficiency
5. Caching strategies
""".strip()

        return await self.llm_client.generate_response(prompt, code)

    async def suggest_seo_improvements(self, html: str) -> str:
        """Suggest SEO improvements"""
        prompt = f"""
Analyze this HTML for SEO improvements:

{html}

Focus on:
1. Meta tags
2. Semantic structure
3. Content hierarchy
4. Image optimization
5. Schema markup
""".strip()

        return await self.llm_client.generate_response(prompt, {'html': html})

    async def suggest_accessibility_improvements(self, code: Dict[str, str]) -> str:
        """Suggest accessibility improvements"""
        prompt = f"""
Analyze this code for accessibility improvements:

HTML:
{code.get('html', '')}

CSS:
{code.get('css', '')}

JavaScript:
{code.get('js', '')}

Focus on:
1. ARIA labels
2. Semantic HTML
3. Color contrast
4. Keyboard navigation
5. Screen reader compatibility
""".strip()

        return await self.llm_client.generate_response(prompt, code) 