import os
from datetime import date, datetime

# Optional: Load environment variables if you have specific configurations
# from dotenv import load_dotenv
# load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.docstore.document import Document
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_ollama.chat_models import ChatOllama
from langchain.tools import tool
from langchain_community.vectorstores import FAISS

from langchain_core.prompts import PromptTemplate
from langchain.agents import create_agent

# --- Configuration ---
# Make sure Ollama is running with the specified model
# (e.g., run "ollama run llama3" in your terminal)
OLLAMA_MODEL = "llama3:latest"
OLLAMA_BASE_URL = "http://localhost:11434" # Default Ollama URL
DOCS_FOLDER = "docs_to_load" # Folder to load documents from

print(f"Using Ollama model: {OLLAMA_MODEL}")
print("-" * 30)

# --- 1. Set up the LLM ---
llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0) # Set temperature to 0
print("LLM Initialized.")

# --- 2. Set up RAG ---
# a) Load documents from the specified folder
print(f"Loading documents from: {DOCS_FOLDER}")
try:
    # Using DirectoryLoader for .txt files by default
    loader = DirectoryLoader(DOCS_FOLDER, glob="**/*.txt", show_progress=True)
    loaded_docs = loader.load()
    print(f"Loaded {len(loaded_docs)} documents for RAG.")
    if not loaded_docs:
        print(f"Warning: No documents found in '{DOCS_FOLDER}'. RAG might not work as expected.")
except Exception as e:
    print(f"Error loading documents from {DOCS_FOLDER}: {e}")
    loaded_docs = [] # Ensure loaded_docs is defined even if loading fails

# b) Create embeddings
embeddings = OllamaEmbeddings(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
print("Embeddings Initialized.")

# c) Create a vector store and retriever
try:
    vector_store = FAISS.from_documents(loaded_docs, embeddings)
    # Retrieve the top 2 relevant docs to provide more context
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})
    print("Vector Store and Retriever Initialized (using FAISS).")
except Exception as e:
    print(f"Error initializing FAISS. Is faiss-cpu installed? Error: {e}")
    exit()

# --- 3. Set up a Custom Tool ---
@tool
def get_current_date(arg: str) -> str:
    """
    Returns the current date in YYYY-MM-DD format.
    返回今天的日期,格式 YYYY-MM-DD
    Use this tool specifically for getting the date. It does not provide the time.
    Ignores any input argument.
    """
    return date.today().isoformat()

print("Custom Date Tool Created.")

@tool
def get_current_time(arg: str) -> str:
    """Returns the current time in HH:MM:SS format. Ignores any input argument."""
    return datetime.now().strftime("%H:%M:%S")

print("Custom Date and Time Tools Created.")

@tool
def calculate_days_until(future_date_str: str) -> str:
    """
    Calculates the number of days from today until a specified future date.
    Expects the future date as a string in 'YYYY-MM-DD' format.
    Returns a string describing the number of days remaining or an error message.
    """
    print(f"DEBUG: calculate_days_until received raw input: '{future_date_str}' (length: {len(future_date_str)})")
    try:
        # Clean the input string: remove leading/trailing whitespace and potential quotes
        cleaned_date_str = future_date_str.strip().strip("'\"")
        print(f"DEBUG: calculate_days_until cleaned input: '{cleaned_date_str}' (length: {len(cleaned_date_str)})")

        today = date.today()
        future_date = datetime.strptime(cleaned_date_str, "%Y-%m-%d").date()

        if future_date <= today:
            return f"Error: The date {cleaned_date_str} is not in the future."

        delta = future_date - today
        return f"There are {delta.days} days remaining until {cleaned_date_str}."
    except ValueError:
        print(f"DEBUG: ValueError during strptime for cleaned input: '{cleaned_date_str}' (raw: '{future_date_str}')")
        return "Error: Invalid date format. Please use 'YYYY-MM-DD'."
    except Exception as e:
        print(f"DEBUG: Exception in calculate_days_until: {e} for raw input: '{future_date_str}'")
        return f"An unexpected error occurred: {e}"

# --- 4. Create the Agent ---
# a) Define the tools the agent can use
tools = [get_current_date, get_current_time, calculate_days_until] # RAG tool is removed

# b) Get a standard ReAct prompt template
# Create a custom prompt template
custom_prompt_template = """
You have been provided with the following context information retrieved from relevant documents:
<RAG_CONTEXT_START>
{rag_context}
<RAG_CONTEXT_END>

Answer the following question. First, carefully review the RAG_CONTEXT. If it directly answers the user's question, formulate your answer based on it.
If the RAG_CONTEXT is insufficient, or if the question requires other capabilities (like getting the current date or performing calculations), you have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: First, I will check if the provided RAG_CONTEXT answers the question. If yes, I will formulate the answer. If no, or if a specific capability (like current date or calculations) is needed, I will consider using a tool.
Action: Exactly one tool name from [{tool_names}] OR the string "Final Answer" if no tool is needed (e.g., because the RAG_CONTEXT was sufficient or the question is general).
Action Input: the input to the action. This should contain *only* the required input value for the tool, formatted correctly (e.g., 'YYYY-MM-DD' for dates). Do NOT include extra commentary or explanation within the Action Input itself.
Observation: the result of the action.
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: After receiving an Observation, I MUST carefully analyze it along with the RAG_CONTEXT and the original question.
If the Observation, combined with prior information (like RAG_CONTEXT), provides all the necessary pieces to answer the original question, my thought MUST be "I now have all the information needed to answer the user's question." and then I MUST proceed directly to the "Final Answer:".
If, after analyzing the Observation, I determine that more steps or another tool is genuinely required, I will then plan the next Action. Do not repeat a previous action if the observation was successful.
Final Answer: The comprehensive final answer to the original input question, synthesized from RAG_CONTEXT and any tool Observations.

**Important Instructions:**
- Only use the `get_current_date` tool if the question specifically asks for the current date.
- Only use the `get_current_time` tool if the question specifically asks for the current time.
- Only use the `calculate_days_until` tool if the question specifically asks to calculate the number of days until a future date, and provide the date in 'YYYY-MM-DD' format as the Action Input.
- If the RAG_CONTEXT is sufficient to answer the question, or if the question is general and does not require a tool, provide the answer directly in the "Final Answer" section after your initial "Thought".

Begin!

Question: {input}
RAG Context Provided:
{rag_context}
Thought:{agent_scratchpad}
"""

prompt = PromptTemplate(
    input_variables=["agent_scratchpad", "input", "tool_names", "tools", "rag_context"],
    template=custom_prompt_template,
)

# c) Create the ReAct agent
#agent = create_agent(llm, tools, prompt)
print("ReAct Agent Creat......")

model = ChatOllama(model="llama3.2:3b-instruct-fp16")

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="You are a helpful research assistant."
)


# d) Create the Agent Executor


# --- 5. Run the Application ---
print("Ready! Ask me about Project Alpha, Project Beta, or the current date.")
print("Type 'quit' to exit.")

while True:
    try:
        user_input = input("\nYour question: ")
        if user_input.lower() == 'quit':
            break

        # 1. Perform RAG retrieval first
        retrieved_docs = retriever.invoke(user_input)
        rag_context_str = "\n\n".join([doc.page_content for doc in retrieved_docs])
        if not rag_context_str:
            rag_context_str = "No specific context found in documents for this query."

        # 2. Invoke the agent with the user input and the retrieved RAG context
        agent_input = {"input": user_input, "rag_context": rag_context_str}

        final_input = f"""
Use this document context first:

{rag_context_str}

Question:
{user_input}
"""
        
        #response = agent.invoke(agent_input)
        response = agent.invoke({
            "messages": [
                {"role": "user", "content": final_input}
            ]
        })

        print("\nAgent Response:")
        print(response["messages"][-1].content)

    except Exception as e:
        print(f"\nAn error occurred: {e}")

print("\nExiting application.")