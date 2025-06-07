"""
Entidades do domínio da aplicação
Seguindo princípios de Clean Architecture
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum


class MessageRole(Enum):
    """Enum para definir os tipos de mensagem"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """Entidade que representa uma mensagem no chat"""
    role: MessageRole
    content: str
    timestamp: datetime
    model_used: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Converte a mensagem para dicionário"""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "model_used": self.model_used
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Cria uma mensagem a partir de um dicionário"""
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            model_used=data.get("model_used")
        )


@dataclass
class ChatSession:
    """Entidade que representa uma sessão de chat"""
    id: str
    messages: List[Message]
    created_at: datetime
    model: str
    title: Optional[str] = None
    
    def add_message(self, message: Message):
        """Adiciona uma mensagem à sessão"""
        self.messages.append(message)
    
    def get_user_messages_count(self) -> int:
        """Retorna quantidade de mensagens do usuário"""
        return len([m for m in self.messages if m.role == MessageRole.USER])
    
    def get_assistant_messages_count(self) -> int:
        """Retorna quantidade de mensagens do assistente"""
        return len([m for m in self.messages 
                   if m.role == MessageRole.ASSISTANT])
    
    def get_total_characters(self) -> int:
        """Retorna total de caracteres na conversa"""
        return sum(len(m.content) for m in self.messages)
    
    def to_dict(self) -> dict:
        """Converte a sessão para dicionário"""
        return {
            "id": self.id,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at.isoformat(),
            "model": self.model,
            "title": self.title
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChatSession':
        """Cria uma sessão a partir de um dicionário"""
        return cls(
            id=data["id"],
            messages=[Message.from_dict(m) for m in data["messages"]],
            created_at=datetime.fromisoformat(data["created_at"]),
            model=data["model"],
            title=data.get("title")
        )


@dataclass
class AIModelConfig:
    """Configuração de um modelo de IA"""
    name: str
    provider: str
    temperature: float = 0.7
    max_tokens: int = 2048
    description: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Converte a configuração para dicionário"""
        return {
            "name": self.name,
            "provider": self.provider,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "description": self.description
        } 