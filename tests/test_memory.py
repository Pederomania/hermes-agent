"""Tests para memoria."""
import pytest
import tempfile
from pathlib import Path

from src.memory.db import Memory


@pytest.fixture
def memory():
    """Fixture para memoria."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Memory(db_path=Path(tmpdir) / "test.db")


def test_create_session(memory):
    """Testea creación de sesión."""
    session_id = memory.create_session()
    assert session_id > 0


def test_add_message(memory):
    """Testea agregar mensaje."""
    session_id = memory.create_session()
    msg_id = memory.add_message(session_id, "user", "Hola")
    assert msg_id > 0


def test_get_messages(memory):
    """Testea obtener mensajes."""
    session_id = memory.create_session()
    memory.add_message(session_id, "user", "Hola")
    memory.add_message(session_id, "assistant", "Hola!")
    
    messages = memory.get_messages(session_id)
    assert len(messages) == 2
    assert messages[0]["content"] == "Hola"
    assert messages[1]["content"] == "Hola!"


def test_get_sessions(memory):
    """Testea obtener sesiones."""
    session_id = memory.create_session()
    memory.add_message(session_id, "user", "Hola")
    
    sessions = memory.get_sessions()
    assert len(sessions) > 0


def test_summarize_messages(memory):
    """Testea resumen de mensajes."""
    messages = [{"role": "user", "content": f"Message {i}"} for i in range(15)]
    summary = memory.summarize_messages(messages)
    assert summary != "" or len(messages) <= 10