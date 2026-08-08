# 将文本分割成更小的部分以进行处理
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 读入txt文件
from langchain_community.document_loaders import TextLoader

# Emdedding模型
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

# 向量数据库Chroma
from langchain_chroma import Chroma


from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnableLambda, RunnablePassthrough


# 导入本地文本
loader = TextLoader("demo2.txt",encoding='utf-8')
data = loader.load()

# 将文本分割成长度为200个字符的小块，并且每个小块之间有20个字符的重叠
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
all_splits = text_splitter.split_documents(data)


#Embedding模型
embedding_function = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-m3")

#导入向量数据库Chroma
vectorstore_torist = Chroma.from_documents(all_splits, embedding_function, persist_directory="./vector_store")

# 使用Ollama:llama3
OLLAMA_MODEL='llama3'
# Prompt设定输出为中文，并且将其上下文设置为向量数据库中的内容
template = """
Answer the question based only on the following context, and output in Chinese:
{context}
Question: {question}
"""

retriever = vectorstore_torist.as_retriever()
prompt = ChatPromptTemplate.from_template(template)

# 采用本地的大语言模型llama3对话
ollama_llm = "llama3"

#构建RAG Chain
model_local = ChatOllama(model=ollama_llm)



# Chain
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model_local
    | StrOutputParser()
)


print(chain.invoke("莱斯科特翼的特点"))
