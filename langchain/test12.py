from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain.schema.document import Document
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM
from langchain_core.runnables import RunnablePassthrough
model_local = OllamaLLM(model="llama3")

# 1. Split data into chunks
urls = [
    "https://en.wikipedia.org/wiki/Maroon_5",
    "https://en.wikipedia.org/wiki/1921_Centre_vs._Harvard_football_game"
]
docs = [WebBaseLoader(url,encoding='UTF-8').load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=7500, chunk_overlap=100)
doc_splits = text_splitter.split_documents(docs_list)

# 2. Convert documents to Embeddings and store them
vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name="rag-chroma",
     embedding=OllamaEmbeddings(base_url="http://localhost:11434", model="llama3")
)
retriever = vectorstore.as_retriever()

# 3. Before RAG
print("Before RAG\n")
before_rag_template = "What is {topic}"
before_rag_prompt = ChatPromptTemplate.from_template(before_rag_template)
before_rag_chain = before_rag_prompt | model_local | StrOutputParser()
print(before_rag_chain.invoke({"topic": "Ollama"}))
answer1 = before_rag_chain.invoke("中国人的居住风格是什么样子的?")
print("--------before_rag_chain--------")
print(answer1)
print("------------------------")

# 4. After RAG
print("\n########\nAfter RAG\n")
after_rag_template = """Answer the question based only on the following context:
{context}
Question: {question}
"""
after_rag_prompt = ChatPromptTemplate.from_template(after_rag_template)
after_rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | after_rag_prompt
    | model_local
    | StrOutputParser()
)
print(after_rag_chain.invoke("Quien integra Brigada A?"))


answer1 = after_rag_chain.invoke("中国人的居住风格是什么样子的?")
print("-------after_rag_chain---------")
print(answer1)
print("------------------------")