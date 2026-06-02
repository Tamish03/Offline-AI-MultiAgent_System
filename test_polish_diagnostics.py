import os
import json
import numpy as np

from core.knowledge_base import KnowledgeBase
from agents.tool_planner_agent import ToolPlannerAgent
from core.tool_parser import ToolParser
from core.session_memory import SessionMemory
from core.ollama_client import chat


def run_diagnostics():
    print("=== OFFLINE AI OS DIAGNOSTICS ===\n")

    # 1. Ollama Connectivity
    print("1. Checking Ollama Connectivity...")
    try:
        response = chat("Respond with 'OK' and nothing else.", model="qwen2.5:1.5b")
        print(f"   Status: Success (Response: {response.strip()})")
    except Exception as e:
        print(f"   Status: Failed ({e})")
    print()

    # 2. Knowledge Base & Auto-Indexing
    print("2. Checking Knowledge Base Initialization...")
    kb = KnowledgeBase()
    topics = kb.list_topics()
    print(f"   Topics in KB: {topics}")
    print(f"   Vector store count: {kb.vector_store.count()} documents")
    print()

    # 3. Deterministic Tool Routing
    print("3. Checking Deterministic Tool Routing...")
    tp = ToolPlannerAgent()
    
    # Test file reading
    file_route = tp.decide_tool("please read file data/test.txt")
    print(f"   Read File Match: {file_route}")
    assert file_route["tool"] == "READ_FILE"
    assert file_route["filepath"] == "data/test.txt"

    # Test folder searching
    folder_route = tp.decide_tool("search folder 'data/output'")
    print(f"   Search Folder Match: {folder_route}")
    assert folder_route["tool"] == "SEARCH_FOLDER"
    assert folder_route["folder"] == "data/output"

    # Test Python execution
    python_route = tp.decide_tool("run python\n```python\nprint('hello')\n```")
    print(f"   Run Python Match: {python_route}")
    assert python_route["tool"] == "EXECUTE_PYTHON"
    assert "print('hello')" in python_route["code"]
    print("   Deterministic Routing: SUCCESS (0 LLM latency!)")
    print()

    # 4. Tool Parser Fences
    print("4. Checking Tool Parser Fence Stripping...")
    parser = ToolParser()
    code = parser.extract_python_code("execute code\n```python\nx = 10\nprint(x)\n```")
    print(f"   Extracted Code:\n---\n{code}\n---")
    assert "```" not in code
    assert "python" not in code.split("\n")[0]
    print()

    # 5. Session Memory
    print("5. Checking Session Memory...")
    session = SessionMemory(session_dir="data/sessions_test_diag")
    session.exchanges = []
    session.add_exchange("What is Python?", "Python is a language.")
    session.add_exchange("What is Java?", "Java is another language.")
    history = session.get_history()
    print(f"   History count: {len(history)} messages")
    assert len(history) == 4
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
    print()

    print("ALL DIAGNOSTICS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    run_diagnostics()
