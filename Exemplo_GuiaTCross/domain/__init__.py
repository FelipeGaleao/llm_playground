"""
Domain Layer - Entidades de negócio
Seguindo princípios de Clean Architecture
"""

from .entities import Message, ChatSession, MessageRole, AIModelConfig

__all__ = ['Message', 'ChatSession', 'MessageRole', 'AIModelConfig'] 