from agents.tool_agent import ToolAgent

agent = ToolAgent()

files = agent.search_folder(
    "data"
)

print(files)