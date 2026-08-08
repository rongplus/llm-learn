from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import TextLoader,PyPDFLoader,WikipediaLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

#### Load

loader = TextLoader("a.txt",encoding='UTF-8')
docs = loader.load()


loader = PyPDFLoader("handbook.pdf")
docs = loader.load()
docs
print(docs[0].page_content)

#!pip install wikipedia
loader = WikipediaLoader(query="颐和园", load_max_docs=3, lang="zh")
docs = loader.load()
docs

####split
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=40,
    separators=["\n\n", "\n", "。", "！", "？", "，", "、", ""]
)

texts = text_splitter.split_documents(docs)
texts


print(texts[0].page_content)



####embedding

embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# 如果你使用的是课程提供的API，则需要提供额外参数
# embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large",
#                                     openai_api_key="<你的API密钥>",
#    
embeded_result = embeddings_model.embed_documents(["Hello world!", "Hey bro"])


# 如果希望嵌入向量维度更小，可以通过dimensions参数进行指定
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=1024)
embeded_result = embeddings_model.embed_documents(["Hello world!", "Hey bro"])
len(embeded_result[0])


db = FAISS.from_documents(texts, embeddings_model)
retriever = db.as_retriever()
retrieved_docs = retriever.invoke("卢浮宫这个名字怎么来的？")
print(retrieved_docs[0].page_content)
##“罗浮宫”这个名字的由来有些争议。根据法国百科全书辞典大拉鲁斯百科全书
retrieved_docs = retriever.invoke("卢浮宫在哪年被命名为中央艺术博物馆")
print(retrieved_docs[0].page_content)
##1793年8月10日，即君主制灭亡一周年，罗浮宫正式命名为“中央艺术博物馆”开放。


#-------------
loader = TextLoader("./demo2.txt")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=40,
    separators=["\n", "。", "！", "？", "，", "、", ""]
)
texts = text_splitter.split_documents(docs)
embeddings_model = OpenAIEmbeddings()
db = FAISS.from_documents(texts, embeddings_model)
retriever = db.as_retriever()
model = ChatOpenAI(model="gpt-3.5-turbo")
memory = ConversationBufferMemory(return_messages=True, memory_key='chat_history', output_key='answer')
qa = ConversationalRetrievalChain.from_llm(
    llm=model,
    retriever=retriever,
    memory=memory
)

question = "卢浮宫这个名字怎么来的？"
qa.invoke({"chat_history": memory, "question": question})

question = "对应的拉丁语是什么呢？"
qa.invoke({"chat_history": memory, "question": question})


qa = ConversationalRetrievalChain.from_llm(
    llm=model,
    retriever=retriever,
    memory=memory,
    return_source_documents=True
)


question = "卢浮宫这个名字怎么来的？"
qa.invoke({"chat_history": memory, "question": question})