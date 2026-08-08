from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
 ###http://shiyanjun.cn/archives/2613.html
llm = Ollama(model="llama3")
chat_model = ChatOllama()
print("导入数据前 -------------")
from langchain.schema import HumanMessage
 
text = "What would be a good company name for a company that makes colorful socks?"
messages = [HumanMessage(content=text)]
llm.invoke(text) # >> Feetful of Fun
print(chat_model.invoke(messages)) # >> AIMessage(content="Socks O'Color")


from langchain.prompts.chat import ChatPromptTemplate
 
template = "You are a helpful assistant that translates {input_language} to {output_language}."
human_template = "{text}"
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", template),
    ("human", human_template),
])
chat_prompt.format_messages(input_language="English", output_language="French", text="I love programming.")



from langchain.output_parsers import CommaSeparatedListOutputParser
 
output_parser = CommaSeparatedListOutputParser()
print(output_parser.parse("hi, bye") )# >> ['hi', 'bye']


template = "Generate a list of 5 {text}.\n\n{format_instructions}"
 
chat_prompt = ChatPromptTemplate.from_template(template)
chat_prompt = chat_prompt.partial(format_instructions=output_parser.get_format_instructions())
chain = chat_prompt | chat_model | output_parser
aa = chain.invoke({"text": "colors"}) # >> ['red', 'blue', 'green', 'yellow', 'orange']
print(aa)


###导入数据前 -------------
###导入数据后 ---------------
print("导入数据后 -------------")


from langchain_community.document_loaders import TextLoader
 
loader = TextLoader("demo2.txt")
loader.load()


from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
docs = [
    Document(
        page_content="A bunch of scientists bring back dinosaurs and mayhem breaks loose",
        metadata={"year": 1993, "rating": 7.7, "genre": "science fiction"},
    ),
    Document(
        page_content="Leo DiCaprio gets lost in a dream within a dream within a dream within a ...",
        metadata={"year": 2010, "director": "Christopher Nolan", "rating": 8.2},
    ),
]
vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings())
 
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import ChatOpenAI
 
metadata_field_info = [
    AttributeInfo(
        name="genre",
        description="The genre of the movie. One of ['science fiction', 'comedy', 'drama', 'thriller', 'romance', 'action', 'animated']",
        type="string",
    ),
    AttributeInfo(
        name="year",
        description="The year the movie was released",
        type="integer",
    ),
]
document_content_description = "Brief summary of a movie"
llm = ChatOpenAI(temperature=0)
retriever = SelfQueryRetriever.from_llm(
    llm, vectorstore, document_content_description, metadata_field_info,
)
 
# This example only specifies a filter
retriever.invoke("I want to watch a movie rated higher than 8.5")



from langchain_community.tools.tavily_search import TavilySearchResults
search = TavilySearchResults()
 
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
loader = WebBaseLoader("https://docs.smith.langchain.com/overview")
docs = loader.load()
documents = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)
vector = FAISS.from_documents(documents, OpenAIEmbeddings())
retriever = vector.as_retriever()
 
from langchain.tools.retriever import create_retriever_tool
retriever_tool = create_retriever_tool(
    retriever,
    "langsmith_search",
    "Search for information about LangSmith. For any questions about LangSmith, you must use this tool!",
)


from langchain_openai import ChatOpenAI
tools = [search, retriever_tool]
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
 
from langchain import hub
prompt = hub.pull("hwchase17/openai-functions-agent") # Get the prompt to use
 
from langchain.agents import create_openai_functions_agent
agent = create_openai_functions_agent(llm, tools, prompt)
 
from langchain.agents import AgentExecutor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

from langchain_core.messages import AIMessage, HumanMessage
agent_executor.invoke(
    {
        "chat_history": [
            HumanMessage(content="hi! my name is bob"),
            AIMessage(content="Hello Bob! How can I assist you today?"),
        ],
        "input": "what's my name?",
    }
)