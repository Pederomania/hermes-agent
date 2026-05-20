"""Agent loop principal tipo Hermes."""
import json
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import get_config
from src.memory.db import get_memory
from src.planner import Planner, get_planner
from src.executor import Executor, get_executor
from src.evaluator import Evaluator, get_evaluator

console = Console()


class HermesAgent:
    """
    Agente autónomo tipo Hermes.
    
    Loop real:
    1. goal → planner.decide() → action
    2. action → executor.execute() → result
    3. result → evaluator.evaluate() → feedback
    4. feedback → memory.log() → continue?
    """
    
    def __init__(
        self,
        provider=None,
        max_iterations: int = 10,
        verbose: bool = True
    ):
        self.provider = provider
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        # Components
        self.memory = get_memory()
        self.planner = get_planner(provider, self.memory)
        self.executor = get_executor()
        self.evaluator = get_evaluator(provider)
        
        self.session_id = self.memory.create_session("hermes-agent")
        
        # State
        self.running = False
    
    def run(self, goal: str) -> str:
        """
        Ejecuta el loop de agente.
        
        Args:
            goal: Goal a cumplir
        
        Returns:
            Resultado final
        """
        self.running = True
        iteration = 0
        last_result = ""
        context = ""
        
        console.print(f"Goal: {goal}")
        
        while self.running and iteration < self.max_iterations:
            iteration += 1
            
            if self.verbose:
                console.print(f"\n--- Iteracion {iteration}/{self.max_iterations} ---")
            
            # 1. PLAN
            if self.verbose:
                console.print("Planner decidiendo...")
            
            plan = self.planner.plan(goal, context, last_result)
            
            thought = plan.get("thought", "")[:100]
            action = plan.get("action", "echo")
            args = plan.get("args", {})
            
            if self.verbose:
                console.print(f"Thought: {thought}")
                console.print(f"Action: {action}({args})")
            
            # Log action
            self.memory.add_message(
                self.session_id,
                "assistant",
                f"Plan: {action}({args})",
                "planner"
            )
            
            # 2. EXECUTE
            if self.verbose:
                console.print("Ejecutando...")
            
            try:
                result = self.executor.execute(action, args)
            except Exception as e:
                result = f"Error: {str(e)}"
            
            if self.verbose:
                console.print(f"Result: {result[:200]}...")
            
            last_result = result
            
            # Log result
            self.memory.add_message(
                self.session_id,
                "assistant",
                f"Result: {result[:500]}",
                "executor"
            )
            
            # 3. EVALUATE
            if self.verbose:
                console.print("Evaluando...")
            
            eval_result = self.evaluator.evaluate(goal, action, result)
            success = eval_result.get("success", False)
            feedback = eval_result.get("feedback", "")
            
            if self.verbose:
                console.print(f"Feedback: {feedback}")
            
            # Check if done
            if success:
                if self.verbose:
                    console.print("Goal cumplido!")
                self.running = False
                break
            
            # Update context (acumular)
            context += f"[Iter {iteration}] {action}: {result[:150]}\n"
            
            # Check if should continue
            if not self.planner.should_continue(goal, result):
                if self.verbose:
                    console.print("Planner indica detener")
                self.running = False
        
        if iteration >= self.max_iterations:
            console.print(f"Max iteraciones alcanzado ({self.max_iterations})")
        
        return last_result
    
    def stop(self) -> None:
        """Detiene el agente."""
        self.running = False


# Instancia global
_agent: HermesAgent | None = None


def get_agent(provider=None) -> HermesAgent:
    """Obtiene el agente."""
    global _agent
    if _agent is None:
        _agent = HermesAgent(provider)
    return _agent


def run_agent(goal: str, provider=None) -> str:
    """Helper para ejecutar el agente."""
    agent = get_agent(provider)
    return agent.run(goal)