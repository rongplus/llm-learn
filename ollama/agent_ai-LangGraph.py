from typing import TypedDict, List

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    BaseMessage,
)
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader,UnstructuredPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import CharacterTextSplitter,RecursiveCharacterTextSplitter


# =========================
# 1. 定义 Agent State
# =========================
class AgentState(TypedDict):
    messages: List[BaseMessage]
    plan: str
    research: str
    result: str
    critique: str


# =========================
# 2. 初始化模型
# =========================
llm = ChatOllama(
    model="llama3",
    temperature=0.7
)

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)


# =========================
# 3. 构建 / 加载向量库（PDF）
# =========================
def load_vectorstore():
    loader = PyPDFLoader("data/LLM-v1.0.0.pdf")

    # ✅ 直接 load
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="vectordb"
    )

    return vectordb


vectordb = load_vectorstore()


# =========================
# 4. Planner Node
# =========================
def planner(state: AgentState):
    question = state["messages"][-1].content

    prompt = f"""
You are a planner AI.

User question:
{question}

Break the task into steps.
Do not answer the question.
"""

    plan_msg = llm.invoke([HumanMessage(content=prompt)])

    return {
        "plan": plan_msg.content,
        "messages": state["messages"] + [
            AIMessage(content=f"[PLAN]\n{plan_msg.content}")
        ],
    }


# =========================
# 5. Researcher Node（RAG）
# =========================
def researcher(state: AgentState):
    query = state["messages"][-1].content

    docs = vectordb.similarity_search(query, k=4)

    context = "\n\n".join(
        f"- {doc.page_content}" for doc in docs
    )

    prompt = f"""
You are a research assistant.

Use ONLY the following context.
Do not write final answer.

CONTEXT:
{context}
"""

    research_msg = llm.invoke([HumanMessage(content=prompt)])

    return {
        "research": research_msg.content,
        "messages": state["messages"] + [
            AIMessage(content=f"[RESEARCH]\n{research_msg.content}")
        ],
    }


# =========================
# 6. Executor Node
# =========================
def executor(state: AgentState):
    prompt = f"""
You are an executor AI.

PLAN:
{state["plan"]}

RESEARCH:
{state["research"]}

Write a clear final answer for the user.
"""

    result_msg = llm.invoke([HumanMessage(content=prompt)])

    return {
        "result": result_msg.content,
        "messages": state["messages"] + [
            AIMessage(content=result_msg.content)
        ],
    }


# =========================
# 7. Critic Node
# =========================
def critic(state: AgentState):
    prompt = f"""
You are a critic AI.

Improve clarity and correctness of the answer below.

ANSWER:
{state["result"]}
"""

    critique_msg = llm.invoke([HumanMessage(content=prompt)])

    return {
        "critique": critique_msg.content,
        "messages": state["messages"] + [
            AIMessage(content=f"[FINAL]\n{critique_msg.content}")
        ],
    }


# =========================
# 8. 构建 LangGraph
# =========================
graph = StateGraph(AgentState)

graph.add_node("planner", planner)
graph.add_node("researcher", researcher)
graph.add_node("executor", executor)
graph.add_node("critic", critic)

graph.add_edge(START, "planner")
graph.add_edge("planner", "researcher")
graph.add_edge("researcher", "executor")
graph.add_edge("executor", "critic")
graph.add_edge("critic", END)

graph = graph.compile()


# =========================
# 9. 运行入口
# =========================
if __name__ == "__main__":
    initial_state: AgentState = {
        "messages": [
            HumanMessage(
                content="What does this document say about large language models?"
            )
        ],
        "plan": "",
        "research": "",
        "result": "",
        "critique": "",
    }

    final_state = graph.invoke(initial_state)

    print("\n========== FINAL ANSWER ==========\n")
    print(final_state["critique"])
