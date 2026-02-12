import os
from typing import List

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# =========================
# 0. 基础配置
# =========================
VECTORDB_DIR = "vectordb"
PDF_PATH = "data/LLM-v1.0.0.pdf"

# =========================
# 1. LLM（Streaming）
# =========================
llm = ChatOllama(
    model="llama3",
    temperature=0,
    streaming=True
)

# =========================
# 2. Embedding
# =========================
embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

# =========================
# 3. VectorDB（自动构建或加载）
# =========================
def load_or_build_vectordb():
    if os.path.exists(VECTORDB_DIR) and os.listdir(VECTORDB_DIR):
        return Chroma(
            persist_directory=VECTORDB_DIR,
            embedding_function=embeddings
        )

    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORDB_DIR
    )
    return vectordb

vectordb = load_or_build_vectordb()
retriever = vectordb.as_retriever(search_kwargs={"k": 4})

# =========================
# 4. Tool（兜底搜索，占位）
# =========================
def web_search_tool(query: str) -> str:
    # ⚠️ 示例占位：真实项目中替换为 SerpAPI / Tavily / 自建爬虫
    return f"""
[Web Search Result]

No sufficient information found in local knowledge base.
This is a placeholder result for the query:

{query}
"""

# =========================
# 5. Router（判断走 RAG 还是 Tool）
# =========================
router_prompt = ChatPromptTemplate.from_template("""
你是一个判断器。

给定用户问题和检索到的上下文，
判断这些上下文是否足以回答问题。

如果足够，回答：RAG
如果不足或不相关，回答：TOOL

只回答 RAG 或 TOOL。

问题：
{question}

上下文：
{context}
""")

router_chain = router_prompt | llm | StrOutputParser()

# =========================
# 6. RAG Streaming Chain
# =========================
rag_prompt = ChatPromptTemplate.from_template("""
请严格基于以下上下文回答问题，不要编造。

上下文：
{context}

问题：
{question}
""")

rag_chain = (
    {
        "context": retriever,
        "question": RunnablePassthrough()
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)

# =========================
# 7. Tool + LLM Streaming Chain
# =========================
tool_prompt = ChatPromptTemplate.from_template("""
你是一个助手。

用户问题：
{question}

下面是通过工具获得的信息：
{tool_result}

请基于工具结果，给出清晰、准确的回答。
""")

tool_chain = tool_prompt | llm | StrOutputParser()

# =========================
# 8. 核心函数：RAG + Tool Streaming
# =========================
def rag_with_tool_stream(question: str):
    # 1️⃣ 先检索
    docs = retriever.invoke(question)
    context = "\n\n".join([d.page_content for d in docs])

    # 2️⃣ Router 决策
    route = router_chain.invoke({
        "question": question,
        "context": context
    }).strip()

    print(f"\n[Router Decision]: {route}\n")

    # 3️⃣ RAG 路径
    if route == "RAG" and context.strip():
        print("📚 使用本地知识库：\n")
        for token in rag_chain.stream(question):
            yield token

    # 4️⃣ Tool 兜底路径
    else:
        print("🌐 本地知识不足，调用 Tool：\n")
        tool_result = web_search_tool(question)

        for token in tool_chain.stream({
            "question": question,
            "tool_result": tool_result
        }):
            yield token

# =========================
# 9. CLI 运行入口
# =========================
if __name__ == "__main__":
    print("=== RAG Streaming + Tool Demo ===\n")

    while True:
        q = input("\n❓ 请输入你的问题（输入 exit 退出）：\n> ")
        if q.lower() in ("exit", "quit"):
            break

        print("\n🤖 回答中：\n")
        for chunk in rag_with_tool_stream(q):
            print(chunk, end="", flush=True)

        print("\n\n" + "=" * 60)
