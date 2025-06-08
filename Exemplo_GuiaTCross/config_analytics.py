"""
Configuração do Google Analytics para o T-Cross Assistant

Para configurar o Google Analytics:
1. Acesse https://analytics.google.com/
2. Crie uma nova propriedade GA4
3. Obtenha seu ID de medição (formato: G-XXXXXXXXXX)
4. Substitua o valor de GOOGLE_ANALYTICS_ID abaixo
5. Configure os segredos no Streamlit Cloud se estiver usando
"""

# Configuração do Google Analytics 4 (GA4)
# Substitua "G-XXXXXXXXXX" pelo seu ID real do Google Analytics
GOOGLE_ANALYTICS_ID = "G-TF6PYQCV15"

# Configurações de debug (apenas para desenvolvimento)
ANALYTICS_DEBUG = False

# Eventos customizados que são rastreados
TRACKED_EVENTS = {
    "page_view": "Visualização de página inicial",
    "message_sent": "Envio de mensagem do usuário", 
    "ai_response_received": "Resposta da IA recebida",
    "vehicle_selected": "Seleção de veículo (ano/versão)",
    "new_conversation": "Nova conversa iniciada",
    "conversation_cleared": "Conversa limpa",
    "error_occurred": "Erro na aplicação"
}

# Configurações de desenvolvimento
DEV_CONFIG = {
    "show_debug_panel": False,  # Mostrar painel de debug do analytics
    "log_events_to_console": False,  # Logar eventos no console
    "track_in_development": True  # Rastrear eventos em desenvolvimento
}

def get_analytics_id():
    """Retorna o ID do Google Analytics configurado"""
    return GOOGLE_ANALYTICS_ID

def is_analytics_enabled():
    """Verifica se o analytics está configurado corretamente"""
    return GOOGLE_ANALYTICS_ID and GOOGLE_ANALYTICS_ID != "G-XXXXXXXXXX"

def get_tracked_events():
    """Retorna lista de eventos rastreados"""
    return TRACKED_EVENTS

def should_show_debug():
    """Verifica se deve mostrar informações de debug"""
    return ANALYTICS_DEBUG or DEV_CONFIG["show_debug_panel"] 