from typing import Dict, Optional
from .llm_client import LLMClient

class CodeGenerator:
    """Generates code suggestions and improvements"""
    
    def __init__(self):
        self.llm_client = LLMClient()

    async def generate_code_suggestion(self, prompt: str, context: Optional[Dict[str, str]] = None) -> str:
        """Generate code suggestions based on user prompt"""
        enhanced_prompt = f"""
As a web development expert, please provide code suggestions for the following request:
{prompt}

Please format your response with clear code examples and explanations.
""".strip()

        return await self.llm_client.generate_response(enhanced_prompt, context)

    async def improve_code(self, code: str, language: str) -> str:
        """Suggest improvements for existing code"""
        prompt = f"""
Please analyze this {language} code and suggest improvements:

{code}

Focus on:
1. Best practices
2. Performance
3. Maintainability
4. Accessibility
""".strip()

        return await self.llm_client.generate_response(prompt, None) 