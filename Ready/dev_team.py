import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama, OllamaEmbeddings

from crewai import LLM
# 配置LLM（这里可以用OpenAI，也可以用本地的大模型）
# 记得换成你自己的API Key
#llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.7)
#llm = ChatOllama(model="llama3", temperature=0.7,base_url="http://localhost:11434")

llm = LLM(
    model="ollama/llama3",
    base_url="http://localhost:11434"
)

# 1. 定义产品经理 Agent
product_manager = Agent(
    role='资深产品经理',
    goal='分析用户需求，产出清晰、详细的软件需求文档(PRD)',
    backstory="""你是一名拥有10年经验的互联网产品经理。
    你擅长挖掘用户痛点，并且能把模糊的一句话需求，拆解成程序员能看懂的技术文档。
    你对细节要求极高，不允许有逻辑漏洞。""",
    verbose=True, # 让他干活时多唠叨几句，我们在终端能看到
    allow_delegation=False,
    llm=llm
)

# 2. 定义Python开发 Agent
developer = Agent(
    role='首席Python架构师',
    goal='根据需求文档，编写高质量、可运行的Python代码',
    backstory="""你是一名顶级黑客和Python专家。
    你只写优雅、高效、符合PEP8规范的代码。
    你能够解决复杂算法问题，并且会给关键逻辑加上详细注释。""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

llm2 = LLM(
    model="ollama/llama3.2:3b-instruct-fp16",
    base_url="http://localhost:11434"
)

# 3. 定义测试工程师 Agent
qa_engineer = Agent(
    role='质量保证(QA)专家',
    goal='审查代码，寻找Bug，确保代码能完美运行',
    backstory="""你是一名以“找茬”为乐的测试专家。
    你会严格审查开发人员的代码，检查是否存在安全隐患、逻辑死循环或语法错误。
    如果发现问题，你会毫不留情地打回重写。""",
    verbose=True,
    allow_delegation=False,
    llm=llm2
)


#三、 派发任务 (Tasks)
#有了人，还得有活儿。 我们需要定义任务，并指定谁来做。


    # 任务1：需求分析
task_analysis = Task(
    description="""
    用户想要一个'基于命令行的贪吃蛇游戏'。
    请分析该需求，定义游戏规则、控制方式（WASD）、界面布局以及计分规则。
    产出一份简短但核心逻辑清晰的需求列表。
    """,
    agent=product_manager,
    expected_output="一份包含游戏规则和功能点的需求列表文本。"
)

# 任务2：编写代码
task_coding = Task(
    description="""
    使用Python的curses库或标准库实现上述贪吃蛇游戏。
    注意：代码必须是一个完整的、可直接运行的.py文件内容。
    处理好蛇撞墙、吃到食物变长等逻辑。
    """,
    agent=developer,
    expected_output="完整的Python代码字符串。"
)

# 任务3：代码审查
task_review = Task(
    description="""
    检查开发人员编写的代码。
    1. 检查是否有语法错误。
    2. 检查逻辑是否符合PM的需求。
    3. 如果代码完美，直接输出代码；如果有问题，列出修改建议。
    """,
    agent=qa_engineer,
    expected_output="经过审查的最终Python代码，或Bug修改建议。"
)


#四、 组建团队并开工 (Crew)
#这是最燃的一步。 我们将这些Agent串联起来，组成一个 Crew（团队）。


    # 组建团队
dev_team = Crew(
    agents=[product_manager, developer, qa_engineer],
    tasks=[task_analysis, task_coding, task_review],
    process=Process.sequential, # 顺序执行：PM -> Dev -> QA
    verbose=True,
    tracing=True   # ✅ 就在这里

)

print(" 虚拟软件开发团队正在集结...")
print(" 老板发布任务：做一个贪吃蛇游戏")

# 开工！
result = dev_team.kickoff()

print("\n\n########################")
print("✅ 最终交付结果：")
print(result)


'''
# 安全代码审计

你是一名资深安全工程师。用户请求代码审计时，按以下清单逐项检查。

## 审计清单

### 1. 注入类漏洞
- [ ] SQL 注入：是否用参数化查询
- [ ] 命令注入：shell 命令参数有没有转义
- [ ] XSS：用户输入有没有转义

### 2. 认证与授权
- [ ] 有没有未授权访问的接口
- [ ] 密码是不是明文存储
- [ ] Session/Token 生成安全吗

### 3. 敏感信息
- [ ] 有没有硬编码的密钥、密码
- [ ] 日志里有没有敏感信息
- [ ] 错误信息会不会泄露内部细节

### 4. 其他
- [ ] 依赖有没有已知漏洞
- [ ] 文件上传有没有类型/大小限制
- [ ] 有没有 CSRF 防护

## 输出格式

按风险等级分类：

**高风险**：立即修
**中风险**：尽快修
**低风险**：建议改
**安全**：没问题

每个问题给出：
1. 问题是什么
2. 在哪一行
3. 怎么修
'''