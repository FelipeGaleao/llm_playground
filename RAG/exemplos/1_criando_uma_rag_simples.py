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
    api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4-turbo-preview", temperature=0
)

# Criar dados de exemplo
texts = [
    "Paris é a capital da França e uma das cidades mais visitadas do mundo.",
    "A Torre Eiffel é um dos marcos mais famosos de Paris.",
    "França é um país europeu conhecido por sua cultura, arte e culinária.",
]

# Criar o vector store
vector_store = FAISS.from_texts(texts, embeddings)
retriever = vector_store.as_retriever()

# Criar template de prompt
template = (
    "Use o seguinte contexto para responder à pergunta. "
    "Se você não souber a resposta baseada no contexto, "
    "diga que não sabe. \n\n"
    "Se a pergunta for sobre um assunto que não está no contexto, "
    "diga que não sabe. \n\n"
    "Contexto: {context}\n\n"
    "Pergunta: {question}\n\n"
    "Resposta:"
)

prompt = PromptTemplate(template=template, input_variables=["context", "question"])

# Criar a chain RAG
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt},
)

# Fazer uma pergunta
pergunta = input("Digite uma pergunta: ")
resposta = qa_chain.invoke({"query": pergunta})

print(f"Pergunta: {pergunta}")
print(f"Resposta: {resposta['result']}")