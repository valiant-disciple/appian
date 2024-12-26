from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class Template:
    """Structure for code templates"""
    name: str
    description: str
    html: str
    css: str
    js: str = ""
    tags: List[str] = field(default_factory=list)

class TemplateManager:
    """Manages code templates"""
    
    def __init__(self):
        self.templates: Dict[str, Template] = {}
        self._initialize_templates()

    def _initialize_templates(self):
        """Initialize default templates"""
        self.templates['landing'] = Template(
            name="Landing Page",
            description="A modern landing page template",
            html="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome</title>
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section id="hero">
            <h1>Welcome to Our Site</h1>
            <p>Discover amazing things with us.</p>
            <button>Get Started</button>
        </section>
    </main>
    <footer>
        <p>&copy; 2024 Your Company</p>
    </footer>
</body>
</html>
""".strip(),
            css="""
:root {
    --primary-color: #4CAF50;
    --text-color: #333;
    --bg-color: #fff;
}

body {
    font-family: 'Arial', sans-serif;
    margin: 0;
    padding: 0;
    line-height: 1.6;
    color: var(--text-color);
    background: var(--bg-color);
}

header {
    background: var(--primary-color);
    padding: 1rem;
}

nav ul {
    list-style: none;
    display: flex;
    gap: 2rem;
    margin: 0;
    padding: 0;
}

nav a {
    color: white;
    text-decoration: none;
}

#hero {
    text-align: center;
    padding: 4rem 2rem;
}

button {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    opacity: 0.9;
}

footer {
    text-align: center;
    padding: 2rem;
    background: #f5f5f5;
}

@media (max-width: 768px) {
    nav ul {
        flex-direction: column;
        gap: 1rem;
    }
}
""".strip(),
            js="""
document.querySelector('button').addEventListener('click', () => {
    alert('Welcome! Thanks for clicking!');
});
""".strip(),
            tags=['landing', 'responsive', 'modern']
        )

    def get_template(self, name: str) -> Optional[Template]:
        """Get a template by name"""
        return self.templates.get(name)

    def list_templates(self) -> List[Template]:
        """List all available templates"""
        return list(self.templates.values())

    def search_templates(self, tag: str) -> List[Template]:
        """Search templates by tag"""
        return [t for t in self.templates.values() if tag in t.tags]