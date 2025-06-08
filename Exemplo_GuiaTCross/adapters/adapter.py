"""
Adapter para comunicação com APIs de IA
Seguindo princípios de Clean Architecture
"""
import time
import random
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from pathlib import Path
from openai import OpenAI
import streamlit as st

# Importações para embeddings (opcionais)
try:
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
    print("Langchain está instalado")
except ImportError:
    print("Langchain não está instalado")
    LANGCHAIN_AVAILABLE = False


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
    """Adapter para OpenAI API com suporte a embeddings"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.available_models = [
            "o1"
        ]
        self.vector_store = None
        self.embeddings_cache_dir = Path("embeddings_cache")
        self.embeddings_cache_dir.mkdir(exist_ok=True)
        self.documents_dir = Path("documents")
        
        # Inicializa embeddings se LangChain estiver disponível
        if LANGCHAIN_AVAILABLE and api_key:
            self.embeddings = OpenAIEmbeddings(api_key=api_key)
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            self._load_or_create_embeddings()
    
    def _load_or_create_embeddings(self):
        """Cache inteligente: carrega embeddings existentes ou cria novos"""
        cache_path = self.embeddings_cache_dir / "tcross_embeddings"
        
        # Tenta carregar embeddings existentes
        if cache_path.exists():
            try:
                self.vector_store = FAISS.load_local(
                    str(cache_path), 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print("✅ Embeddings carregados do cache")
                return
            except Exception as e:
                print(f"⚠️ Erro ao carregar embeddings do cache: {e}")
        
        # Se não conseguir carregar, cria novos embeddings
        self._create_embeddings_from_txt_files()
    
    def _create_embeddings_from_txt_files(self):
        """Cria embeddings a partir de arquivos .txt na pasta documents"""
        if not self.documents_dir.exists():
            self.documents_dir.mkdir()
            print("📁 Pasta 'documents' criada. "
                  "Adicione arquivos .txt lá para usar embeddings.")
            return
        
        txt_files = list(self.documents_dir.glob("*.txt"))
        if not txt_files:
            print("📄 Nenhum arquivo .txt encontrado na pasta 'documents'")
            return
        
        # Carrega todos os documentos
        all_texts = []
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Adiciona metadados
                    filename = file_path.name
                    content_with_metadata = (f"[ARQUIVO: {filename}]\n"
                                           f"{content}")
                    
                    # Divide em chunks
                    chunks = self.text_splitter.split_text(
                        content_with_metadata)
                    all_texts.extend(chunks)
                    
                print(f"📖 Processado: {filename}")
            except Exception as e:
                print(f"❌ Erro ao processar {file_path}: {e}")
        
        if all_texts:
            try:
                # Cria vector store
                self.vector_store = FAISS.from_texts(
                    all_texts, self.embeddings)
                
                # Salva no cache
                cache_path = self.embeddings_cache_dir / "tcross_embeddings"
                self.vector_store.save_local(str(cache_path))
                
                print(f"✅ Embeddings criados com {len(all_texts)} chunks "
                      f"e salvos no cache")
            except Exception as e:
                print(f"❌ Erro ao criar embeddings: {e}")
    
    def _get_context_from_embeddings(self, message: str, k: int = 3) -> str:
        """Busca contexto relevante nos embeddings"""
        if not self.vector_store:
            return ""
        
        try:
            docs = self.vector_store.similarity_search(message, k=k)
            if docs:
                context_parts = [doc.page_content for doc in docs]
                return ("\n\nCONTEXTO DOS DOCUMENTOS:\n" + 
                        "\n---\n".join(context_parts))
        except Exception as e:
            print(f"⚠️ Erro na busca por similaridade: {e}")
        
        return ""
    
    def generate_response(self, message: str, model: str) -> str:
        """
        Gera resposta usando OpenAI API com contexto de embeddings
        """
        client = OpenAI(api_key=self.api_key)
        
        # Busca contexto relevante nos embeddings
        context = (self._get_context_from_embeddings(message) 
                   if LANGCHAIN_AVAILABLE else "")
        
        # Prepara mensagens do sistema
        messages = [
            {"role": "system", 
             "content": "Você é um engenheiro da Volkswagen que responde "
                        "perguntas sobre o VW T-Cross."},
            {"role": "system", 
             "content": f"O carro atualmente selecionado é um VW T-Cross "
                        f"{st.session_state.ano_veiculo} "
                        f"{st.session_state.versao_veiculo}"},
            {"role": "system", 
             "content": "Você deve responder apenas perguntas sobre o "
                        "VW T-Cross, caso seja sobre um outro carro ou um "
                        "outro contexto, diga que você não pode responder."}
        ]
        
        # Adiciona contexto dos documentos se disponível
        if context:
            messages.append({
                "role": "system", 
                "content": f"Use as informações dos documentos abaixo "
                           f"como referência para suas respostas:{context}"
                           f"Não responda nenhuma pergunta cujo a resposta não esteja no contexto dos documentos."
            })
        
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
        
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
        self.available_models = [
            "Claude-3", "Claude-3-Sonnet", "Claude-3-Opus"
        ]
    
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