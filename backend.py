from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Optional
from groq import Groq
from functools import lru_cache
from enum import Enum
import logging
from datetime import datetime
from os import getenv
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImprovementType(str, Enum):
    SEMANTIC = "semantic"
    DESIGN = "design"
    ACCESSIBILITY = "accessibility"

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class HTMLRequest(BaseModel):
    html: str = Field(..., description="HTML content to analyze")
    improvement_types: Optional[List[ImprovementType]] = Field(
        default=list(ImprovementType),
        description="Types of improvements to analyze"
    )

class Improvement(BaseModel):
    id: str
    type: ImprovementType
    priority: Priority
    selector: str
    suggestion: str
    original_code: str
    improved_code: str
    explanation: str
    category: str

class Settings:
    def __init__(self):
        self.groq_api_key = getenv("GROQ_API_KEY")
        self.allowed_origins = getenv("ALLOWED_ORIGINS", "*").split(",")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

def get_groq_client(settings: Settings = Depends(get_settings)) -> Groq:
    return Groq(api_key=settings.groq_api_key)

app = FastAPI(
    title="HTML Analyzer API",
    description="API for analyzing and improving HTML content",
    version="1.0.0"
)

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

async def generate_completion(prompt: str, client: Groq) -> str:
    """Generate completion using Groq API with error handling."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        
        if hasattr(chat_completion, 'content'):
            return str(chat_completion.content)
        elif hasattr(chat_completion, 'choices') and chat_completion.choices:
            return str(chat_completion.choices[0].message.content)
        else:
            raise ValueError("Unexpected response format from Groq API")
            
    except Exception as e:
        logger.error(f"Error generating completion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating completion: {str(e)}"
        )

def extract_page_structure(html: str) -> Dict:
    """Extract page structure from HTML content."""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        return {
            "elements": [
                {
                    "tag": elem.name,
                    "classes": elem.get("class", []),
                    "id": elem.get("id", ""),
                    "content": elem.get_text()[:100] if elem.get_text() else "",
                    "attributes": {k: v for k, v in elem.attrs.items() if k != "class"}
                }
                for elem in soup.find_all()
            ]
        }
    except Exception as e:
        logger.error(f"Error extracting page structure: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Invalid HTML content"
        )

IMPROVEMENT_PROMPTS = {
    ImprovementType.SEMANTIC: """Analyze this HTML structure and suggest semantic improvements. For each suggestion, provide:
    1. What element to change
    2. Why it should be changed
    3. What it should be changed to
    4. Example code
    Focus on proper HTML5 semantic elements, ARIA roles, and structural improvements.
    Return as JSON array of improvements.""",
    
    ImprovementType.DESIGN: """Suggest modern design improvements for this HTML structure. Include:
    1. Typography improvements (font pairs, sizing, readability)
    2. Color scheme suggestions
    3. Spacing and layout improvements
    4. Component styling
    For each suggestion, provide specific CSS code.
    Return as JSON array of improvements.""",
    
    ImprovementType.ACCESSIBILITY: """Analyze this HTML for accessibility improvements. Suggest:
    1. ARIA attributes needed
    2. Keyboard navigation improvements
    3. Screen reader optimizations
    4. Color contrast issues
    For each suggestion, provide specific code changes.
    Return as JSON array of improvements."""
}

@app.post("/analyze", response_model=Dict[str, List[Improvement]])
async def analyze_html(
    request: HTMLRequest,
    client: Groq = Depends(get_groq_client)
):
    """
    Analyze HTML content and suggest improvements.
    Returns a list of suggested improvements based on specified improvement types.
    """
    try:
        structure = extract_page_structure(request.html)
        improvements = []

        for imp_type in request.improvement_types:
            prompt = IMPROVEMENT_PROMPTS[imp_type]
            try:
                response = await generate_completion(
                    prompt + json.dumps(structure),
                    client
                )
                type_improvements = json.loads(response)
                improvements.extend(type_improvements)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing improvements for {imp_type}: {str(e)}")
                continue

        return {"improvements": improvements}
    
    except Exception as e:
        logger.error(f"Error in analyze_html: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing HTML: {str(e)}"
        )

@app.post("/apply-improvements")
async def apply_improvements(
    html: str,
    selected_improvements: List[Improvement]
):
    """
    Apply selected improvements to HTML content.
    Returns the improved HTML with applied changes.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        for improvement in selected_improvements:
            elements = soup.select(improvement.selector)
            for element in elements:
                try:
                    new_element = BeautifulSoup(
                        improvement.improved_code,
                        'html.parser'
                    )
                    element.replace_with(new_element)
                except Exception as e:
                    logger.error(
                        f"Error applying improvement {improvement.id}: {str(e)}"
                    )
                    continue
        
        return {"improved_html": str(soup)}
    
    except Exception as e:
        logger.error(f"Error in apply_improvements: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error applying improvements: {str(e)}"
        )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(    
        app,
        host="0.0.0.0",
        port=int(getenv("PORT", "3000"))
    )