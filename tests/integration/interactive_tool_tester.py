import asyncio
import json
import sys
from typing import Any, Dict, List

# Proje kök dizinini Python yoluna ekle, böylece 'src' modülü bulunabilir.
if '.' not in sys.path:
    sys.path.insert(0, '.')

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax

# Proje importları
from mcp import types as mcp_types
from src.n8n_mcp.client import N8nApiError
from src.n8n_mcp.config import load_settings
from src.n8n_mcp.server import N8nMcpServer, get_tool_definitions

# rich konsolunu başlat
console = Console()


async def get_tool_arguments(tool: mcp_types.Tool) -> Dict[str, Any]:
    """Kullanıcıdan seçilen araç için argümanları interaktif olarak alır."""
    args = {}
    console.print(Panel(f"Enter arguments for [bold cyan]{tool.name}[/]", title="Argument Input", border_style="green"))

    properties = tool.inputSchema.get("properties", {})
    required_fields = tool.inputSchema.get("required", [])

    if not properties:
        console.print("[yellow]This tool does not require any arguments.[/yellow]")
        return args

    for name, prop in properties.items():
        is_required = name in required_fields
        prop_type = prop.get("type", "string")
        default_val = prop.get("default")

        # Prompt metnini oluştur
        prompt_text = f"  - [b]{name}[/b] ({prop_type})"
        if is_required:
            prompt_text += " [red](required)[/red]"
        else:
            prompt_text += " (optional"
            if default_val is not None:
                prompt_text += f", default: {default_val}"
            prompt_text += ")"

        console.print(Markdown(prompt_text))
        console.print(f"    [dim]{prop.get('description', '')}[/dim]")

        # Kullanıcıdan input al
        user_input = Prompt.ask("    > ")

        if not user_input:
            if is_required:
                console.print(f"[bold red]Error: Required field '{name}' cannot be empty.[/bold red]")
                # Gerekli alan boşsa, işlemi iptal et
                raise ValueError(f"Required field '{name}' was not provided.")
            # İsteğe bağlı ve boşsa atla
            continue

        # Tipe göre değeri dönüştür
        try:
            if prop_type == "integer":
                args[name] = int(user_input)
            elif prop_type == "boolean":
                args[name] = user_input.lower() in ["true", "y", "yes", "1"]
            elif prop_type == "array":
                # Virgülle ayrılmış değerleri listeye çevir
                args[name] = [item.strip() for item in user_input.split(",")]
            elif prop_type == "object":
                # JSON string'i olarak al
                args[name] = json.loads(user_input)
            else:  # string
                args[name] = user_input
        except (ValueError, json.JSONDecodeError) as e:
            console.print(f"[bold red]Invalid input for type '{prop_type}': {e}[/bold red]")
            raise ValueError(f"Invalid input for field '{name}'.")

    return args


async def call_tool_handler(server: N8nMcpServer, tool_name: str, arguments: dict) -> List[mcp_types.TextContent]:
    """Sunucu üzerindeki doğru _handle metodunu dinamik olarak çağırır."""
    handler_name = f"_handle_{tool_name}"
    handler_method = getattr(server, handler_name, None)

    if not handler_method or not asyncio.iscoroutinefunction(handler_method):
        raise ValueError(f"No valid async handler method '{handler_name}' found on server for tool '{tool_name}'")

    return await handler_method(arguments)


async def main():
    """İnteraktif test aracını çalıştıran ana fonksiyon."""
    console.print(Markdown("# n8n MCP Server - Interactive Tool Tester 🛠️"))

    server = None
    try:
        # 1. Ayarları yükle ve sunucuyu başlat
        console.print("▶️  Loading settings and initializing server...")
        settings = load_settings(use_env=True)
        server = N8nMcpServer(settings)
        await server.initialize()

        # Başlangıçta sağlık kontrolü yap
        health_result = await server._handle_health_check({})
        raw_text = health_result[0].text
        health_data = json.loads(raw_text)
        if health_data.get("healthy"):
            console.print("[bold green]✅ n8n API connection verified.[/bold green]")
        else:
            console.print("[bold red]❌ n8n API health check failed. Exiting.[/bold red]")
            return

        # 2. Mevcut araçları al
        tools = get_tool_definitions()
        tool_map = {str(i + 1): tool for i, tool in enumerate(tools)}

        # 3. Ana döngü
        while True:
            console.print(Markdown("--- \n### Select a tool to test:"))
            for index, tool in tool_map.items():
                console.print(f"  [cyan]{index}[/cyan]: [bold]{tool.name}[/bold] - {tool.description}")
            console.print("  [red]q[/red]: [bold]Quit[/bold]")

            choice = Prompt.ask("\nEnter your choice", default="q").lower()

            if choice == "q":
                break

            selected_tool = tool_map.get(choice)
            if not selected_tool:
                console.print("[bold red]Invalid choice, please try again.[/bold red]")
                continue

            try:
                # 4. Parametreleri al
                arguments = await get_tool_arguments(selected_tool)

                # 5. Aracı çalıştır
                console.print(f"\n▶️  Executing [bold cyan]{selected_tool.name}[/] with args: {arguments}")
                result_content = await call_tool_handler(server, selected_tool.name, arguments)

                # 6. Sonucu göster
                console.print(Markdown(f"### ✅ Result from `{selected_tool.name}`:"))
                if result_content and isinstance(result_content, list) and result_content[0].type == "text":
                    raw_text = result_content[0].text
                    # Hata mesajı olup olmadığını kontrol et
                    if "Error" in raw_text or "Missing required field" in raw_text or "Workflow not found" in raw_text:
                        console.print(Panel(f"[yellow]Server-side tool error:[/] {raw_text}", title="Tool Error", border_style="yellow"))
                    else:
                        try:
                            # JSON olarak formatlamayı dene
                            parsed_json = json.loads(raw_text)
                            pretty_json = json.dumps(parsed_json, indent=2, ensure_ascii=False)
                            console.print(Syntax(pretty_json, "json", theme="monokai", line_numbers=True))
                        except json.JSONDecodeError:
                            # Düz metin olarak yazdır
                            console.print(raw_text)
                else:
                    console.print(f"[yellow]Received an unexpected result format:[/] {result_content}")

            except N8nApiError as e:
                console.print(Panel(f"[bold red]API Error:[/] {e.message}", title=f"Error in {selected_tool.name}", border_style="red"))
            except ValueError as e:
                # Argüman giriş hatası
                console.print(Panel(f"[bold red]Input Error:[/] {e}", title="Operation Cancelled", border_style="red"))
            except Exception as e:
                console.print(Panel(f"[bold red]An unexpected error occurred:[/] {e}", title=f"Error in {selected_tool.name}", border_style="red"))

    except Exception as e:
        console.print(Panel(f"[bold red]A critical error occurred during initialization:[/] {e}", title="Critical Error", border_style="red"))
    finally:
        if server:
            await server.cleanup()
            console.print("\n[bold green]✅ Resources cleaned up. Exiting.[/bold green]")
        console.print(Markdown("---"))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user. Exiting.[/yellow]")