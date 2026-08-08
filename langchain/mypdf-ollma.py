# Langchain dependencies
from langchain_community.document_loaders  import PyPDFLoader,PyPDFDirectoryLoader,WebBaseLoader,WikipediaLoader # Importing PDF loader from Langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter,CharacterTextSplitter # Importing text splitter from Langchain
from langchain_ollama import OllamaEmbeddings,OllamaLLM # Importing OpenAI embeddings from Langchain
from langchain.schema import Document # Importing Document schema from Langchain
from langchain_chroma import Chroma  # Importing Chroma vector store from Langchain

from langchain_community.chat_models import ChatOllama

import os # Importing os module for operating system functionalities
import shutil # Importing shutil module for high-level file operations

from langchain.schema.document import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

model_local = OllamaLLM(model="llama3")

# 1. Split data into chunks
urls = [
    "https://en.wikipedia.org/wiki/Maroon_5",
    "https://en.wikipedia.org/wiki/1921_Centre_vs._Harvard_football_game"
]
docs = [WebBaseLoader(url,encoding='UTF-8').load() for url in urls]
loader = WikipediaLoader(query="颐和园", load_max_docs=3, lang="zh")
docs = loader.load()

p1 =  PyPDFLoader("../data/a1.pdf")
p2 =  PyPDFLoader("../data/a1.pdf")
documents = [p1.load(),p2.load()] # Call the function

####split
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=40,
    separators=["\n\n", "\n", "。", "！", "？", "，", "、", ""]
)

doc_splits = text_splitter.split_documents(documents)

#docs_list = [item for sublist in docs for item in sublist]
#text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=7500, chunk_overlap=100)
#doc_splits = text_splitter.split_documents(docs_list)



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

answer1 = before_rag_chain.invoke("请用中文描述一下颐和园的特点")
print("--------before_rag_chain--------")
print(answer1)
print("-----end --before_rag_chain---------")

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


print("-------after_rag_chain---------")
answer1 = after_rag_chain.invoke("请用中文描述一下颐和园的特点")
print("-------after_rag_chain---------")
print(answer1)
print("------------------------")