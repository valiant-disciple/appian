from typing import Dict, Optional
from .llm_client import LLMClient

class TestingAdvisor:
    """Generates testing suggestions using LLM"""
    
    def __init__(self):
        self.llm_client = LLMClient()

    async def generate_test_cases(self, code: Dict[str, str]) -> str:
        """Generate test cases for the code"""
        prompt = f"""
Please generate comprehensive test cases for this code:

HTML:
{code.get('html', '')}

CSS:
{code.get('css', '')}

JavaScript:
{code.get('js', '')}

Include:
1. Unit tests
2. Integration tests
3. UI tests
4. Edge cases
5. Performance tests
""".strip()

        return await self.llm_client.generate_response(prompt, code)

    async def suggest_testing_strategy(self, code: Dict[str, str]) -> str:
        """Suggest testing strategy"""
        prompt = f"""
Please suggest a testing strategy for this code:

HTML:
{code.get('html', '')}

CSS:
{code.get('css', '')}

JavaScript:
{code.get('js', '')}

Include:
1. Testing frameworks
2. Test coverage goals
3. Testing priorities
4. CI/CD integration
5. Testing best practices
""".strip()

        return await self.llm_client.generate_response(prompt, code) 