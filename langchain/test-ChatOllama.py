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