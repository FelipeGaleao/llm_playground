"""
Use Cases da aplicação
Seguindo princípios de Clean Architecture
"""
import uuid
from datetime import datetime
from typing import List, Optional
from .entities import Message, ChatSession, MessageRole, AIModelConfig
from .adapter import AIService


class ChatUseCase:
    """Use Case para gerenciar operações de chat"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.current_session: Optional[ChatSession] = None
    
    def start_new_session(self, model: str) -> ChatSession:
        """Inicia uma nova sessão de chat"""
        session_id = str(uuid.uuid4())
        self.current_session = ChatSession(
            id=session_id,
            messages=[],
            created_at=datetime.now(),
            model=model
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


class ModelConfigUseCase:
    """Use Case para gerenciar configurações de modelos"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.configs: List[AIModelConfig] = []
        self._setup_default_configs()
    
    def _setup_default_configs(self):
        """Configura os modelos padrão"""
        models = self.ai_service.get_all_models()
        
        for provider, model_list in models.items():
            for model in model_list:
                config = AIModelConfig(
                    name=model,
                    provider=provider,
                    description=f"Modelo {model} do provedor {provider}"
                )
                self.configs.append(config)
    
    def get_available_configs(self) -> List[AIModelConfig]:
        """Retorna todas as configurações disponíveis"""
        return self.configs
    
    def get_config_by_name(self, name: str) -> Optional[AIModelConfig]:
        """Busca configuração por nome do modelo"""
        for config in self.configs:
            if config.name == name:
                return config
        return None
    
    def update_config(self, name: str, temperature: float, 
                     max_tokens: int) -> bool:
        """Atualiza configuração de um modelo"""
        config = self.get_config_by_name(name)
        if config:
            config.temperature = temperature
            config.max_tokens = max_tokens
            return True
        return False


class ExportUseCase:
    """Use Case para exportar dados da conversa"""
    
    def export_session_to_dict(self, session: ChatSession) -> dict:
        """Exporta uma sessão para dicionário"""
        return session.to_dict()
    
    def export_session_to_json(self, session: ChatSession) -> str:
        """Exporta uma sessão para JSON"""
        import json
        return json.dumps(session.to_dict(), indent=2, ensure_ascii=False)
    
    def import_session_from_dict(self, data: dict) -> ChatSession:
        """Importa uma sessão a partir de dicionário"""
        return ChatSession.from_dict(data)


# Factory para criar instâncias dos use cases
class UseCaseFactory:
    """Factory para criar use cases com dependências"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    def create_chat_use_case(self) -> ChatUseCase:
        """Cria use case de chat"""
        return ChatUseCase(self.ai_service)
    
    def create_model_config_use_case(self) -> ModelConfigUseCase:
        """Cria use case de configuração de modelo"""
        return ModelConfigUseCase(self.ai_service)
    
    def create_export_use_case(self) -> ExportUseCase:
        """Cria use case de exportação"""
        return ExportUseCase() 