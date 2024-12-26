from dataclasses import dataclass
from typing import Dict, Optional
import json
import zipfile
import io

@dataclass
class ExportFormat:
    """Export format configuration"""
    name: str
    file_extension: str
    include_html: bool = True
    include_css: bool = True
    include_js: bool = True
    bundle: bool = False

class ExportManager:
    """Handle code export in various formats"""

    FORMATS = {
        "HTML": ExportFormat("HTML", ".html", bundle=True),
        "Component Files": ExportFormat("Component Files", ".zip"),
        "React Component": ExportFormat("React Component", ".jsx"),
        "Vue Component": ExportFormat("Vue Component", ".vue", bundle=True),
        "Web Component": ExportFormat("Web Component", ".js", bundle=True)
    }

    def export(self, format_name: str, html: str, css: str, js: str, 
               component_name: str = "MyComponent") -> Optional[str]:
        """Export code in specified format"""
        if format_name not in self.FORMATS:
            raise ValueError(f"Unknown format: {format_name}")

        export_format = self.FORMATS[format_name]
        
        if export_format.bundle:
            return self._bundle_code(format_name, html, css, js, component_name)
        else:
            return self._create_component_files(html, css, js, component_name)

    def _bundle_code(self, format_name: str, html: str, css: str, js: str, 
                    component_name: str) -> str:
        """Bundle code based on format"""
        if format_name == "HTML":
            return self._create_html_bundle(html, css, js)
        elif format_name == "React Component":
            return self._create_react_component(html, css, js, component_name)
        elif format_name == "Vue Component":
            return self._create_vue_component(html, css, js, component_name)
        elif format_name == "Web Component":
            return self._create_web_component(html, css, js, component_name)
        return ""

    def _create_html_bundle(self, html: str, css: str, js: str) -> str:
        """Create bundled HTML file"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exported Component</title>
    <style>
{css}
    </style>
</head>
<body>
{html}
    <script>
{js}
    </script>
</body>
</html>
"""

    def _create_react_component(self, html: str, css: str, js: str, 
                              component_name: str) -> str:
        """Create React component"""
        # Convert HTML to JSX
        jsx = html.replace('class=', 'className=')
        
        return f"""
import React from 'react';

const {component_name} = () => {{
    const styles = {{
{self._indent_css(css)}
    }};

    {js}

    return (
        <div style={{styles.container}}>
            {jsx}
        </div>
    );
}};

export default {component_name};
"""

    def _create_vue_component(self, html: str, css: str, js: str, 
                            component_name: str) -> str:
        """Create Vue component"""
        return f"""
<template>
{self._indent_code(html)}
</template>

<script>
export default {{
    name: '{component_name}',
    data() {{
        return {{}}
    }},
    methods: {{
{self._indent_code(js, 8)}
    }}
}}
</script>

<style scoped>
{css}
</style>
"""

    def _create_web_component(self, html: str, css: str, js: str, 
                            component_name: str) -> str:
        """Create Web Component"""
        class_name = "".join(word.capitalize() for word in component_name.split("-"))
        return f"""
class {class_name} extends HTMLElement {{
    constructor() {{
        super();
        this.attachShadow({{mode: 'open'}});
    }}

    connectedCallback() {{
        this.shadowRoot.innerHTML = `
            <style>
{self._indent_code(css, 12)}
            </style>
{self._indent_code(html, 12)}
        `;

{self._indent_code(js, 8)}
    }}
}}

customElements.define('{component_name}', {class_name});
"""

    def _create_component_files(self, html: str, css: str, js: str, 
                              component_name: str) -> bytes:
        """Create ZIP with component files"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"{component_name}.html", html)
            zip_file.writestr(f"{component_name}.css", css)
            zip_file.writestr(f"{component_name}.js", js)
            
            # Add package.json for npm
            package_json = {
                "name": component_name.lower(),
                "version": "1.0.0",
                "description": "Exported web component",
                "main": f"{component_name}.js",
                "scripts": {
                    "test": "echo \"Error: no test specified\" && exit 1"
                }
            }
            zip_file.writestr('package.json', json.dumps(package_json, indent=2))

        return zip_buffer.getvalue()

    def _indent_code(self, code: str, spaces: int = 4) -> str:
        """Indent code with specified number of spaces"""
        indent = " " * spaces
        return "\n".join(indent + line for line in code.split("\n"))

    def _indent_css(self, css: str) -> str:
        """Convert CSS to JavaScript object format"""
        rules = {}
        current_selector = ""
        
        for line in css.split("\n"):
            line = line.strip()
            if line.endswith("{"):
                current_selector = line[:-1].strip()
                rules[current_selector] = {}
            elif line.endswith("}"):
                current_selector = ""
            elif ":" in line and current_selector:
                prop, value = line.split(":", 1)
                prop = prop.strip()
                value = value.strip().rstrip(";")
                rules[current_selector][prop] = value

        # Convert to JavaScript object format
        js_rules = []
        for selector, properties in rules.items():
            props = [f"    {prop}: '{value}'" for prop, value in properties.items()]
            js_rules.append(f"{selector}: {{\n{',\\n'.join(props)}\n}}")

        return ",\n".join(js_rules)