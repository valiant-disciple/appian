from typing import Dict, Optional, List
import streamlit as st
from groq import Groq
import re
from dataclasses import dataclass
from .state import ErrorHandler

@dataclass
class CodeSuggestion:
    """Structure for code improvement suggestions"""
    suggestion: str
    category: str
    priority: int

@dataclass
class AIResponse:
    """Structure for AI responses"""
    html: str = ""
    css: str = ""
    js: str = ""
    explanation: str = ""

class AIIntegration:
    """Handle AI code generation and assistance"""
    
    def __init__(self, groq_client: Optional[Groq] = None):
        """Initialize AI integration"""
        self.groq_client = groq_client
        if 'ai_context' not in st.session_state:
            st.session_state.ai_context = []
        self.max_context_length = 5

    async def generate_code(self, prompt: str) -> Optional[AIResponse]:
        """Generate code using Groq"""
        if not self.groq_client:
            ErrorHandler.handle_error(Exception("Groq client not initialized"))
            return None

        try:
            # Update context window
            self._update_context(prompt)

            system_prompt = (
                "You are an expert web developer. Generate clean, modern, and responsive code. "
                "Follow these guidelines:\n"
                "1. Use semantic HTML5 elements\n"
                "2. Write modern CSS (flexbox, grid, custom properties)\n"
                "3. Use ES6+ JavaScript\n"
                "4. Ensure accessibility\n"
                "5. Follow best practices for performance\n"
                "6. Include helpful comments\n"
                "Provide code in separate HTML, CSS, and JavaScript blocks."
            )

            # Generate response
            response = await self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.ai_context]
                ],
                temperature=0.7,
                max_tokens=2048
            )

            if response.choices:
                content = response.choices[0].message.content
                self._update_context(content, role="assistant")
                return self._parse_response(content)
            
            return None

        except Exception as e:
            ErrorHandler.handle_error(e, "AI code generation")
            return None

    def _update_context(self, content: str, role: str = "user") -> None:
        """Update conversation context"""
        st.session_state.ai_context.append({"role": role, "content": content})
        if len(st.session_state.ai_context) > self.max_context_length:
            st.session_state.ai_context.pop(0)

    def _parse_response(self, content: str) -> AIResponse:
        """Parse code blocks from AI response"""
        html = self._extract_code_block(content, "html")
        css = self._extract_code_block(content, "css")
        js = self._extract_code_block(content, "javascript")
        explanation = self._extract_explanation(content)

        return AIResponse(html, css, js, explanation)

    def _extract_code_block(self, content: str, language: str) -> str:
        """Extract code block for specific language"""
        pattern = rf"```{language}\n(.*?)\n```"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_explanation(self, content: str) -> str:
        """Extract explanation from AI response"""
        # Remove code blocks
        clean_content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        return clean_content.strip()

    def get_suggestions(self, code: str, code_type: str) -> List[CodeSuggestion]:
        """Get improvement suggestions for code"""
        if not self.groq_client:
            return []

        try:
            prompt = (
                f"Analyze this {code_type} code and provide improvement suggestions:\n\n"
                f"```{code_type}\n{code}\n```"
            )

            response = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a code reviewer. Provide clear, concise suggestions for improvement."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1024
            )

            if response.choices:
                suggestions = response.choices[0].message.content.split("\n")
                return [
                    CodeSuggestion(
                        suggestion=s.strip("- "),
                        category="general",
                        priority=1
                    ) 
                    for s in suggestions if s.strip()
                ]
            return []

        except Exception as e:
            ErrorHandler.handle_error(e, "getting code suggestions")
            return []