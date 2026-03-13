# 配置好同级文件夹下.env中的大模型API
from dotenv import load_dotenv
load_dotenv()

from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools import MemoryTool, RAGTool

# 创建工具注册表
tool_registry = ToolRegistry()

# 添加记忆工具
memory_tool = MemoryTool(user_id="user123")
tool_registry.register_tool(memory_tool)

# 添加RAG工具
rag_tool = RAGTool(knowledge_base_path="./knowledge_base")
tool_registry.register_tool(rag_tool)

# 创建LLM实例
llm = HelloAgentsLLM()

# 创建Agent
agent = SimpleAgent(
    name="智能助手",
    llm=llm,
    system_prompt="你是一个有记忆和知识检索能力的AI助手",
    tool_registry=tool_registry,
    enable_tool_calling=True
)

# 为Agent配置工具
# agent.tool_registry = tool_registry

# 开始对话
# response = agent.run("你好！请记住我叫张三，我是一名Python开发者")
# print(response)

# 第一次对话
response1 = agent.run("我叫张三，正在学习Python，目前掌握了基础语法")
print(response1)  # "很好！Python基础语法是编程的重要基础..."
 
print("---- 第二次对话 ----")

# 第二次对话（新的会话）
response2 = agent.run("你还记得我是谁？我的学习进度吗？")
print(response2)  # "抱歉，我不知道您的学习进度..."