"""
Interface Streamlit para o Guia do VW T-Cross
Seguindo princípios de Clean Architecture - UI Layer
"""
import streamlit as st
from adapters import ai_service
from use_cases import UseCaseFactory
from domain import MessageRole


# Configuração da página
st.set_page_config(
    page_title="Guia VW T-Cross",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado
st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF !important;
        font-family: 'Arial', sans-serif;
        color: #000000;
    }
    
    /* Override dark mode */
    .stApp > div {
        background-color: #FFFFFF !important;
    }
    
    /* Header da Volkswagen */
    .vw-header {
        background: linear-gradient(135deg, #005ea6 0%, #0073cc 100%);
        padding: 1.5rem;
        margin-bottom: 2rem;
        border-radius: 12px;
        text-align: center;
        color: white;
    }
    
    .vw-title {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .vw-subtitle {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: flex-start;
    }
    
    .chat-message.user {
        background: #005ea6;
        color: white;
        margin-left: 2rem;
    }
    
    .chat-message.assistant {
        background: #f8f9fa;
        color: #2c3e50;
        margin-right: 2rem;
        border-left: 4px solid #005ea6;
    }
    
    .chat-message .avatar {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        margin-right: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    .user .avatar {
        background: rgba(255, 255, 255, 0.2);
        color: white;
    }
    
    .assistant .avatar {
        background: #005ea6;
        color: white;
    }
    
    .message-content {
        flex: 1;
        line-height: 1.6;
    }
    
    /* Welcome Message */
    .welcome-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 12px;
        margin: 2rem 0;
        text-align: center;
        border: 2px solid #005ea6;
    }
    
    /* Buttons */
    .stButton > button {
        background: #005ea6 !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        min-width: 100px !important;
        width: 100% !important;
        white-space: nowrap !important;
        font-size: 1rem !important;
    }
    
    .stButton > button:hover {
        background: #004080 !important;
    }
    
    /* Input */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        padding: 0.75rem !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa !important;
    }
    
    /* Info cards styling */
    .stAlert > div {
        background-color: #e3f2fd !important;
        border-left: 4px solid #005ea6 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        color: #2c3e50 !important;
    }
    [data-testid="stSidebarContent"] {
        background-color: #e3f2fd !important;
        color: #2c3e50 !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #005ea6 !important;
        color: #005ea6 !important;
        border-radius: 0.5rem;
        width: 2rem;
        height: 2rem;
    }
    [data-testid="stHeadingWithActionElements"] {
        color: #005ea6 !important;
    }
    .st-br {
        background-color:   !important;
    }
    .st-bq {
        border-bottom-color:   !important;
    }
    .st-bp {
        border-top-color:   !important;
    }
    .st-bo {
        border-right-color:   !important;
    }
    [data-testid="stBaseButton-headerNoPadding"] {
        background-color: #005ea6 !important;
        color: white;
    }
    .stAlert [data-testid="alertIndicator"] {
        color: #005ea6 !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Force light theme */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff !important;
    }
    
    /* Responsive layout */
    @media (max-width: 768px) {
        .stButton > button {
            min-width: 80px !important;
            font-size: 0.9rem !important;
            padding: 0.5rem 1rem !important;
        }
    }
    
    /* Selectboxes styling */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox > div > div > div {
        color: #2c3e50 !important;
    }
</style>
""", unsafe_allow_html=True)


# Inicializar use cases
@st.cache_resource
def get_use_case_factory():
    """Cria e retorna factory de use cases"""
    return UseCaseFactory(ai_service)


def initialize_session_state():
    """Inicializa o estado da sessão do Streamlit"""
    if "chat_use_case" not in st.session_state:
        factory = get_use_case_factory()
        st.session_state.chat_use_case = factory.create_chat_use_case()
    
    # Inicia sessão se não existir
    if not st.session_state.chat_use_case.get_current_session():
        st.session_state.chat_use_case.start_new_session()


def display_message(role: str, content: str, avatar: str):
    """Exibe uma mensagem no chat"""
    message_class = "user" if role == "user" else "assistant"
    
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="avatar">{avatar}</div>
        <div class="message-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Renderiza a sidebar simplificada"""
    with st.sidebar:
        st.title("🚗 Guia VW T-Cross")
        
        st.markdown("---")
        
        # Controles da conversa
        st.subheader("💬 Controles")
        
        if st.button("➕ Nova Conversa"):
            st.session_state.chat_use_case.start_new_session()
            st.rerun()
        
        if st.button("🗑️ Limpar Conversa"):
            st.session_state.chat_use_case.clear_session()
            st.session_state.chat_use_case.start_new_session()
            st.rerun()
        
        # Estatísticas
        stats = st.session_state.chat_use_case.get_session_stats()
        if stats["user_messages"] > 0:
            st.markdown("---")
            st.subheader("📊 Estatísticas")
            st.metric("Suas Perguntas", stats["user_messages"])
            st.metric("Respostas da IA", stats["ai_messages"])
            st.metric("Total de Caracteres", stats["total_characters"])


def render_main_chat():
    """Renderiza a área principal do chat"""
    # Cabeçalho da Volkswagen
    st.markdown("""
    <div class="vw-header">
        <div class="vw-title">🚗 T-Cross Assistant</div>
        <div class="vw-subtitle">Seu assistente virtual especializado no VW T-Cross</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Container para mensagens
    chat_container = st.container()
    
    current_session = st.session_state.chat_use_case.get_current_session()
    
    with chat_container:
        if not current_session or not current_session.messages:
            # Mensagem de boas-vindas simplificada
            st.markdown("""
            <div class="welcome-box">
                <h2 style="color: #005ea6; margin-bottom: 1rem;">
                    🚗 Bem-vindo ao T-Cross Assistant!
                </h2>
                <p style="color: #6c757d; font-size: 1.1rem; margin-bottom: 2rem;">
                    Seu assistente virtual especializado no VW T-Cross
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Features usando colunas do Streamlit
            st.subheader("💡 O que posso te ajudar:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("""
                **⛽ Consumo de Combustível**
                
                Informações sobre economia
                """)
                
                st.info("""
                **🔧 Ficha Técnica**
                
                Especificações completas
                """)
            
            with col2:
                st.info("""
                **💰 Preços e Versões**
                
                Valores atualizados
                """)
                
                st.info("""
                **🛠️ Manutenção**
                
                Cuidados e revisões
                """)
                
        else:
            # Exibir mensagens existentes
            for message in current_session.messages:
                if message.role == MessageRole.USER:
                    display_message("user", message.content, "👤")
                else:
                    display_message("assistant", message.content, "🚗")


def render_input_area():
    """Renderiza a área de input do usuário"""
    st.markdown("---")
    
    # Seleção de ano e versão
    st.subheader("🚗 Configuração do Veículo")
    
    col_ano, col_versao = st.columns(2)
    
    with col_ano:
        ano = st.selectbox(
            "Ano do T-Cross:",
            ["2024", "2023", "2022", "2021", "2020", "2019"],
            index=0,
            key="ano_veiculo"
        )
    
    with col_versao:
        versao = st.selectbox(
            "Versão:",
            [
                "200 TSI Comfortline",
                "200 TSI Highline", 
                "250 TSI Highline",
                "1.0 TSI Sense",
                "1.6 Sense",
                "1.6 Comfortline"
            ],
            index=0,
            key="versao_veiculo"
        )
    
    # Exibir configuração selecionada
    st.info(f"🚗 **Configuração selecionada:** T-Cross {versao} {ano}")
    
    # Campo de pergunta
    st.subheader("💬 Sua Pergunta")
    
    col1, col2 = st.columns([6, 2])
    
    with col1:
        user_input = st.text_input(
            f"Faça sua pergunta sobre o T-Cross {versao} {ano}...",
            key="user_input",
            placeholder="Ex: Qual o consumo na cidade?",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button(
            "Enviar", 
            key="send_button", 
            use_container_width=True
        )
    
    return user_input, send_button, ano, versao


def process_user_message(user_input: str, ano: str, versao: str):
    """Processa a mensagem do usuário"""
    try:
        # Contexto adicional com ano e versão
        contexto = f"Veículo: VW T-Cross {versao} {ano}\nPergunta: {user_input}"
        
        # Enviar mensagem do usuário
        st.session_state.chat_use_case.send_message(user_input)
        
        # Obter resposta da IA com contexto adicional
        with st.spinner("🤖 Analisando sua pergunta..."):
            st.session_state.chat_use_case.get_ai_response(contexto)
        
        st.rerun()
        
    except Exception as e:
        st.error(f"Erro ao processar mensagem: {str(e)}")


def main():
    """Função principal da aplicação"""
    # Inicializar estado da sessão
    initialize_session_state()
    
    # Renderizar componentes
    render_sidebar()
    render_main_chat()
    
    # Área de input
    user_input, send_button, ano, versao = render_input_area()
    
    # Processar mensagem se enviada
    if send_button and user_input:
        process_user_message(user_input, ano, versao)
    
    # Informações na parte inferior
    st.markdown("---")
    st.info(
        "💡 **Como usar:** Digite sua pergunta e pressione Enter ou clique em Enviar\n\n"
        "🚗 **T-Cross Assistant** | 🤖 Powered by AI | **Volkswagen**"
    )


if __name__ == "__main__":
    main()
