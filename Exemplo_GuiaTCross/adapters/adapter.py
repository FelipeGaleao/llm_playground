"""
Adapter para comunicação com APIs de IA
Seguindo princípios de Clean Architecture
"""
import time
import random
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


class AIProviderInterface(ABC):
    """Interface abstrata para provedores de IA"""
    
    @abstractmethod
    def generate_response(self, message: str, model: str) -> str:
        """Gera uma resposta baseada na mensagem do usuário"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Retorna lista de modelos disponíveis"""
        pass


class OpenAIAdapter(AIProviderInterface):
    """Adapter para OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.available_models = [
            "GPT-3.5-turbo", 
            "GPT-4", 
            "GPT-4-turbo"
        ]
    
    def generate_response(self, message: str, model: str) -> str:
        """
        Gera resposta usando OpenAI API
        Por enquanto simula a resposta para demonstração
        """
        # Simula tempo de processamento da API
        time.sleep(random.uniform(0.5, 2.0))
        
        # Aqui você integraria com a OpenAI API real
        # import openai
        # response = openai.ChatCompletion.create(...)
        
        return self._simulate_openai_response(message, model)
    
    def get_available_models(self) -> List[str]:
        """Retorna modelos disponíveis da OpenAI"""
        return self.available_models
    
    def _simulate_openai_response(self, message: str, model: str) -> str:
        """Simula resposta da OpenAI para demonstração"""
        
        # Respostas específicas para o contexto do VW T-Cross
        tcross_responses = {
            "consumo": (
                "O VW T-Cross tem consumo médio de 14,5 km/l na cidade "
                "e 16,2 km/l na estrada com motor 1.0 TSI. "
                "Com motor 1.4 TSI, o consumo é de 13,8 km/l cidade "
                "e 15,1 km/l estrada."
            ),
            "preço": (
                "O preço do VW T-Cross varia de R$ 85.000 a R$ 130.000, "
                "dependendo da versão (Sense, Comfortline, Highline). "
                "Consulte uma concessionária para valores atualizados."
            ),
            "ficha técnica": (
                "VW T-Cross principais especificações:\n"
                "- Motores: 1.0 TSI (128cv) ou 1.4 TSI (150cv)\n"
                "- Transmissão: Manual 6 marchas ou automática 6 marchas\n"
                "- Comprimento: 4,19m\n"
                "- Porta-malas: 420 litros"
            ),
            "versões": (
                "O VW T-Cross tem 3 versões principais:\n"
                "• Sense: versão de entrada\n"
                "• Comfortline: versão intermediária\n"
                "• Highline: versão top de linha\n"
                "Cada uma com diferentes níveis de equipamentos."
            ),
            "manutenção": (
                "A manutenção do VW T-Cross deve ser feita a cada "
                "10.000 km ou 12 meses. O custo médio das revisões "
                "varia entre R$ 400 a R$ 800, dependendo do tipo "
                "de serviço necessário."
            )
        }
        
        # Verifica se a pergunta é sobre o T-Cross
        message_lower = message.lower()
        for key, response in tcross_responses.items():
            if key in message_lower:
                return f"[{model}] {response}"
        
        # Respostas genéricas
        generic_responses = [
            (f"Como {model}, posso ajudar com informações sobre o "
             f"VW T-Cross. Você gostaria de saber sobre consumo, "
             f"preço, versões ou manutenção?"),
            (f"Baseado no {model}, posso fornecer detalhes técnicos "
             f"e práticos sobre o VW T-Cross. O que especificamente "
             f"você gostaria de saber?"),
            (f"Usando {model}, posso esclarecer suas dúvidas sobre "
             f"o VW T-Cross. Pergunte sobre características, "
             f"desempenho ou qualquer aspecto do veículo.")
        ]
        
        return random.choice(generic_responses)


class ClaudeAdapter(AIProviderInterface):
    """Adapter para Claude API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.available_models = ["Claude-3", "Claude-3-Sonnet", "Claude-3-Opus"]
    
    def generate_response(self, message: str, model: str) -> str:
        """Gera resposta usando Claude API"""
        time.sleep(random.uniform(0.3, 1.5))
        return f"[{model}] Resposta simulada do Claude para: {message}"
    
    def get_available_models(self) -> List[str]:
        return self.available_models


class AIService:
    """Serviço principal para gerenciar diferentes provedores de IA"""
    
    def __init__(self):
        self.providers: Dict[str, AIProviderInterface] = {
            "openai": OpenAIAdapter(),
            "claude": ClaudeAdapter()
        }
        self.current_provider = "openai"
    
    def set_provider(self, provider_name: str):
        """Define o provedor de IA atual"""
        if provider_name in self.providers:
            self.current_provider = provider_name
        else:
            raise ValueError(f"Provedor {provider_name} não disponível")
    
    def get_response(self, message: str, model: str) -> str:
        """Obtém resposta do provedor atual"""
        provider = self.providers[self.current_provider]
        return provider.generate_response(message, model)
    
    def get_available_models(self) -> List[str]:
        """Retorna modelos disponíveis do provedor atual"""
        provider = self.providers[self.current_provider]
        return provider.get_available_models()
    
    def get_all_models(self) -> Dict[str, List[str]]:
        """Retorna todos os modelos de todos os provedores"""
        all_models = {}
        for name, provider in self.providers.items():
            all_models[name] = provider.get_available_models()
        return all_models


# Instância singleton do serviço
ai_service = AIService() 