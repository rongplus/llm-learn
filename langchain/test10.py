from langchain_ollama import OllamaLLM

#Part1 初始化Ollama
#------------Define  ollama------------
#方法1 使用本地的llama3
ollama = OllamaLLM(base_url='http://localhost:11434', model="llama3")
#方法2 使用网上的llama3
#ollama = OllamaLLM(model="llama3")
#-----------end define ollama--------------

# 使用Ollama进行简单的查询
response = ollama.invoke("why is the sky blue")

# 打印查询结果
print(response)


#Part2 使用WebBaseLoader加载文档
from langchain.document_loaders import WebBaseLoader

# 指定要加载的网页URL
url = "https://www.gutenberg.org/files/1727/1727-h/1727-h.htm"

# 创建WebBaseLoader实例
loader = WebBaseLoader(url)

# 加载文档
data = loader.load()

# 打印加载的文档前100个字符，以验证是否成功加载
print(data[:100])

#Part 3 文档分割