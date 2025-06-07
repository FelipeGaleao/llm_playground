# 🚗 Guia VW T-Cross - Assistente Virtual

Assistente virtual especializado no VW T-Cross construído com **Clean Architecture**.

## 🚀 Como Executar

### Opção 1: Usando o main.py
```bash
cd Exemplo_GuiaTCross
python main.py
```

### Opção 2: Diretamente com Streamlit
```bash
cd Exemplo_GuiaTCross
streamlit run ui/streamlit.py
```

### Opção 3: Com uv (recomendado)
```bash
cd Exemplo_GuiaTCross
uv run streamlit run ui/streamlit.py
```

## 💬 Exemplos de Perguntas

- "Qual o consumo do T-Cross?"
- "Quais são as versões disponíveis?"  
- "Qual o preço da versão Highline?"
- "Como é a manutenção?"
- "Ficha técnica completa"

## 🏗️ Estrutura Clean Architecture

```
📁 domain/     - Entidades de negócio
📁 use_cases/  - Casos de uso
📁 adapters/   - Interface adapters
📁 ui/         - Interface Streamlit
```

## 🎯 Funcionalidades

- ✅ Chat especializado em VW T-Cross
- ✅ Interface simples e focada
- ✅ Estatísticas da conversa
- ✅ Arquitetura limpa e extensível
