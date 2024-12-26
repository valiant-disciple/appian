from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json

from ai.templates import TemplateManager
from ai.analyzer import CodeAnalyzer
from ai.llm_client import LLMClient

class CodeGenerator:
    def __init__(self):
        """Initialize the code generator"""
        self.template_manager = TemplateManager()
        self.analyzer = CodeAnalyzer()
        self.llm_client = LLMClient()

    async def generate_improvements(self,
                                 analysis: Dict[str, Any],
                                 screenshot: Any,
                                 code: Dict[str, str]) -> Dict[str, Any]:
        """Generate code improvements"""
        try:
            # Get base template if needed
            template = self.template_manager.find_matching_template(code)
            
            # Generate improvements using LLM
            improvements_json = await self.llm_client.improve_code(
                analysis,
                code
            )
            
            return json.loads(improvements_json)
            
        except Exception as e:
            print(f"Error generating improvements: {str(e)}")
            raise

    async def generate_response(self,
                             message: str,
                             analysis: Dict[str, Any],
                             code_context: Dict[str, str]) -> str:
        """Generate response to user message"""
        try:
            prompt = f"""
            As a web development expert, respond to this query:
            
            User Message: {message}
            
            Analysis Context:
            {json.dumps(analysis, indent=2)}
            
            Code Context:
            {json.dumps(code_context, indent=2)}
            
            Provide a detailed response with specific suggestions and code examples.
            """
            
            return await self.llm_client.generate_completion(prompt)
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            raise
