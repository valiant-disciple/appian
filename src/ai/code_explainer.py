from typing import Dict, Optional
from .llm_client import LLMClient

class CodeExplainer:
    """Explains code and concepts using LLM"""
    
    def __init__(self):
        self.llm_client = LLMClient()

    async def explain_code(self, code: str, language: str) -> str:
        """Generate detailed explanation of code"""
        prompt = f"""
Please explain this {language} code in detail:

{code}

Include:
1. Overall purpose
2. How it works
3. Key components
4. Best practices used
5. Potential improvements
""".strip()

        return await self.llm_client.generate_response(prompt, None)

    async def explain_concept(self, concept: str, level: str = "intermediate") -> str:
        """Explain a web development concept"""
        prompt = f"""
Please explain the web development concept of '{concept}' at a {level} level.

Include:
1. Definition
2. Use cases
3. Examples
4. Best practices
5. Common pitfalls
""".strip()

        return await self.llm_client.generate_response(prompt, None)

    async def generate_documentation(self, code: str, language: str) -> str:
        """Generate documentation for code"""
        prompt = f"""
Please generate comprehensive documentation for this {language} code:

{code}

Include:
1. Overview
2. Parameters/Props
3. Return values/Output
4. Usage examples
5. Dependencies
6. Edge cases
""".strip()

        return await self.llm_client.generate_response(prompt, None) 