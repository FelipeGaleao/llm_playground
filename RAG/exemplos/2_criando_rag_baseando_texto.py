from dotenv import load_dotenv
import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

# Configurar embeddings e modelo de chat
embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), 
    model="gpt-4-turbo-preview", 
    temperature=0
)

# Caminhos para os arquivos de texto
base_path = "/Users/mfelipemota/Projects/llm_playground/RAG/exemplos/arquivos/"
arquivos_texto = [
    "mca-100-16-2021-01-04-_1_.txt",
    "manual_seguranca_737.txt"
]

# Ler todos os documentos
documentos = []
for arquivo in arquivos_texto:
    arquivo_path = os.path.join(base_path, arquivo)
    try:
        with open(arquivo_path, "r", encoding="utf-8") as f:
            texto = f.read()
            # Adicionar identificador do documento ao texto
            texto_com_fonte = f"[FONTE: {arquivo}]\n{texto}"
            documentos.append(texto_com_fonte)
            print(f"Documento carregado: {arquivo}")
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {arquivo}")
        continue

# Combinar todos os documentos
texto_completo = "\n\n".join(documentos)

# Dividir o texto em chunks menores para melhor performance
chunks = [texto_completo[i:i+1000] 
          for i in range(0, len(texto_completo), 1000)]

# Criar o vector store
vector_store = FAISS.from_texts(chunks, embeddings)
retriever = vector_store.as_retriever()

# Criar template de prompt
template = """Você é um instrutor especializado em Boeing 737-800 e está 
ajudando pilotos a operarem a aeronave de forma profissional.
Você receberá dúvidas sobre procedimentos, checklists e operações do 
Boeing 737-800.
Você deve responder as perguntas com base no QRH (Quick Reference Handbook) 
e no Manual de Segurança fornecidos no contexto.
Se você não souber a resposta, diga que não sabe.
Se a pergunta for sobre um assunto que não está no contexto dos documentos, 
diga que não sabe.
Forneça respostas diretas e práticas, citando os procedimentos específicos 
quando aplicável.
Responda em markdown, com tom otimista para uma resposta no Slack.

Contexto: {context}

Pergunta: {question}

Resposta:"""

prompt = PromptTemplate(
    template=template, 
    input_variables=["context", "question"]
)

# Criar a chain RAG
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt}
)

# Fazer pergunta
pergunta = input("Digite uma pergunta: ")
resposta = qa_chain.invoke({"query": pergunta})

print(f"\nPergunta: {pergunta}")
print(f"Resposta: {resposta['result']}")
print(f"\nDocumentos processados: {len(documentos)}")
print(f"Total de chunks criados: {len(chunks)}")