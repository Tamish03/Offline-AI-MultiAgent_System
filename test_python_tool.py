from tools.tool_manager import ToolManager

tools = ToolManager()

code = """
print("Hello AI OS")
print(5 + 10)
"""

result = tools.execute_python(
    code
)

print(result)