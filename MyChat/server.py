import os
import json
import uuid
import shutil
from typing import Dict

from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.responses import HTMLResponse

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory

# =========================
# CONFIG
# =========================
MODEL_NAME = "llama3"
VECTOR_DIR = "vectorstore"
UPLOAD_DIR = "uploaded_pdfs"
HISTORY_FILE = "chat_history.json"

os.makedirs(VECTOR_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# =========================
# VECTORSTORE
# =========================
embeddings = OllamaEmbeddings(model=MODEL_NAME)

if os.path.exists(os.path.join(VECTOR_DIR, "index.faiss")):
    vectordb = FAISS.load_local(
        VECTOR_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )
else:
    vectordb = FAISS.from_texts(
        ["初始化知识库"], embeddings
    )
    vectordb.save_local(VECTOR_DIR)

# =========================
# HISTORY
# =========================
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    return json.load(open(HISTORY_FILE, encoding="utf-8"))

def save_history(data):
    json.dump(data, open(HISTORY_FILE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

history_file_data = load_history()
session_histories: Dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id):
    if session_id not in session_histories:
        h = InMemoryChatMessageHistory()
        if session_id in history_file_data:
            for m in history_file_data[session_id]:
                if m["role"] == "human":
                    h.add_user_message(m["content"])
                else:
                    h.add_ai_message(m["content"])
        session_histories[session_id] = h
    return session_histories[session_id]

# =========================
# LLM + PROMPT
# =========================
llm = ChatOllama(
    model=MODEL_NAME,
    streaming=True,
    temperature=0.2
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个基于本地知识库回答问题的 AI，请只根据以下内容回答：\n\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

chain = prompt | llm

chat_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history"
)

# =========================
# RETRIEVAL
# =========================
def retrieve_context(query: str, k: int = 4):
    docs = vectordb.similarity_search(query, k=k)
    return "\n\n".join(d.page_content for d in docs)

# =========================
# PDF INGEST
# =========================
def add_pdf_to_vectordb(pdf_path, filename):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    for d in docs:
        d.metadata["source"] = filename

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(docs)
    vectordb.add_documents(chunks)
    vectordb.save_local(VECTOR_DIR)
    return len(chunks)

# =========================
# API
# =========================
@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    uid = uuid.uuid4().hex
    path = os.path.join(UPLOAD_DIR, f"{uid}_{file.filename}")

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    count = add_pdf_to_vectordb(path, file.filename)

    return {"status": "ok", "chunks": count}

@app.websocket("/ws/{session_id}")
async def chat_ws(ws: WebSocket, session_id: str):
    await ws.accept()

    while True:
        msg = await ws.receive_text()
        context = retrieve_context(msg)

        for chunk in chat_chain.stream(
            {"question": msg, "context": context},
            config={"configurable": {"session_id": session_id}}
        ):
            if chunk.content:
                await ws.send_text(chunk.content)

        await ws.send_text("__END__")

        hist = session_histories[session_id]
        history_file_data[session_id] = [
            {"role": "human" if isinstance(m, HumanMessage) else "ai", "content": m.content}
            for m in hist.messages
        ]
        save_history(history_file_data)

@app.get("/")
def index():
    return HTMLResponse(open("index.html", encoding="utf-8").read())
