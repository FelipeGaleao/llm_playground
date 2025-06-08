"""
Use Cases da aplicação
Seguindo princípios de Clean Architecture
"""
import uuid
from datetime import datetime
from typing import Optional
from domain.entities import Message, ChatSession, MessageRole
from adapters.adapter import AIService


class ChatUseCase:
    """Use Case para gerenciar operações de chat"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.current_session: Optional[ChatSession] = None
        self.default_model = "o1"  # Modelo fixo
    
    def start_new_session(self, model: str = None) -> ChatSession:
        """Inicia uma nova sessão de chat"""
        session_id = str(uuid.uuid4())
        used_model = model or self.default_model
        self.current_session = ChatSession(
            id=session_id,
            messages=[],
            created_at=datetime.now(),
            model=used_model
        )
        return self.current_session
    
    def send_message(self, content: str) -> Message:
        """Envia uma mensagem do usuário"""
        if not self.current_session:
            raise ValueError("Nenhuma sessão ativa")
        
        # Criar mensagem do usuário
        user_message = Message(
            role=MessageRole.USER,
            content=content,
            timestamp=datetime.now()
        )
        
        # Adicionar à sessão
        self.current_session.add_message(user_message)
        
        return user_message
    
    def get_ai_response(self, user_message: str) -> Message:
        """Obtém resposta da IA para a mensagem do usuário"""
        if not self.current_session:
            raise ValueError("Nenhuma sessão ativa")
        
        # Obter resposta da IA
        ai_response_content = self.ai_service.get_response(
            user_message, self.current_session.model
        )
        
        # Criar mensagem da IA
        ai_message = Message(
            role=MessageRole.ASSISTANT,
            content=ai_response_content,
            timestamp=datetime.now(),
            model_used=self.current_session.model
        )
        
        # Adicionar à sessão
        self.current_session.add_message(ai_message)
        
        return ai_message
    
    def get_current_session(self) -> Optional[ChatSession]:
        """Retorna a sessão atual"""
        return self.current_session
    
    def clear_session(self):
        """Limpa a sessão atual"""
        self.current_session = None
    
    def get_session_stats(self) -> dict:
        """Retorna estatísticas da sessão atual"""
        if not self.current_session:
            return {
                "user_messages": 0,
                "ai_messages": 0,
                "total_characters": 0
            }
        
        return {
            "user_messages": self.current_session.get_user_messages_count(),
            "ai_messages": self.current_session.get_assistant_messages_count(),
            "total_characters": self.current_session.get_total_characters()
        }


# Factory para criar instâncias dos use cases
class UseCaseFactory:
    """Factory para criar use cases com dependências"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    def create_chat_use_case(self) -> ChatUseCase:
        """Cria use case de chat"""
        return ChatUseCase(self.ai_service) 