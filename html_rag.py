from dataclasses import dataclass
from typing import List
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
from groq import Groq
import json
import os
import tempfile
import webbrowser
import hashlib
from bs4 import BeautifulSoup

@dataclass
class HTMLVariation:
    html: str  # The modified HTML
    changes: List[str]  # List of changes made
    
    @classmethod
    def from_dict(cls, data: dict) -> 'HTMLVariation':
        """Create an HTMLVariation from a dictionary, with validation."""
        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary")
        
        required_fields = {'html', 'changes'}
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        if not isinstance(data['changes'], list):
            raise ValueError("Changes must be a list")
            
        if not data['html'] or not data['html'].strip():
            raise ValueError("HTML cannot be empty")
            
        return cls(
            html=data['html'],
            changes=data['changes']
        )

class ChatCompletionService:
    def __init__(self):
        self.client = Groq(api_key="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")

    def generate_completion(self, prompt: str) -> str:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )
            if hasattr(chat_completion, 'content'):
                return str(chat_completion.content)
            elif hasattr(chat_completion, 'choices'):
                return str(chat_completion.choices[0].message.content)
            else:
                return str(chat_completion)
        except Exception as e:
            raise Exception(f"Error generating completion: {str(e)}")

class ModernizationPreview:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()

    def show_preview(self, html: str, index: int):
        """Show preview in default browser."""
        filename = hashlib.md5(f"variation_{index}".encode()).hexdigest()[:10]
        preview_path = os.path.join(self.temp_dir, f"{filename}.html")
        with open(preview_path, 'w', encoding='utf-8') as f:
            f.write(html)
        webbrowser.open(f'file://{preview_path}')

class HTMLEnhancementCLI:
    def __init__(self):
        self.console = Console()
        self.chat_service = ChatCompletionService()
        self.preview = ModernizationPreview()

    def generate_variation(self, html: str, request: str, variation_num: int) -> HTMLVariation:
        """Generate a single variation of the requested changes."""
        prompt = f"""
You are an expert web designer. Generate variation {variation_num} for this request:
"{request}"

Original HTML:
{html}

Return ONLY a JSON object with these keys:
1. "html": The complete modified HTML with all changes
2. "changes": List of specific changes made

Example response:
{{
    "html": "<!DOCTYPE html><html>...[full modified HTML]...</html>",
    "changes": [
        "Added responsive navigation menu",
        "Updated color scheme to modern palette"
    ]
}}

Important: Return ONLY the JSON object, nothing else."""
        
        try:
            response = self.chat_service.generate_completion(prompt)
            
            # Find JSON object in response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON object found in response")
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            return HTMLVariation.from_dict(data)
            
        except Exception as e:
            self.console.print(f"[red]Error generating variation {variation_num}: {str(e)}[/red]")
            return None

    def show_variation_preview(self, variation: HTMLVariation, index: int):
        """Display variation details and show preview."""
        if not variation:
            return

        # Show changes
        changes_table = Table(title=f"Variation {index} Changes")
        changes_table.add_column("Change", style="green")
        for change in variation.changes:
            changes_table.add_row(change)
        self.console.print(changes_table)
        
        # Show HTML preview
        self.preview.show_preview(variation.html, index)

    def run(self):
        """Run the enhanced CLI application."""
        self.console.print("[bold blue]HTML Enhancement Tool[/bold blue]")
        
        # Get input HTML
        while True:
            file_path = Prompt.ask("\n[yellow]Enter the path to your HTML file[/yellow]")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html = f.read()
                # Validate HTML
                if not BeautifulSoup(html, 'html.parser').find():
                    raise ValueError("Invalid or empty HTML file")
                break
            except Exception as e:
                self.console.print(f"[red]Error reading file: {str(e)}[/red]")
                if not Confirm.ask("[red]Would you like to try another file?[/red]"):
                    return

        request = Prompt.ask("\n[yellow]What would you like to change or enhance?[/yellow]")
        
        # Generate variations with retry logic
        self.console.print("\n[green]Generating variations...[/green]")
        variations = []
        max_retries = 2
        
        for i in range(1, 4):
            retry_count = 0
            while retry_count <= max_retries and len(variations) < i:
                variation = self.generate_variation(html, request, i)
                if variation:
                    variations.append(variation)
                    break
                retry_count += 1
                if retry_count <= max_retries:
                    self.console.print(f"[yellow]Retrying variation {i} (attempt {retry_count + 1})...[/yellow]")
            
            if variation:
                self.show_variation_preview(variation, len(variations))
                if i < 3 and len(variations) > 0:
                    Prompt.ask("\nPress Enter to see the next variation")

        if not variations:
            self.console.print("[red]Failed to generate any valid variations[/red]")
            return

        # Save result
        if len(variations) > 1:
            choice = Prompt.ask(
                "\n[yellow]Which variation would you like to apply?[/yellow]",
                choices=[str(i) for i in range(1, len(variations) + 1)]
            )
            selected_variation = variations[int(choice) - 1]
        else:
            selected_variation = variations[0]
        
        if Confirm.ask("\nWould you like to save the enhanced HTML?"):
            original_path = Path(file_path)
            default_filename = f"{original_path.stem}_enhanced{original_path.suffix}"
            filename = Prompt.ask(
                "Enter filename",
                default=str(original_path.parent / default_filename)
            )
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(selected_variation.html)
                self.console.print(f"\n[green]Enhanced HTML saved to {filename}[/green]")
            except Exception as e:
                self.console.print(f"[red]Error saving file: {str(e)}[/red]")

def main():
    cli = HTMLEnhancementCLI()
    cli.run()

if __name__ == "__main__":
    main()