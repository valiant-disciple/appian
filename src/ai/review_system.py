from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import os
from .analyzer import CodeAnalyzer, AnalysisResult
from .generator import CodeGenerator

@dataclass
class ReviewResult:
    """Structure for code review results"""
    improved_code: Dict[str, str]
    suggestions: List[str]
    changes_made: List[str]
    quality_score: float
    analysis: Dict[str, Any]

class AIReviewSystem:
    def __init__(self):
        """Initialize the review system"""
        self.analyzer = CodeAnalyzer()
        self.generator = CodeGenerator()
        self.client = None  # Will be set by AIChat
        
    async def review_and_improve(self, html: str, css: str, js: str, requirements: str) -> ReviewResult:
        """Two-stage AI review and improvement process"""
        try:
            # Stage 1: Initial Analysis and Improvement
            initial_analysis = self._analyze_current_code(html, css, js, requirements)
            initial_improvements = await self._generate_improvements(initial_analysis)
            
            # Stage 2: Quality Review and Refinement
            final_result = await self._review_and_refine(initial_improvements, requirements)
            
            return final_result
            
        except Exception as e:
            print(f"Error in review process: {str(e)}")
            return ReviewResult(
                improved_code={"html": html, "css": css, "js": js},
                suggestions=[],
                changes_made=[],
                quality_score=0.0,
                analysis={}
            )

    def _analyze_current_code(self, html: str, css: str, js: str, requirements: str) -> Dict[str, Any]:
        """Analyze current code and create improvement context"""
        analysis_result = self.analyzer.analyze_code(html, css, js)
        
        return {
            "current_code": {
                "html": html,
                "css": css,
                "js": js
            },
            "requirements": requirements,
            "analysis": analysis_result.to_dict(),
            "improvement_needs": self._identify_improvement_needs(analysis_result)
        }

    def _identify_improvement_needs(self, analysis_result: AnalysisResult) -> List[str]:
        """Identify areas needing improvement"""
        needs = []
        
        # Check for issues
        for issue in analysis_result.issues:
            needs.append(f"Fix {issue['category']} issue: {issue['message']}")
        
        # Check metrics
        metrics = analysis_result.metrics
        if metrics.get('accessibility_score', 1) < 0.8:
            needs.append("Improve accessibility")
        
        # Check patterns
        pattern_types = [p['type'] for p in analysis_result.patterns]
        if 'responsive' not in pattern_types:
            needs.append("Add responsive design patterns")
        
        return needs

    async def _generate_improvements(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """First AI: Generate improvements based on analysis"""
        try:
            prompt = self._create_improvement_prompt(analysis)
            response = await self._get_ai_response(prompt)
            
            # Parse and validate improvements
            improvements = json.loads(response)
            return self._validate_improvements(improvements)
            
        except Exception as e:
            print(f"Error generating improvements: {str(e)}")
            return {}

    def _create_improvement_prompt(self, analysis: Dict[str, Any]) -> str:
        """Create prompt for improvement generation"""
        return f"""
        As an expert web developer, improve this code based on the following analysis:
        
        Current Issues:
        {json.dumps(analysis['improvement_needs'], indent=2)}
        
        Requirements:
        {analysis['requirements']}
        
        Analysis Results:
        {json.dumps(analysis['analysis'], indent=2)}
        
        Please provide improvements in JSON format with:
        1. Modified code (HTML, CSS, JS)
        2. List of changes made
        3. Explanation for each change
        4. Quality metrics for the improvements
        
        Focus on:
        - Maintaining functionality
        - Improving accessibility
        - Enhancing performance
        - Following best practices
        - Modern design patterns
        """

    def _validate_improvements(self, improvements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize improvement suggestions"""
        validated = {
            "code": {},
            "changes": [],
            "explanations": [],
            "metrics": {}
        }
        
        # Validate code changes
        if "code" in improvements:
            for key in ["html", "css", "js"]:
                if key in improvements["code"]:
                    validated["code"][key] = improvements["code"][key]
        
        # Validate changes and explanations
        if "changes" in improvements:
            validated["changes"] = [str(change) for change in improvements["changes"]]
        if "explanations" in improvements:
            validated["explanations"] = [str(exp) for exp in improvements["explanations"]]
        
        # Validate metrics
        if "metrics" in improvements:
            validated["metrics"] = {
                str(k): float(v) if isinstance(v, (int, float)) else v
                for k, v in improvements["metrics"].items()
            }
        
        return validated

    async def _review_and_refine(self, improvements: Dict[str, Any], requirements: str) -> ReviewResult:
        """Second AI: Review and refine the improvements"""
        try:
            review_prompt = self._create_review_prompt(improvements, requirements)
            review_response = await self._get_ai_response(review_prompt)
            review_result = json.loads(review_response)
            
            return ReviewResult(
                improved_code=review_result.get("code", improvements.get("code", {})),
                suggestions=review_result.get("suggestions", []),
                changes_made=review_result.get("changes", improvements.get("changes", [])),
                quality_score=float(review_result.get("quality_score", 0.0)),
                analysis=review_result.get("analysis", {})
            )
            
        except Exception as e:
            print(f"Error in review and refine: {str(e)}")
            return ReviewResult(
                improved_code=improvements.get("code", {}),
                suggestions=[],
                changes_made=improvements.get("changes", []),
                quality_score=0.0,
                analysis={}
            )

    def _create_review_prompt(self, improvements: Dict[str, Any], requirements: str) -> str:
        """Create prompt for review phase"""
        return f"""
        As a senior web developer and UX expert, review these improvements:
        
        Original Requirements:
        {requirements}
        
        Proposed Improvements:
        {json.dumps(improvements, indent=2)}
        
        Please review and refine the changes, ensuring:
        1. All requirements are met
        2. Code follows best practices
        3. Design is modern and professional
        4. Accessibility standards are met
        5. Performance is optimized
        
        Return a JSON object with:
        1. Final code (HTML, CSS, JS)
        2. List of additional refinements
        3. Quality score (0-1)
        4. Suggestions for future improvements
        5. Analysis of the improvements
        """

    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from AI model"""
        try:
            if not self.client:
                raise ValueError("AI client not initialized")
                
            response = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert web developer and designer with deep knowledge of modern web development best practices."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting AI response: {str(e)}")
            raise 