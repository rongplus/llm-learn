from langchain_community.chat_models import ChatOllama
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage

llm = ChatOllama(model="llama3", temperature=0.3)

# Per-session memory store
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chat = RunnableWithMessageHistory(
    llm,
    get_session_history,
)

print("🧠 Ollama3 Chat with History (type exit)\n")

session_id = "user-1"

while True:
    user_input = input("User: ")
    if user_input.lower() in ("exit", "quit"):
        break

#------------invoke chat with history------------
    """
    response = chat.invoke(
        [HumanMessage(content=user_input)],
        config={"configurable": {"session_id": session_id}},
        return_intermediate_steps=True
    )
    """
#------------print response------------
     # STREAM tokens
    for chunk in chat.stream(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}}
    ):
        if chunk.content:
            print(chunk.content, end="", flush=True)

    print("\n")

    #print("Agent:", response.content, "\n")
