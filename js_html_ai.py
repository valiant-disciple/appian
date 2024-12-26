from dataclasses import dataclass, asdict
from typing import List, Optional, Union
from pathlib import Path
import json
import os
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from groq import Groq
import traceback
import time
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from uvicorn import Config, Server
import asyncio

client = Groq(api_key="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")

@dataclass
class Suggestion:
    """Dataclass for generating suggestions"""
    code: str
    description: str

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Suggestion':
        return cls(
            code=data['code'],
            description=data['description']
        )

@dataclass
class ErrorResponse:
    """Dataclass for handling error responses"""
    error: str
    details: Optional[str] = None

class AIChatHandler:
    def _init_(self, ai_client):
        self.ai_client = ai_client

    def chat_completion(self, prompt: str) -> str:
        try:
            chat_completion = self.ai_client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192"
            )
            if hasattr(chat_completion, 'content'):
                return str(chat_completion.content)
            elif hasattr(chat_completion, 'choices'):
                return str(chat_completion.choices[0].message.content)
            else:
                return str(chat_completion)
        except Exception as e:
            error_message = f"Error during chat completion: {e}"
            print(error_message)
            raise Exception(error_message)

    def generate_suggestions_overview(self, user_prompt: str) -> Union[List[str], ErrorResponse]:
        """Generates high-level descriptions for suggestions."""
        prompt = f"""
    You are a seasoned JavaScript developer. Generate exactly three visually distinct high-level suggestions for the user's request.

    User Request: {user_prompt}

    Each suggestion should be described in a concise and clear sentence focusing on its unique layout, color scheme, or interactivity.

    Output Format (JSON):
    [
        "string - concise description of suggestion 1",
        "string - concise description of suggestion 2",
        "string - concise description of suggestion 3"
    ]
    No additional text outside the JSON array.
    """
        try:
            response_content = self.chat_completion(prompt)

            # Extract and validate JSON
            start = response_content.find('[')
            end = response_content.rfind(']') + 1
            if start == -1 or end == 0:
                raise ValueError("Response JSON array not found")

            json_str = response_content[start:end]
            descriptions = json.loads(json_str)

            if len(descriptions) == 3 and all(isinstance(desc, str) for desc in descriptions):
                return descriptions
            else:
                raise ValueError("Invalid number of suggestions returned or incomplete structure")
        except Exception as e:
            error_message = f"Error during overview generation: {e}"
            print(error_message)
            return ErrorResponse(error="Overview Generation Failed", details=error_message)


    def generate_code_for_suggestion(self, description: str) -> Union[str, ErrorResponse]:
        """Generates JavaScript code for a specific suggestion."""
        prompt = f"""
    You are a seasoned JavaScript developer. Based on the following high-level description, generate the JavaScript code implementing it.

    Description: {description}

    Provide only the JavaScript code, with no additional text.
    """
        try:
            return self.chat_completion(prompt).strip()
        except Exception as e:
            error_message = f"Error during code generation: {e}"
            print(error_message)
            return ErrorResponse(error="Code Generation Failed", details=error_message)

class JSModernizer:
    def _init_(self, chat_handler: AIChatHandler):
        self.chat_handler = chat_handler
        self.console = Console()

    def get_user_selection_overview(self, overviews: List[str]) -> str:
      """Displays high-level suggestions and allows the user to select one."""
      table = Table(title="Available Options")
      table.add_column("Option", style="cyan")
      table.add_column("Description", style="green")

      for idx, overview in enumerate(overviews, 1):
          table.add_row(f"Option {idx}", overview)

      self.console.print(table)

      selection = Prompt.ask(
          "Select the number of the suggestion to generate code for",
          choices=[str(i) for i in range(1, len(overviews) + 1)]
      )
      return overviews[int(selection) - 1]
    def _launch_live_demo(self, suggestion: Suggestion):
        app = FastAPI()

        @app.get("/", response_class=HTMLResponse)
        async def demo():
            return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Live Demo</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }}
                    h1 {{ color: #333; }}
                    #feature-container {{ margin-top: 20px; border: 1px solid #ccc; padding: 10px; }}
                </style>
            </head>
            <body>
                <h1>Live Demo of Your Feature</h1>
                <div id="feature-container">This is a placeholder. Your JavaScript should modify this area.</div>
                <script>
                    try {{
                        {suggestion.code}
                    }} catch (e) {{
                        console.error("Error in executing user code:", e);
                        document.getElementById('feature-container').innerText = 
                            "Error: Unable to display the feature. Check console for details.";
                    }}
                </script>
            </body>
            </html>
            """

        @app.get("/favicon.ico")
        async def favicon():
            return HTMLResponse(content="", status_code=204)

        print("Launching live demo at http://127.0.0.1:8000")

        config = Config(app, host="127.0.0.1", port=8000, loop="asyncio")
        server = Server(config)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(server.serve())

    def save_modification(self, suggestion: Suggestion, output_path: str):
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(suggestion.code)
            self.console.print(f"[green]Modified JavaScript saved to {output_path}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error saving file: {str(e)}[/red]")

def main():
    console = Console()

    input_file = Prompt.ask("Enter the path to the JavaScript file")
    output_file = "/modified_output.js"
    user_prompt = Prompt.ask("Describe the feature and UI improvements you want in detail")

    if not os.path.exists(input_file):
        console.print("[red]Input file does not exist.[/red]")
        exit(1)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            js_code = f.read()

        console.print("[cyan]Generating high-level suggestions based on your request...[/cyan]")

        chat_handler = AIChatHandler(client)
        modernizer = JSModernizer(chat_handler)

        overviews = chat_handler.generate_suggestions_overview(user_prompt)

        if isinstance(overviews, ErrorResponse):
            console.print(f"[red]{overviews.error}: {overviews.details}[/red]")
            return

        selected_overview = modernizer.get_user_selection_overview(overviews)

        console.print(f"[cyan]Generating code for selected suggestion: {selected_overview}[/cyan]")
        code_result = chat_handler.generate_code_for_suggestion(selected_overview)

        if isinstance(code_result, ErrorResponse):
            console.print(f"[red]{code_result.error}: {code_result.details}[/red]")
            return

        if Confirm.ask("Would you like to apply best practices to your selection?"):
            best_practices_result = chat_handler.apply_best_practices(code_result)
            if isinstance(best_practices_result, ErrorResponse):
                console.print(f"[red]{best_practices_result.error}: {best_practices_result.details}[/red]")
            else:
                code_result = best_practices_result

        if Confirm.ask("Would you like to save the generated code?"):
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(code_result)
            console.print(f"[green]Modified JavaScript saved to {output_file}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        console.print(traceback.format_exc())
main()
#yes, copy paste. suffer.