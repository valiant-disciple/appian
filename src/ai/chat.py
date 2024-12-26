from typing import Dict, List, Any, Optional
from .llm_client import LLMClient
from .design_review_system import DesignReviewSystem
from state_manager import StateManager

class AIChat:
    """Handles chat interactions with AI"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.design_review = DesignReviewSystem()

    async def handle_message(self, message: str):
        """Handle a user message"""
        try:
            # Get current code context
            state = StateManager.get_state()
            code_context = {
                'html': state.current_html,
                'css': state.current_css,
                'js': state.current_js
            }
            
            # Add user message to chat
            StateManager.add_chat_message('user', message)
            
            # Check if it's a feature implementation request
            if self._is_feature_request(message):
                response = await self._handle_feature_request(message, code_context)
            else:
                # Generate regular response
                response = await self.design_review.generate_response(message, code_context)
            
            # Add AI response to chat
            StateManager.add_chat_message('assistant', response)
            
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            StateManager.add_chat_message('assistant', error_message)

    def _is_feature_request(self, message: str) -> bool:
        """Check if message is requesting a feature implementation"""
        keywords = ['add', 'implement', 'create', 'make', 'change', 'update']
        return any(keyword in message.lower() for keyword in keywords)

    async def _handle_feature_request(self, message: str, code_context: Dict[str, str]) -> str:
        """Handle feature implementation request"""
        prompt = f"""
User wants to: {message}

Current code:
HTML: {code_context.get('html', '')}
CSS: {code_context.get('css', '')}
JS: {code_context.get('js', '')}

Please provide:
1. Step-by-step implementation instructions
2. Code changes needed
3. Any considerations or warnings

Return as a formatted response with code blocks.
"""
        return await self.llm_client.generate_response(prompt, code_context)