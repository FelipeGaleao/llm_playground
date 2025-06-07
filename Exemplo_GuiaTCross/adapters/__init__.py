"""
Adapters Layer - Interface Adapters
Seguindo princípios de Clean Architecture
"""

from .adapter import AIService, OpenAIAdapter, ClaudeAdapter, ai_service

__all__ = ['AIService', 'OpenAIAdapter', 'ClaudeAdapter', 'ai_service'] 