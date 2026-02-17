"""
ArenaAgent - Free AI Coding Assistant using LM Arena

A local Python CLI application that connects to LM Arena via persistent browser 
automation, maintains full conversation and execution context locally, executes 
code autonomously, and handles errors through model feedback loops.
"""

__version__ = "0.1.0"
__author__ = "ArenaAgent Team"
__license__ = "MIT"

from arenaagent.core.agent import AgentCore

__all__ = ["AgentCore"]
