"""CLI interactiva del agente Hermes."""
import os
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from src.config import get_config, reload_config
from src.memory.db import get_memory
from src.providers import ProviderFactory, get_default_provider
from src.tools import list_all_tools


console = Console()


class HermesCLI:
    """CLI interactiva para el agente Hermes."""
    
    def __init__(self, session_id: int | None = None):
        self.console = console
        self.memory = get_memory()
        self.session_id = self.memory.get_or_create_session(session_id)
        self.provider = get_default_provider()
        self.running = True
    
    def run(self) -> None:
        """Inicia el loop principal."""
        self._print_banner()
        
        while self.running:
            try:
                user_input = Prompt.ask(
                    "[bold cyan]hermes>[/bold cyan]",
                    console=self.console
                )
                
                if not user_input.strip():
                    continue
                
                self._process_input(user_input)
            
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Usa /exit para salir[/yellow]")
            except EOFError:
                break
    
    def _print_banner(self) -> None:
        """Imprime el banner de inicio."""
        banner = """
╔══════════════════════════════════════╗
║     🤖 Hermes Agent v0.1.0          ║
║     Asistente IA Multi-proveedor     ║
╚══════════════════════════════════════╝

Escribe /help para ver comandos disponibles.
"""
        self.console.print(Panel(banner.strip(), border_style="cyan"))
    
    def _process_input(self, user_input: str) -> None:
        """Procesa input del usuario."""
        # Comandos especiales
        if user_input.startswith("/"):
            self._handle_command(user_input)
            return
        
        # Mensaje normal al LLM
        self._chat(user_input)
    
    def _handle_command(self, command: str) -> None:
        """Maneja comandos CLI."""
        parts = command[1:].split()
        cmd = parts[0].lower() if parts else ""
        args = parts[1:]
        
        handlers = {
            "help": self._cmd_help,
            "exit": self._cmd_exit,
            "quit": self._cmd_exit,
            "clear": self._cmd_clear,
            "model": self._cmd_model,
            "tools": self._cmd_tools,
            "history": self._cmd_history,
            "session": self._cmd_session,
            "reload": self._cmd_reload,
            "run": self._cmd_run,
        }
        
        handler = handlers.get(cmd)
        if handler:
            handler(*args)
        else:
            self.console.print(f"[red]Comando desconocido: /{cmd}[/red]")
            self.console.print("Usa /help para ver comandos disponibles.")
    
    def _cmd_help(self, *args) -> None:
        """Muestra ayuda."""
        help_text = """
# Comandos disponibles

## General
- `/help` - Muestra esta ayuda
- `/clear` - Limpia la pantalla
- `/exit` - Sale del agente

## Proveedor
- `/model [nombre]` - Muestra o cambia el proveedor LLM actual
- `/reload` - Recarga configuración

## Herramientas
- `/tools` - Lista herramientas disponibles

## Memoria
- `/history` - Muestra historial de la sesión
- `/session [id]` - Cambia a otra sesión
"""
        self.console.print(Markdown(help_text))
    
    def _cmd_exit(self, *args) -> None:
        """Sale del agente."""
        self.console.print("[cyan]👋 Hasta luego![/cyan]")
        self.running = False
    
    def _cmd_clear(self, *args) -> None:
        """Limpia la pantalla."""
        self.console.clear()
        self._print_banner()
    
    def _cmd_model(self, *args) -> None:
        """Cambia o muestra proveedor."""
        if args:
            model_name = args[0]
            try:
                from src.providers import set_default_provider
                
                self.provider = ProviderFactory.create(model_name)
                set_default_provider(self.provider, model_name)
                self.console.print(f"[green]✅ Proveedor cambiado a: {model_name}[/green]")
            except Exception as e:
                self.console.print(f"[red]❌ Error: {e}[/red]")
        else:
            name = self.provider.name
            models = self.provider.get_available_models()
            self.console.print(f"Proveedor actual: [cyan]{name}[/cyan]")
            if models:
                self.console.print(f"Modelos disponibles: {', '.join(models[:5])}")
    
    def _cmd_tools(self, *args) -> None:
        """Lista herramientas."""
        tools = list_all_tools()
        
        self.console.print("[bold]Herramientas disponibles:[/bold]")
        for tool in tools:
            self.console.print(f"  • {tool['name']}: {tool['description']}")
    
    def _cmd_history(self, *args) -> None:
        """Muestra historial."""
        messages = self.memory.get_messages(self.session_id)
        
        if not messages:
            self.console.print("[yellow]No hay mensajes en esta sesión.[/yellow]")
            return
        
        self.console.print(f"[bold]Historial (últimos {len(messages)} mensajes):[/bold]")
        for msg in messages[-10:]:
            role = msg["role"]
            content = msg["content"][:100]
            color = "green" if role == "user" else "blue" if role == "assistant" else "yellow"
            self.console.print(f"  [{color}]{role}[/{color}]: {content}...")
    
    def _cmd_session(self, *args) -> None:
        """Cambia sesión."""
        if args:
            try:
                new_session_id = int(args[0])
                self.session_id = self.memory.get_or_create_session(new_session_id)
                self.console.print(f"[green]✅ Cambiado a sesión: {new_session_id}[/green]")
            except ValueError:
                self.console.print("[red]❌ ID de sesión inválido[/red]")
        else:
            sessions = self.memory.get_sessions()
            
            self.console.print("[bold]Sesiones recientes:[/bold]")
            for s in sessions[:5]:
                active = "●" if s["id"] == self.session_id else "○"
                self.console.print(f"  {active} Sesión {s['id']} - {s['last_active'][:19]}")
    
    def _cmd_reload(self, *args) -> None:
        """Recarga configuración."""
        reload_config()
        self.console.print("[green]✅ Configuración recargada[/green]")
    
    def _cmd_run(self, *args) -> None:
        """Ejecuta el agente autonomo."""
        if not args:
            self.console.print("[red]Uso: /run <objetivo>[/red]")
            return
        
        goal = " ".join(args)
        from src.agent import HermesAgent
        
        self.console.print(Panel(f"[bold cyan]Ejecutando:[/bold cyan] {goal}", border_style="cyan"))
        
        try:
            agent = HermesAgent(provider=self.provider, verbose=True)
            result = agent.run(goal)
            self.console.print(Panel(result, border_style="green", title="Resultado final"))
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")


    def _chat(self, user_input: str) -> None:
        """Envía mensaje al LLM."""
        # Agregar mensaje del usuario
        self.memory.add_message(
            self.session_id,
            "user",
            user_input,
            self.provider.name
        )
        
        # Obtener mensajes del historial
        messages = self.memory.get_messages(self.session_id)
        
        # Convertir a formato para LLM
        llm_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
        
        # Enviar al LLM
        try:
            response = self.provider.chat(llm_messages)
            
            # Agregar respuesta
            self.memory.add_message(
                self.session_id,
                "assistant",
                response,
                self.provider.name
            )
            
            # Mostrar respuesta
            self.console.print(Panel(response, border_style="blue"))
        
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            self.console.print(f"[red]{error_msg}[/red]")


def main():
    """Entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agente Hermes CLI")
    parser.add_argument("--session", type=int, help="ID de sesión")
    args = parser.parse_args()
    
    cli = HermesCLI(session_id=args.session)
    cli.run()


if __name__ == "__main__":
    main()