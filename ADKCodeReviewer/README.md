# ADK Code Reviewer & Bug Fixing Agent

Agente autônomo de análise, depuração e correção de código desenvolvido com o **Google Agent Development Kit (ADK)** e **Gemini 2.5 Flash**.

---

## 📌 Visão Geral

O **CodeReviewer** é projetado para atuar como um assistente de engenharia de software autônomo. Em vez de depender do usuário para apontar caminhos exatos de arquivos ou linhas de código com defeito, o agente:
1. **Varre autonomamente** a base de código utilizando busca por padrões (`grep_search`) e listagem de diretório (`list_files`).
2. **Inspeciona e analisa** os arquivos suspeitos (`read_file`).
3. **Aplica as correções necessárias** com precisão (`write_file`).
4. **Executa a suíte de testes automatizados** (`run_tests`) para garantir que o bug foi corrigido sem quebrar funcionalidades existentes.

---

## 🛠️ Ferramentas Disponíveis ao Agente

As ferramentas estão implementadas em [`tools.py`](codereviewer/tools.py) e operam com segurança isoladas no diretório `workspace/`:

| Ferramenta | Descrição |
| :--- | :--- |
| `grep_search(pattern, path)` | Localiza definições, chamadas ou trechos de código em arquivos do workspace. |
| `list_files(directory)` | Lista recursivamente arquivos e pastas do workspace. |
| `read_file(file_path)` | Lê o conteúdo textual de um arquivo específico. |
| `write_file(file_path, content)` | Grava ou reescreve o conteúdo corrigido de um arquivo. |
| `run_tests(test_target)` | Roda a suíte de testes (com suporte a `pytest` e fallback para `unittest`). |

---

## 🧪 Avaliação e Benchmarking (Google ADK Evals)

O projeto conta com suíte de avaliação contínua em [`eval_set_1.evalset.json`](codereviewer/eval_set_1.evalset.json), testando a autonomia do agente em cenários reais:

- **Caso 1 (`caso_1_corrigir_bug_divisao_implicito`)**: Correção autônoma de bug matemático sem indicação prévia do nome do arquivo.
- **Caso 2 (`caso_2_buscar_funcao_sem_nome_de_arquivo`)**: Descoberta e explicação de função via varredura de código.
- **Caso 3 (`caso_3_execucao_direta_de_testes`)**: Execução direta e validação de testes via `run_tests` com avaliação de trajetória (`tool_trajectory_avg_score`).
- **Caso 4 (`caso_4_adicionar_nova_funcao_com_testes`)**: Criação de novas funções e validação com suíte de testes.

---

## 🚀 Como Executar

### 1. Pré-requisitos
- Python 3.10+
- Google GenAI ADK instalado
- Variável `GEMINI_API_KEY` configurada no arquivo `.env` dentro de `codereviewer/`

### 2. Iniciar o ADK Web UI
A partir da raiz do repositório ou pasta do agente:
```bash
adk web ADKCodeReviewer/codereviewer
```
Acesse a interface em `http://localhost:8000` para conversar com o agente ou acessar a aba **Eval Sets** para rodar os testes automatizados.
