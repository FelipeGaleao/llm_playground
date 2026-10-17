# LLM Playground

Playground de experimentos e estudos práticos com Modelos de Linguagem de Larga Escala (LLMs), frameworks de agentes e ferramentas de IA.

---

## 🎯 Objetivos do Repositório

Explorar, prototipar e avaliar aplicações modernas baseadas em LLMs:
- **AI Agents**: Agentes autônomos orientados a objetivos com capacidade de tomada de decisão e uso de ferramentas (*Tool Calling*).
- **Agent Evaluation (Evals)**: Avaliação de trajetórias de ferramentas, fidelidade e acurácia de respostas usando o Google GenAI ADK.
- **RAG (Retrieval-Augmented Generation)**: Geração de respostas baseadas em recuperação contextual de documentos e dados.
- **MCP (Model Context Protocol)**: Integração e automação de serviços externos e bases de dados padronizadas para modelos de IA.

---

## 📁 Estrutura de Projetos

- **[ADKCodeReviewer](ADKCodeReviewer/README.md)**: Agente autônomo baseado no **Google ADK** e **Gemini 2.5 Flash** capaz de varrer a base de código (`grep`), inspecionar arquivos, corrigir bugs e validar com testes automatizados, acompanhado de suíte de avaliação com *Evals*.
- **[TrafegoAereo](TrafegoAereo/)**: Agente e ferramentas especializadas para consulta de autorizações e informações de tráfego aéreo.
- **[AnaliseComentarios](AnaliseComentarios/)**: Notebooks e pipelines para análise semântica e classificação de comentários.
- **[RAG](RAG/)**: Implementações e estudos com recuperação aumentada por geração.
- **[Exemplo_GuiaTCross](Exemplo_GuiaTCross/)**: Demonstrações práticas e testes de assistência inteligente baseados em manuais e guias.
