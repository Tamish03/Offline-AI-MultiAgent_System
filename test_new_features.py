import os
import json
from pathlib import Path
from core.knowledge_base import KnowledgeBase
from core.session_memory import SessionMemory
from workflows.engine import WorkflowEngine


def run_tests():
    print("=== STARTING NEW FEATURES VERIFICATION ===\n")
    
    # Setup directories
    os.makedirs("data/test_sandbox", exist_ok=True)

    # ==============================
    # 1. TEST KNOWLEDGE GRAPH MAPPING
    # ==============================
    print("1. Testing Knowledge Graph Association...")
    kb = KnowledgeBase()
    
    # Clean old nodes if present
    kb.graph.remove_node("MongoDatabase")
    kb.graph.remove_node("NoSQL Systems")

    # Save two topics where the second one references the first
    kb.save_knowledge("MongoDatabase", "MongoDB is a document store database.")
    # This content references "MongoDatabase"
    kb.save_knowledge("NoSQL Systems", "NoSQL systems include MongoDatabase and key-value stores.")

    # Check graph
    graph_data = kb.graph.get_graph_data()
    print(f"   Nodes: {[n['id'] for n in graph_data['nodes']]}")
    print(f"   Links: {graph_data['links']}")

    # Verify link exists
    link_found = False
    for link in graph_data["links"]:
        if (link["source"] == "MongoDatabase" and link["target"] == "NoSQL Systems") or \
           (link["source"] == "NoSQL Systems" and link["target"] == "MongoDatabase"):
            link_found = True
            break
            
    assert link_found, "Knowledge Graph failed to link related topics!"
    print("   Knowledge Graph: SUCCESS")
    print()

    # ==============================
    # 2. TEST DETERMINISTIC WRITE_FILE TOOL
    # ==============================
    print("2. Testing Deterministic WRITE_FILE Tool...")
    engine = WorkflowEngine()
    
    test_filepath = "data/test_sandbox/output_code.py"
    if os.path.exists(test_filepath):
        os.remove(test_filepath)

    prompt = f"write file {test_filepath} code\n```python\n# sandbox run\nprint('sandbox')\n```"
    result = engine.execute_goal(prompt)
    
    print(f"   Result Output: {result.get('output')}")
    assert os.path.exists(test_filepath), "WRITE_FILE tool failed to create target file!"
    
    with open(test_filepath, "r") as f:
        content = f.read()
    
    assert "sandbox run" in content, "Written file contents did not match expected code!"
    print("   WRITE_FILE Tool: SUCCESS")
    print()

    # ==============================
    # 3. TEST DETERMINISTIC GREP_SEARCH TOOL
    # ==============================
    print("3. Testing Deterministic GREP_SEARCH Tool...")
    
    # We will search for the word 'sandbox' in 'data/test_sandbox'
    search_prompt = "grep search sandbox in data/test_sandbox"
    result = engine.execute_goal(search_prompt)
    
    print(f"   Grep Results:\n---\n{result.get('output')}\n---")
    assert "output_code.py" in result.get("output"), "GREP_SEARCH failed to find matching text in target folder!"
    print("   GREP_SEARCH Tool: SUCCESS")
    print()

    # ==============================
    # 4. TEST CONTEXT MEMORY COMPRESSION
    # ==============================
    print("4. Testing Session Context Summarization & Compression...")
    # Instantiate memory with low max_exchanges to force compression easily
    session = SessionMemory(max_exchanges=2, session_dir="data/sessions_test")
    
    # Clear old data
    session.exchanges = []
    session.summary_context = ""
    
    # Add exchanges. Limit is 2, so adding a 3rd will trigger compression of the oldest 3
    session.add_exchange("What is Python?", "Python is an interpreted high-level language.")
    session.add_exchange("What is the capital of France?", "The capital of France is Paris.")
    session.add_exchange("What is gravity?", "Gravity is a fundamental force of nature.")
    
    print(f"   Remaining exchanges: {session.count()}")
    print(f"   Summarized context: {session.summary_context}")
    
    # Verify exchanges were shifted and summary context was generated
    assert session.count() == 0, "Exchanges were not shifted out during compression!"
    assert len(session.summary_context) > 0, "Summary context was not generated!"
    print("   Session Compression: SUCCESS")
    print()

    print("ALL NEW PHASE 4 FEATURES COMPLETED & VERIFIED SUCCESSFULLY!")


if __name__ == "__main__":
    run_tests()
