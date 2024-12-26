import chromadb
from chromadb.utils import embedding_functions
import openai
from bs4 import BeautifulSoup
import json
from typing import List, Dict
import os

class HTMLEnhancementSystem:
    def __init__(self, openai_api_key: str):
        # Initialize OpenAI client
        openai.api_key = openai_api_key
        
        # Initialize ChromaDB client
        self.client = chromadb.Client()
        
        # Use OpenAI embeddings
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name="text-embedding-3-small"
        )
        
        # Create collections for different types of content
        self.template_collection = self.client.create_collection(
            name="html_templates",
            embedding_function=self.embedding_function
        )
        
        self.component_collection = self.client.create_collection(
            name="html_components",
            embedding_function=self.embedding_function
        )

    def add_template(self, html: str, metadata: Dict):
        """Add a template to the database."""
        # Parse HTML to get a cleaner version
        soup = BeautifulSoup(html, 'html.parser')
        
        # Convert list metadata values to strings
        for key, value in metadata.items():
            if isinstance(value, list):
                metadata[key] = ', '.join(value)
        
        # Create a description for the template
        description = f"Template style: {metadata.get('style', 'unknown')}. " \
                    f"Purpose: {metadata.get('purpose', 'general')}. " \
                    f"Features: {metadata.get('features', 'None')}"
        
        self.template_collection.add(
            documents=[str(soup)],
            metadatas=[metadata],
            ids=[f"template_{len(self.template_collection.get()['ids']) + 1}"]
        )

    def add_component(self, component: str, metadata: Dict):
        """Add a component (like animations, navigation bars, etc.) to the database."""
        # Convert list metadata values to strings
        for key, value in metadata.items():
            if isinstance(value, list):
                metadata[key] = ', '.join(value)
        
        self.component_collection.add(
            documents=[component],
            metadatas=[metadata],
            ids=[f"component_{len(self.component_collection.get()['ids']) + 1}"]
        )

    def search_templates(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search for relevant templates based on user query."""
        results = self.template_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return self._format_results(results)

    def search_components(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search for relevant components based on user query."""
        results = self.component_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return self._format_results(results)

    def enhance_html(self, html: str, enhancement_request: str) -> str:
        """
        Enhance HTML based on user request using OpenAI's GPT model.
        """
        # First, search for relevant components if needed
        components = self.search_components(enhancement_request)
        
        # Create a prompt for GPT
        prompt = f"""
        Original HTML:
        {html}
        
        Enhancement request: {enhancement_request}
        
        Relevant components found in database:
        {json.dumps(components, indent=2)}
        
        Please enhance the HTML according to the request. Incorporate relevant components 
        if applicable. Return only the modified HTML code.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert web developer. Modify the HTML according to the user's request."},
                {"role": "user", "content": prompt}
            ]
        )
        
        enhanced_html = response.choices[0].message.content
        return enhanced_html

    def _format_results(self, results: Dict) -> List[Dict]:
        """Format ChromaDB results into a more usable structure."""
        formatted_results = []
        for i in range(len(results['ids'])):
            formatted_results.append({
                'id': results['ids'][i],
                'content': results['documents'][i],
                'metadata': results['metadatas'][i]
            })
        return formatted_results

def initialize_database():
    """Initialize the database with some example templates and components."""
    system = HTMLEnhancementSystem(openai_api_key=os.getenv('OPENAI_API_KEY'))
    
    # Add some example templates
    modern_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Modern Template</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    </head>
    <body class="bg-gray-100">
        <header class="bg-white shadow">
            <nav class="container mx-auto px-6 py-4">
                <h1 class="text-2xl font-bold">Modern Website</h1>
            </nav>
        </header>
        <main class="container mx-auto px-6 py-8">
            <!-- Content goes here -->
        </main>
    </body>
    </html>
    """
    
    system.add_template(
        modern_template,
        {
            'style': 'modern',
            'purpose': 'general',
            'features': ['responsive', 'clean design', 'tailwind css']
        }
    )
    
    # Add some example components
    bubble_animation = """
    <style>
    .bubble {
        position: fixed;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        animation: float 8s ease-in-out infinite;
    }
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
        100% { transform: translateY(0px); }
    }
    </style>
    <script>
    function createBubbles() {
        const bubbleCount = 10;
        const container = document.body;
        
        for (let i = 0; i < bubbleCount; i++) {
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.style.width = Math.random() * 100 + 50 + 'px';
            bubble.style.height = bubble.style.width;
            bubble.style.left = Math.random() * 100 + 'vw';
            bubble.style.animationDelay = Math.random() * 5 + 's';
            container.appendChild(bubble);
        }
    }
    createBubbles();
    </script>
    """
    
    system.add_component(
        bubble_animation,
        {
            'type': 'animation',
            'name': 'floating bubbles',
            'features': ['interactive', 'decorative', 'scroll-responsive']
        }
    )
    
    return system

initialize_database()