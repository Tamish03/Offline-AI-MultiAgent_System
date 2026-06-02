import os
import sys
import time
import threading
from core.knowledge_base import KnowledgeBase
from agents.question_agent import QuestionAgent
from agents.research_agent import ResearchAgent
from workflows.engine import WorkflowEngine

def test_semantic_caching_and_rag():
    print("\n--- Testing Semantic Caching and RAG Path ---")
    kb = KnowledgeBase()
    agent = QuestionAgent()
    
    # 1. Clear any existing test knowledge
    test_topic = "Python Decorators Guide"
    kb.delete_knowledge(test_topic)
    
    # Verify deletion
    assert kb.get_knowledge(test_topic) is None, "Failed to delete test knowledge"
    
    # 2. First Run: Standard LLM Research (no cache, low similarity)
    print("\n[Run 1] Requesting new topic (expect standard research + save to KB)...")
    start = time.time()
    ans1, hit1 = agent.answer(test_topic)
    duration1 = time.time() - start
    print(f"Result hit: {hit1}, Duration: {duration1:.2f}s")
    assert not hit1, "Expected knowledge cache miss on first run"
    assert len(ans1) > 0, "Expected a valid research response"
    
    # 3. Second Run: Exact Cache Hit (expect instant response)
    print("\n[Run 2] Requesting exact same topic (expect exact cache hit)...")
    start = time.time()
    ans2, hit2 = agent.answer(test_topic)
    duration2 = time.time() - start
    print(f"Result hit: {hit2}, Duration: {duration2:.4f}s")
    assert hit2, "Expected exact cache hit on second run"
    assert ans1 == ans2, "Expected cached content to match original research"
    assert duration2 < 0.1, f"Expected cache hit to be near-instant (got {duration2:.4f}s)"

    # 4. Third Run: Semantic Cache Hit >= 0.80 (expect instant response)
    similar_topic_high = "A Guide to Python Decorators"
    print(f"\n[Run 3] Requesting high similarity topic: '{similar_topic_high}' (expect semantic hit >= 0.80)...")
    start = time.time()
    ans3, hit3 = agent.answer(similar_topic_high)
    duration3 = time.time() - start
    print(f"Result hit: {hit3}, Duration: {duration3:.4f}s")
    # Clean up newly saved semantic topic if created, but it should hit semantic cache
    kb.delete_knowledge(similar_topic_high)
    
    # 5. Fourth Run: Loose Semantic Match (0.30 <= score < 0.80) -> expect RAG context injection
    similar_topic_loose = "python function wrapping techniques and concepts"
    print(f"\n[Run 4] Requesting loose topic: '{similar_topic_loose}' (expect loose match + RAG)...")
    start = time.time()
    ans4, hit4 = agent.answer(similar_topic_loose)
    duration4 = time.time() - start
    print(f"Result hit: {hit4}, Duration: {duration4:.2f}s")
    assert not hit4, "Expected knowledge cache miss for loose topic"
    kb.delete_knowledge(similar_topic_loose)
    
    # Cleanup main test topic
    kb.delete_knowledge(test_topic)
    print("Semantic cache and RAG testing completed successfully!")

def test_token_generator_streaming():
    print("\n--- Testing Generator Token Streaming ---")
    engine = WorkflowEngine()
    
    goal = "What is the capital of France?"
    meta = {}
    print(f"Executing goal: '{goal}' with stream=True...")
    start = time.time()
    result = engine.execute_goal(goal, stream=True, meta=meta)
    
    intent = result.get("intent")
    output_generator = result.get("output")
    print(f"Detected Intent: {intent}")
    
    assert intent == "QUESTION", f"Expected intent to be QUESTION, got {intent}"
    assert hasattr(output_generator, "__iter__"), "Expected engine output to be a generator/iterator"
    
    print("Streaming tokens: ", end="", flush=True)
    tokens = []
    for token in output_generator:
        print(token, end="", flush=True)
        tokens.append(token)
    print()
    
    duration = time.time() - start
    print(f"Streaming finished. Total duration: {duration:.2f}s, tokens received: {len(tokens)}")
    assert len(tokens) > 0, "Expected to receive streaming tokens"
    
    # Verify metadata contains output file path
    assert "file" in meta and meta["file"], "Expected metadata to contain output file path"
    print(f"Output saved to: {meta['file']}")
    assert os.path.exists(meta["file"]), "Output markdown file should exist on disk"

def test_parallel_research():
    print("\n--- Testing Parallel Research Agent Execution ---")
    researcher = ResearchAgent()
    
    # We test research tasks in parallel.
    # Parallel research agent uses ThreadPoolExecutor under the hood when deep_research is called.
    sub_queries = [
        "History of artificial intelligence",
        "Recent breakthroughs in nuclear fusion",
        "Basics of quantum computing"
    ]
    
    # Join queries into a research task
    composite_query = "\n".join([f"- Research: {q}" for q in sub_queries])
    
    print("Running parallel research on queries:")
    for q in sub_queries:
        print(f"  * {q}")
        
    start = time.time()
    research_result = researcher.deep_research(composite_query)
    duration = time.time() - start
    
    print(f"\nParallel Deep Research completed in {duration:.2f}s")
    assert len(research_result) > 0, "Expected non-empty research result"
    print("Sample Output (first 200 chars):")
    print(research_result[:200] + "...")

if __name__ == "__main__":
    print("==========================================")
    print("  OFFLINE AI OS DIAGNOSTICS & VERIFICATION")
    print("==========================================")
    
    try:
        test_semantic_caching_and_rag()
        test_token_generator_streaming()
        test_parallel_research()
        print("\n==========================================")
        print("  ALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
        print("==========================================")
    except Exception as e:
        import traceback
        print("\n==========================================")
        print("  VERIFICATION FAILED:")
        traceback.print_exc()
        print("==========================================")
        sys.exit(1)
