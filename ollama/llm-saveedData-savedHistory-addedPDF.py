import json
import os
from typing import Dict
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import CharacterTextSplitter,RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.document_loaders import PyPDFLoader
# -------------------------------
# 1) SCRAPE ZHIHU ARTICLE
# -------------------------------
lilianweng_URL = "https://lilianweng.github.io/posts/2023-06-23-agent/"

INDEX_DIR = "vector_index_lilianweng"
HISTORY_FILE = "chat_history_lilianweng.json"
PDF_DIR = "data"
MODEL_NAME = 'llama3'

# =========================
# LOAD PDFS
# =========================
def load_pdfs(pdf_dir: str):
    documents = []
    for path in Path(pdf_dir).rglob("*.pdf"):
        print(f"📄 Loading {path}")
        loader = PyPDFLoader(str(path))
        documents.extend(loader.load())
    return documents

# =========================
# APPEND TO VECTORSTORE
# =========================
def add_pdfs_to_index(vectordb):
    docs = load_pdfs(PDF_DIR)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)

    print(f"📌 Adding {len(chunks)} chunks to existing index")

    vectordb.add_documents(chunks)
    vectordb.save_local(INDEX_DIR)

    print("✅ PDFs successfully added to existing vectorstore")

def fetch_lilianweng_article(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    # Extract main content
    article_body = soup.select_one("article")
    if not article_body:
        article_body = soup.select_one(".Post-RichTextContainer")  # fallback
    text = article_body.get_text(separator="\n").strip()
    return text



def build_vectorstore():
    print("📌 Fetching article...")
    raw_text = fetch_lilianweng_article(lilianweng_URL)
    print("✅ Article downloaded:", len(raw_text), "characters")

    # -------------------------------
    # 2) SPLIT & EMBED TEXT
    # -------------------------------
    print("📌 Splitting content for embeddings...")
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = splitter.split_text(raw_text)

    print(f"📌 Creating embeddings for {len(texts)} chunks...")

    embeddings = OllamaEmbeddings(model="llama3")  # Ollama embeddings
    vectordb = FAISS.from_texts(texts, embeddings)
    vectordb.save_local(INDEX_DIR)
    print("✅ Vector index saved")

    print("✅ Embeddings created and indexed!")
    return vectordb

def load_vectorstore():
    if not os.path.exists(INDEX_DIR):
        return build_vectorstore()

    print("✅ Loading existing vector index")
    embeddings = OllamaEmbeddings(model="llama3")  # Ollama embeddings
    return FAISS.load_local(
        INDEX_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )

vectordb = load_vectorstore()
add_pdfs_to_index(vectordb)
# -------------------------------
# 3) SETUP CHAT WITH HISTORY
# -------------------------------

# ==================================================
# HISTORY FILE HELPERS
# ==================================================
def load_history_file() -> Dict[str, list]:
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history_file(data: Dict[str, list]):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def json_to_messages(items):
    messages = []
    for item in items:
        if item["role"] == "human":
            messages.append(HumanMessage(content=item["content"]))
        elif item["role"] == "ai":
            messages.append(AIMessage(content=item["content"]))
    return messages

def messages_to_json(messages):
    out = []
    for m in messages:
        if isinstance(m, HumanMessage):
            out.append({"role": "human", "content": m.content})
        elif isinstance(m, AIMessage):
            out.append({"role": "ai", "content": m.content})
    return out



def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in session_histories:
        history = InMemoryChatMessageHistory()
        if session_id in history_file_data:
            history.messages = json_to_messages(history_file_data[session_id])
        session_histories[session_id] = history
        print(f"📜 Loaded history for session: {session_id}")
    return session_histories[session_id]
# -------------------------------
# 4) RETRIEVE + CHAT LOOP
# -------------------------------
def retrieve_context(query: str, k: int = 4) -> str:
    results = vectordb.similarity_search(query, k=k)
    combined = "\n\n".join([doc.page_content for doc in results])
    return combined

# ==================================================
# LOAD HISTORY INTO MEMORY
# ==================================================
history_file_data = load_history_file()
session_histories: Dict[str, InMemoryChatMessageHistory] = {}
llm = ChatOllama(model="llama3", temperature=0.2, streaming=True)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that answers based on the provided document context."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

chain = prompt | llm

chat_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)



print("\n🧠 RAG Chat Ready (type 'exit')\n")

session_id = "user-1"
while True:
    q = input("User: ")
    if q.lower() in ("exit", "quit"):
        break

    # 1) retrieve context
    context = retrieve_context(q)
    augmented_input = f"{q}\n\nRelevant content:\n{context}"

    # 2) stream answer
    print("Assistant: ", end="", flush=True)
    full_answer = ""
    for token in chat_with_history.stream(
        {"input": augmented_input},
        config={"configurable": {"session_id": session_id}}
    ):
        if token.content:
            print(token.content, end="", flush=True)
            full_answer += token.content

    print("\n")

    # ==================================================
    # SAVE HISTORY
    # ==================================================
    history_obj = session_histories[session_id]
    history_file_data[session_id] = messages_to_json(history_obj.messages)
    save_history_file(history_file_data)
