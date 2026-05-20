"""Sistema de memoria SQLite."""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


class Memory:
    """Sistema de memoria conversacional."""
    
    def __init__(self, db_path: str | Path | None = None):
        if db_path is None:
            db_path = Path.cwd() / "memory" / "history.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self) -> None:
        """Inicializa la base de datos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de sesiones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                provider TEXT DEFAULT 'ollama',
                goal TEXT,
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        # Tabla de mensajes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                provider_used TEXT,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # Tabla de acciones (HERMES STYLE)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                goal TEXT NOT NULL,
                step INTEGER NOT NULL,
                thought TEXT,
                action TEXT NOT NULL,
                args TEXT,
                result TEXT,
                success BOOLEAN,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # Tabla de goals
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                goal TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(self, provider: str = "ollama") -> int:
        """Crea una nueva sesión."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO sessions (provider) VALUES (?)",
            (provider,)
        )
        session_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def add_message(
        self,
        session_id: int,
        role: str,
        content: str,
        provider: str | None = None,
        metadata: dict | None = None
    ) -> int:
        """Agrega un mensaje a la sesión."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO messages (session_id, role, content, provider_used, metadata) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, content, provider, json.dumps(metadata or {}))
        )
        message_id = cursor.lastrowid
        
        # Actualizar last_active
        cursor.execute(
            "UPDATE sessions SET last_active = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,)
        )
        
        conn.commit()
        conn.close()
        
        return message_id
    
    def get_messages(self, session_id: int, limit: int = 100) -> list[dict]:
        """Obtiene mensajes de una sesión."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, role, content, timestamp, provider_used, metadata 
            FROM messages 
            WHERE session_id = ? 
            ORDER BY timestamp ASC 
            LIMIT ?
            """,
            (session_id, limit)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "role": row[1],
                "content": row[2],
                "timestamp": row[3],
                "provider": row[4],
                "metadata": json.loads(row[5] or "{}")
            }
            for row in rows
        ]
    
    def get_sessions(self, limit: int = 10) -> list[dict]:
        """Lista sesiones recientes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, created_at, last_active, provider, metadata 
            FROM sessions 
            ORDER BY last_active DESC 
            LIMIT ?
            """,
            (limit,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "created_at": row[1],
                "last_active": row[2],
                "provider": row[3],
                "metadata": json.loads(row[4] or "{}")
            }
            for row in rows
        ]
    
    def get_or_create_session(self, session_id: int | None = None) -> int:
        """Obtiene o crea una sesión."""
        if session_id is None:
            return self.create_session()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM sessions WHERE id = ?", (session_id,))
        if cursor.fetchone() is None:
            session_id = self.create_session()
        
        conn.close()
        return session_id
    
    def summarize_messages(self, messages: list[dict]) -> str:
        """Resume mensajes para contexto."""
        if len(messages) <= 10:
            return ""
        
        # Usar los primeros y últimos mensajes
        summary_parts = []
        
        if len(messages) > 2:
            first_msgs = messages[:2]
            summary_parts.append("[Resumen de mensajes iniciales]")
            for msg in first_msgs:
                summary_parts.append(f"{msg['role']}: {msg['content'][:100]}...")
        
        if len(messages) > 4:
            last_msgs = messages[-2:]
            summary_parts.append("[Resumen de mensajes recientes]")
            for msg in last_msgs:
                summary_parts.append(f"{msg['role']}: {msg['content'][:100]}...")
        
        return "\n".join(summary_parts)
    
    def delete_session(self, session_id: int) -> None:
        """Elimina una sesión."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM actions WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM goals WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        
        conn.commit()
        conn.close()
    
    # ===== HERMES STYLE: Actions & Goals =====
    
    def log_action(
        self,
        session_id: int,
        goal: str,
        step: int,
        thought: str,
        action: str,
        args: dict,
        result: str,
        success: bool
    ) -> int:
        """Loggea una acción (estilo Hermes)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO actions 
            (session_id, goal, step, thought, action, args, result, success) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, goal, step, thought, action, json.dumps(args), result, success)
        )
        
        action_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return action_id
    
    def get_actions(self, session_id: int, limit: int = 100) -> list[dict]:
        """Obtiene historial de acciones."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, goal, step, thought, action, args, result, success, timestamp
            FROM actions 
            WHERE session_id = ? 
            ORDER BY step ASC 
            LIMIT ?""",
            (session_id, limit)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "goal": row[1],
                "step": row[2],
                "thought": row[3],
                "action": row[4],
                "args": json.loads(row[5] or "{}"),
                "result": row[6],
                "success": row[7],
                "timestamp": row[8]
            }
            for row in rows
        ]
    
    def create_goal(self, session_id: int, goal: str) -> int:
        """Crea un nuevo goal."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO goals (session_id, goal) VALUES (?, ?)",
            (session_id, goal)
        )
        
        goal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return goal_id
    
    def complete_goal(self, goal_id: int) -> None:
        """Marca un goal como completado."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """UPDATE goals 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP 
            WHERE id = ?""",
            (goal_id,)
        )
        
        conn.commit()
        conn.close()


# Instancia global
_memory: Memory | None = None


def get_memory(db_path: str | Path | None = None) -> Memory:
    """Obtiene la instancia global de memoria."""
    global _memory
    if _memory is None:
        _memory = Memory(db_path)
    return _memory