"""Framework de skills para el agente Hermes."""
import importlib
import importlib.util
import json
import os
import re
from pathlib import Path
from typing import Any


class Skill:
    """Skill cargable del agente."""
    
    def __init__(
        self,
        name: str,
        description: str,
        triggers: list[str],
        content: str,
        metadata: dict | None = None
    ):
        self.name = name
        self.description = description
        self.triggers = triggers
        self.content = content
        self.metadata = metadata or {}
    
    def matches(self, query: str) -> bool:
        """Verifica si la query coincide con los triggers."""
        query_lower = query.lower()
        return any(
            trigger.lower() in query_lower
            for trigger in self.triggers
        )
    
    def execute(self, context: dict) -> str:
        """Ejecuta el skill (placeholder -会被LLM调用)."""
        return self.content


class SkillLoader:
    """Cargador de skills."""
    
    def __init__(self, skills_dir: str | Path | None = None):
        if skills_dir is None:
            skills_dir = Path.cwd() / "skills"
        
        self.skills_dir = Path(skills_dir)
        self.skills: list[Skill] = []
    
    def load(self) -> None:
        """Carga todos los skills del directorio."""
        self.skills = []
        
        if not self.skills_dir.exists():
            return
        
        for item in self.skills_dir.iterdir():
            if item.suffix == ".md" and not item.name.startswith("_"):
                skill = self._load_skill(item)
                if skill:
                    self.skills.append(skill)
    
    def _load_skill(self, path: Path) -> Skill | None:
        """Carga un skill desde un archivo markdown."""
        try:
            with open(path) as f:
                content = f.read()
            
            # Parsear frontmatter si existe
            name = path.stem
            description = ""
            triggers = []
            metadata = {}
            
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    fm_text = parts[1].strip()
                    body = parts[2].strip()
                    
                    for line in fm_text.split("\n"):
                        if ":" in line:
                            key, value = line.split(":", 1)
                            key = key.strip()
                            value = value.strip()
                            
                            if key == "name":
                                name = value
                            elif key == "description":
                                description = value
                            elif key == "triggers":
                                triggers = json.loads(value) if value.startswith("[") else [value]
                            else:
                                metadata[key] = value
                    
                    content = body
            
            return Skill(
                name=name,
                description=description,
                triggers=triggers,
                content=content
            )
        
        except Exception as e:
            print(f"Error cargando skill {path}: {e}")
            return None
    
    def find_skill(self, query: str) -> Skill | None:
        """Encuentra un skill que coincida con la query."""
        for skill in self.skills:
            if skill.matches(query):
                return skill
        return None
    
    def list_skills(self) -> list[dict]:
        """Lista todos los skills."""
        return [
            {
                "name": s.name,
                "description": s.description,
                "triggers": s.triggers
            }
            for s in self.skills
        ]


# Instancia global
_skill_loader: SkillLoader | None = None


def get_skill_loader(skills_dir: str | Path | None = None) -> SkillLoader:
    """Obtiene el loader de skills."""
    global _skill_loader
    if _skill_loader is None:
        _skill_loader = SkillLoader(skills_dir)
        _skill_loader.load()
    return _skill_loader


def find_skill(query: str) -> Skill | None:
    """Encuentra un skill por query."""
    return get_skill_loader().find_skill(query)


def list_skills() -> list[dict]:
    """Lista todos los skills."""
    return get_skill_loader().list_skills()