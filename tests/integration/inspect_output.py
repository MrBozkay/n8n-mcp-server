import asyncio
import json
import sys

# Proje kök dizinini Python yoluna ekle, böylece 'src' modülü bulunabilir.
if '.' not in sys.path:
    sys.path.insert(0, '.')

from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.panel import Panel

# Proje importları
from mcp import types as mcp_types
from src.n8n_mcp.server import N8nMcpServer
from src.n8n_mcp.client import N8nApiError
from src.n8n_mcp.config import load_settings

# Initialize rich console
console = Console()

async def test_tool_end_to_end(tool_name: str, arguments: dict):
    """
    Performs a true end-to-end integration test for a given tool
    by simulating a tool call through the N8nMcpServer.
    """
    console.print(Markdown(f"# E2E Test for: `{tool_name}` 🚀"))
    
    server = None
    try:
        # 1. Load real settings from .env file
        settings = load_settings(use_env=True)
        
        # 2. Instantiate and initialize the server
        server = N8nMcpServer(settings)
        await server.initialize()
        
        console.print(f"▶️  Simulating call to [bold cyan]{tool_name}[/] with args: {arguments}")

        # Dinamik olarak sunucu örneğindeki handler metodunu bul ve çağır
        handler_name = f"_handle_{tool_name}"
        handler_method = getattr(server, handler_name, None)

        if not handler_method or not asyncio.iscoroutinefunction(handler_method):
            raise AttributeError(f"No valid async handler method '{handler_name}' found on server for tool '{tool_name}'")

        result_content = await handler_method(arguments)

        # 5. Display the final result as the server would return it
        console.print(Markdown(f"### ✅ Result from Server for `{tool_name}`:"))
        
        # The _handle_... methods directly return list[types.TextContent]
        # We need to check if the first item in the list is an error or actual content.
        if result_content and isinstance(result_content, list) and result_content[0].type == "text":
            raw_text = result_content[0].text
            # Check if the text itself indicates an error (e.g., "Missing required field")
            if "Error" in raw_text or "Missing required field" in raw_text or "Workflow not found" in raw_text:
                console.print(Panel(f"[yellow]Server-side tool error:[/] {raw_text}", title="Tool Error", border_style="yellow"))
            else:
                try:
                    # Try to parse as JSON, if not, print as plain text
                    parsed_json = json.loads(raw_text)
                    pretty_json = json.dumps(parsed_json, indent=2)
                    console.print(Syntax(pretty_json, "json", theme="default", line_numbers=True))
                except json.JSONDecodeError:
                    console.print(raw_text)
        else:
            console.print(f"[yellow]Received an unexpected result format:[/] {result_content}")

    except N8nApiError as e:
        console.print(Panel(f"[bold red]API Error:[/] {e.message}", title=f"Error in {tool_name}", border_style="red"))
    except Exception as e:
        console.print(Panel(f"[bold red]An unexpected error occurred:[/] {e}", title=f"Error in {tool_name}", border_style="red"))
    finally:
        if server:
            await server.cleanup()
            console.print(f"✅ Resources for `{tool_name}` test cleaned up.")
        console.print(Markdown("---"))


async def main():
    """Main async function to run the inspection scenarios."""
    console.print(Markdown("# Running E2E Server Integration Tests"))
    
     # Scenario 1: Health check
    await test_tool_end_to_end(
        tool_name="health_check",
        arguments={}
    )

    # Scenario 2: List first 2 workflows
    await test_tool_end_to_end(
        tool_name="list_workflows",
        arguments={"limit": 5}
    )
    
   
    
    # Scenario 3: Get a non-existent workflow to test error handling
    await test_tool_end_to_end(
        tool_name="get_workflow",
        arguments={"workflow_id": "non-existent-id-12345"}
    )

    # Scenario 4: Create a new workflow for testing
    test_workflow_name = "E2E Test Workflow"
    await test_tool_end_to_end(
        tool_name="create_workflow",
        arguments={"name": test_workflow_name, "active": False}
    )

    # Scenario 5: Search for the newly created workflow
    await test_tool_end_to_end(
        tool_name="search_workflows",
        arguments={"query": test_workflow_name}
    )
    # Not: Bu senaryodan sonra `delete_workflow` ile oluşturulan iş akışını silmek
    # iyi bir pratik olacaktır, ancak bunun için `create_workflow`'dan dönen ID'yi yakalamak gerekir.


if __name__ == "__main__":
    asyncio.run(main())
