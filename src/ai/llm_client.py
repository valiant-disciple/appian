import sys
import os
from groq import Groq
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import json
import time

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.models.suggestion import Suggestion, CodeChange, Preview

class LLMClient:
    def __init__(self):
        self.client = Groq(api_key="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")
        self.max_retries = 3
        self.retry_delay = 5

    def analyze_code(self, html: str, analysis_type: str = "ux", custom_prompt: str = None) -> Optional[Suggestion]:
        """Updated to handle chat requests better"""
        for attempt in range(self.max_retries):
            try:
                # Use chat-specific prompt if it's a custom request
                if custom_prompt:
                    prompt = self._format_chat_prompt(html, custom_prompt)
                else:
                    prompt = self._format_prompt(html, analysis_type)
                
                # Rest of the method remains exactly the same
                if attempt > 0:
                    sleep_time = self.retry_delay * (2 ** (attempt - 1))
                    print(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                
                try:
                    response = self.client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are a web development expert. Provide responses in valid JSON format only."},
                            {"role": "user", "content": prompt}
                        ],
                        model="llama-3.3-70b-versatile",
                        timeout=60
                    )
                except Exception as api_error:
                    print(f"API Error on attempt {attempt + 1}: {str(api_error)}")
                    if attempt == self.max_retries - 1:
                        raise ConnectionError(f"Failed to connect to Groq API after {self.max_retries} attempts: {str(api_error)}")
                    continue

                if not hasattr(response.choices[0].message, 'content'):
                    print(f"Attempt {attempt + 1}: No content in response")
                    continue

                content = response.choices[0].message.content
                suggestion = self._parse_response(content)
                if suggestion:
                    return suggestion
                
                print(f"Attempt {attempt + 1}: Failed to parse response")

            except Exception as e:
                print(f"Attempt {attempt + 1}: Error: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise ConnectionError(f"Failed after {self.max_retries} attempts: {str(e)}")

        return None

    def _parse_response(self, content: str) -> Optional[Suggestion]:
        try:
            # Clean up the content
            content = content.strip()
            
            # Remove markdown code block markers if present
            if content.startswith('```'):
                # Find the first and last occurrence of ```
                first = content.find('```')
                last = content.rfind('```')
                # Extract content between the markers
                if first != last:
                    # If there's a language identifier (e.g., ```json), skip the first line
                    first_newline = content.find('\n')
                    if first_newline != -1 and first_newline < last:
                        content = content[first_newline:last].strip()
                    else:
                        content = content[first + 3:last].strip()
            
            # Remove any remaining markdown formatting
            content = content.replace('```json', '').replace('```', '').strip()
            
            # Parse the JSON
            data = json.loads(content)
            
            if not isinstance(data, dict):
                raise ValueError("Response is not a dictionary")
            if "changes" not in data or "preview" not in data:
                raise ValueError("Missing required fields")
            
            return Suggestion.from_dict(data)
            
        except Exception as e:
            print(f"Error parsing response: {e}")
            print(f"Raw content: {content}")
            return None

    def _format_prompt(self, html: str, analysis_type: str) -> str:
        base_prompt = """
        You are an expert web performance analyst and developer. Analyze the provided HTML code and suggest multiple improvements.
        Focus on enhancing performance, SEO, accessibility, and overall user experience.
        
        Your response must be valid JSON in this exact format:
        {
            "changes": {
                "change1": {
                    "old": "exact HTML snippet that needs to be replaced",
                    "new": "improved HTML snippet",
                    "status": "brief description of improvement"
                }
                // ... more changes ...
            },
            "preview": {
                "html": "complete improved HTML with ALL changes applied"
            }
        }

        RULES:
        1. The 'old' field must contain the EXACT HTML snippet that exists in the code
        2. Each change should be independent and self-contained
        3. Provide at least 4-5 meaningful performance improvements
        4. Use inline styles for all styling (no external CSS)
        5. Make bold, impactful changes that enhance performance
        """

        type_specific_prompts = {
            "performance": """
            Analyze the HTML for the following performance enhancements:

            1. **Code Structure Analyzer**:
               - Suggest semantic HTML improvements and better organization.
               - Ensure proper nesting of elements for clarity.

            2. **Performance Optimizer**:
               - Minify and compress HTML, CSS, and JavaScript for faster loading.
               - Remove dead code (unused CSS and JavaScript).

            3. **Best Practices Enforcer**:
               - Implement current web development standards for performance.
               - Ensure that best practices are followed throughout the code.

            4. **Security Enhancement**:
               - Identify and fix common security issues (e.g., XSS vulnerabilities).
               - Suggest best practices for secure coding.

            5. **Cross-browser Compatibility**:
               - Ensure the code works across all major browsers (Chrome, Firefox, Safari, Edge).
               - Suggest polyfills or fallbacks for unsupported features.

            6. **Code Documentation**:
               - Generate clear documentation for maintainability.
               - Suggest inline comments for complex logic.

            7. **Asset Optimization**:
               - Compress images and implement lazy loading for better performance.
               - Suggest using modern image formats (e.g., WebP).

            8. **Cache Strategy Builder**:
               - Implement efficient caching strategies for better performance.
               - Suggest using service workers for caching.

            9. **SEO Analyzer**:
               - Optimize meta tags and content structure for better search visibility.
               - Suggest improvements for heading hierarchy and content flow.

            10. **Analytics Dashboard**:
                - Provide recommendations for integrating real-time performance insights.
                - Suggest tools for tracking site speed metrics.

            11. **Load Time Optimizer**:
                - Identify and fix performance bottlenecks in the code.
                - Suggest techniques for reducing load times.

            12. **Schema Generator**:
                - Create structured data for better search visibility.
                - Suggest implementing JSON-LD for schema markup.

            13. **Link Checker**:
                - Find and fix broken links automatically.
                - Suggest best practices for maintaining link integrity.

            14. **Mobile Responsiveness Tester**:
                - Test site across different devices for responsiveness.
                - Suggest improvements for mobile usability.

            15. **Accessibility Scanner**:
                - Check and fix accessibility issues (e.g., ARIA roles, alt text).
                - Suggest improvements for screen reader compatibility.

            16. **Image Optimization**:
                - Compress and convert images to modern formats for faster loading.
                - Suggest using responsive images (srcset) for better performance.

            17. **Performance Monitoring**:
                - Track and report site speed metrics.
                - Suggest tools for ongoing performance monitoring.

            IMPORTANT:
            - Provide actionable suggestions for each of the above areas.
            - Ensure that all changes are practical and can be implemented easily.
            - Focus on improving the overall performance and user experience of the site.
            """,
            "ux": """
            Transform this into a modern, professional website by implementing these design patterns:

            1. STRUCTURAL HIERARCHY (Correct Element Placement):
               - Navigation MUST be the first element in <body>
               - Header/hero section should follow navigation
               - Main content should be properly sectioned
               - Footer MUST be the last element
               - Ensure proper nesting of elements

            2. LAYOUT ORGANIZATION:
               - Analyze and fix any misplaced elements
               - Group related content in sections
               - Maintain consistent spacing between sections
               - Ensure logical content flow
               - Fix any orphaned or misplaced elements

            3. MODERN COMPONENTS (With Proper Placement):
               - Sticky navigation at the top
               - Hero section below navigation
               - Feature sections in the middle
               - Testimonials after features
               - Contact/CTA sections before footer
               - Footer at the bottom

            4. VISUAL STYLING:
               - Choose a color palette from the following options:
                 - Palette 1: #2D3436 (dark), #636E72 (gray), #00B894 (accent), #DFE6E9 (light)
                 - Palette 2: #1B2A6D (navy), #F1C40F (yellow), #E74C3C (red), #ECF0F1 (light gray)
                 - Palette 3: #34495E (dark blue), #2ECC71 (green), #E67E22 (orange), #F39C12 (gold)
                 - Palette 4: #8E44AD (purple), #2980B9 (blue), #D35400 (orange), #F4D03F (yellow)
               - Font stack options:
                 - Stack 1: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen
                 - Stack 2: 'Helvetica Neue', Arial, sans-serif
                 - Stack 3: 'Georgia', 'Times New Roman', serif
                 - Stack 4: 'Courier New', Courier, monospace
               - Consistent spacing: padding: 1.5rem for sections
               - Box shadows: 0 4px 6px rgba(0, 0, 0, 0.1)
               - Border radius: 8px for cards

            ELEMENT PLACEMENT RULES:
            1. Always check and fix element ordering
            2. Navigation must be at the top
            3. Footer must be at the bottom
            4. Related elements should be grouped
            5. Maintain proper content hierarchy
            6. Fix any floating or misplaced elements
            7. Ensure proper parent-child relationships

            IMPORTANT:
            - Analyze the entire document structure
            - Fix any elements that are out of place
            - Maintain semantic HTML structure
            - Ensure proper content flow
            - Check for orphaned elements
            - Verify header hierarchy
            """,
            "practices": """
            Focus on HTML best practices:
            - Semantic tag usage
            - Required attributes
            - Proper nesting
            - HTML5 doctype
            - Meta tags
            - Character encoding
            """
        }

        prompt = f"{base_prompt}\n{type_specific_prompts.get(analysis_type, '')}\n\nHTML to analyze:\n{html}"
        return prompt

    def _format_chat_prompt(self, html: str, user_request: str) -> str:
        """New method specifically for chat requests"""
        chat_prompt = f"""
        You are an expert HTML developer. A user has requested changes to their HTML code.
        
        USER REQUEST: {user_request}

        Generate specific HTML changes that fulfill this request. Focus ONLY on HTML changes - no CSS or JavaScript.
        
        Your response must be valid JSON in this exact format:
        {{
            "changes": {{
                "change1": {{
                    "old": "exact HTML snippet that needs to be replaced",
                    "new": "improved HTML snippet with requested changes",
                    "status": "description of what this change accomplishes"
                }},
                // Add more changes if needed
            }},
            "preview": {{
                "html": "complete improved HTML with ALL changes applied"
            }}
        }}

        RULES:
        1. The 'old' field must contain the EXACT HTML snippet that exists in the code
        2. Only suggest HTML changes, no CSS or JavaScript
        3. Make sure whitespace and indentation in 'old' matches exactly
        4. Each change should be independent and self-contained
        5. If adding new elements, 'old' can be omitted
        6. Be creative and thorough in implementing the user's request
        7. Provide only the JSON response, no additional text

        CURRENT HTML:
        {html}
        """
        return chat_prompt