from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS

INDEX_DIR = "vector_index-ollama"
llm = ChatOllama(
    model='llama3',   
    temperature=0,
    streaming=True,
)

# Web 搜索（DuckDuckGo）
from ddgs import DDGS

def ddgs_search(q: str) -> str:
    items = []
    with DDGS() as s:
        for it in s.text(q.strip(), max_results=6):
            items.append(f"{it['title']} :: {it['href']} :: {it['body']}")
    return "\n".join(items)[:2000] or "no results"

# 浏览器渲染（获取真实页面内容）
from playwright.sync_api import sync_playwright

def browser_render(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url.strip(), wait_until="domcontentloaded", timeout=30000)
        html = page.content()
        context.close(); browser.close()
    return html[:4000]

# HTTP 端点获取
import requests
from bs4 import BeautifulSoup
def http_fetch(url: str) -> str:
    r = requests.get(url.strip(), timeout=20)
    r.raise_for_status()
    return r.text[:2000]

# PDF 文本提取（可选）
import tempfile
from pathlib import Path

def download_pdf_text(url: str) -> str:
    r = requests.get(url.strip(), timeout=30)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(r.content)
        path = Path(tmp.name)
    try:
        from langchain_community.document_loaders.pdf import PyPDFLoader
        pages = PyPDFLoader(str(path)).load()
        return "\n".join(p.page_content for p in pages)[:4000]
    finally:
        path.unlink(missing_ok=True)

lilianweng_URL = "https://lilianweng.github.io/posts/2023-06-23-agent/"
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

from langchain_core.tools import StructuredTool

tools = [
    StructuredTool.from_function(ddgs_search, name="ddgs_search", description="Perform web search via DuckDuckGo."),
    StructuredTool.from_function(browser_render, name="browser_render", description="Render a webpage using headless Chromium and return HTML content."),
    StructuredTool.from_function(http_fetch, name="http_fetch", description="Fetch plain text or JSON from HTTP endpoints."),
    StructuredTool.from_function(download_pdf_text, name="download_pdf_text", description="Download a PDF file and extract its textual content."),
]



from langchain_classic.agents import AgentType, initialize_agent

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=30,
    agent_kwargs={
        "system_message": (
            "You are a ReAct analyst. Solve the task by interleaving Thought, Action, and Observation. "
            "Do not treat search engine result pages (SERPs) as evidence. Always open and summarize at least one "
            "content page, PDF, or API response before concluding. If evidence is insufficient, state 'Insufficient Evidence' "
            "instead of hallucinating."
        )
    },
)

result = agent.invoke({"input": "what is Whole Life insurance"})
print("\n[Final Answer]", result.get("output"))