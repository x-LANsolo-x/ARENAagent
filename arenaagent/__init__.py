"""ArenaAgent - Free AI coding assistant using LM Arena.

A powerful, local-first AI coding assistant that uses LM Arena's free API
for intelligent code generation, debugging, and assistance.
"""

__version__ = "0.1.0"
__author__ = "ArenaAgent Team"
__license__ = "MIT"

# Core models are available - other components will be added in later phases
from arenaagent.models import Message, Conversation, CodeChange, ExecutionResult

__all__ = [
    "Message",
    "Conversation",
    "CodeChange",
    "ExecutionResult",
]
