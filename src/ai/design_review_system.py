from typing import Dict, List, Any, Optional
from .llm_client import LLMClient
from .analyzer import CodeAnalyzer

class DesignReviewSystem:
    """System for reviewing and suggesting design improvements"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.analyzer = CodeAnalyzer()
        
    async def generate_response(self, prompt: str, code_context: Dict[str, str]) -> str:
        """Generate a response based on the prompt and code context"""
        try:
            # First analyze the code
            analysis = await self.analyzer.analyze_code(
                code_context.get('html', ''),
                code_context.get('css', ''),
                code_context.get('js', '')
            )
            
            # Prepare analysis summary
            analysis_summary = self._prepare_analysis_summary(analysis)
            
            # Generate response using LLM
            enhanced_prompt = f"""
Based on the following code analysis:
{analysis_summary}

User question:
{prompt}

Please provide a helpful response that takes into account both the user's question and the code analysis.
""".strip()

            return await self.llm_client.generate_response(enhanced_prompt, code_context)
            
        except Exception as e:
            print(f"Error in design review: {str(e)}")
            return f"I apologize, but I encountered an error while reviewing the code: {str(e)}"
            
    def _prepare_analysis_summary(self, analysis: Dict[str, Any]) -> str:
        """Prepare a summary of the code analysis"""
        summary = []
        
        if 'overall_score' in analysis:
            summary.append(f"Overall Score: {analysis['overall_score']:.2f}")
            
        for analyzer_name, result in analysis.items():
            if analyzer_name != 'overall_score':
                summary.append(f"\n{analyzer_name.title()} Analysis:")
                if hasattr(result, 'overall_score'):
                    summary.append(f"- Score: {result.overall_score:.2f}")
                if hasattr(result, 'issues') and result.issues:
                    summary.append("- Issues:")
                    for issue in result.issues:
                        summary.append(f"  * {issue['message']}")
                        
        return "\n".join(summary)