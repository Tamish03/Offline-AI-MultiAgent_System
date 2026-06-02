"""
AI OS Interactive Chat

Single-process REPL.
Bypasses task queue for fast paths.
Streams LLM responses in real-time.

Usage:
    python chat.py
"""

import time
import requests

from agents.router_agent import RouterAgent
from workflows.engine import WorkflowEngine
from core.session_memory import SessionMemory
from core.learning_journal import LearningJournal
from config import OLLAMA_URL, DEFAULT_MODEL, EMBEDDING_MODEL


def print_banner():
    print()
    print("=" * 60)
    print()
    print("    OFFLINE AI OS")
    print("    Persistent Intelligence System")
    print()
    print("=" * 60)
    print()
    print("  Commands:")
    print("    status    — Show system health and status")
    print("    topics    — List stored knowledge")
    print("    stats     — Show AI statistics")
    print("    history   — Conversation history")
    print("    clear     — Clear conversation")
    print("    quit      — Exit")
    print()
    print("=" * 60)
    print()


def check_ollama_health():
    """Startup health check for Ollama and required models."""
    print("Performing Startup Diagnostics...")
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if resp.status_code == 200:
            print("  [OK] Ollama is running.")
            models = [m["name"] for m in resp.json().get("models", [])]
            
            # Check models
            qwen_ok = any(DEFAULT_MODEL in m for m in models)
            nomic_ok = any(EMBEDDING_MODEL in m for m in models)
            
            if not qwen_ok:
                print(f"  [WARN] Default model '{DEFAULT_MODEL}' is not pulled.")
                print(f"         Please run: ollama pull {DEFAULT_MODEL}")
            else:
                print(f"  [OK] Default model '{DEFAULT_MODEL}' is active.")
                
            if not nomic_ok:
                print(f"  [WARN] Embedding model '{EMBEDDING_MODEL}' is not pulled.")
                print(f"         Please run: ollama pull {EMBEDDING_MODEL}")
            else:
                print(f"  [OK] Embedding model '{EMBEDDING_MODEL}' is active.")
        else:
            print(f"  [WARN] Ollama returned status code {resp.status_code}.")
    except Exception:
        print("  [ERROR] Ollama is not running.")
        print(f"          Ensure Ollama is started at {OLLAMA_URL}")
    print()


def handle_command(
    command,
    session,
    journal
):
    """Handle special commands. Returns True if handled."""

    cmd = command.lower().strip()

    # ==============================
    # STATUS
    # ==============================
    if cmd == "status":
        print("\n--- System Status ---\n")
        # Ollama check
        try:
            resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            if resp.status_code == 200:
                print("  Ollama Status: Running")
                models = [m["name"] for m in resp.json().get("models", [])]
                print(f"  Loaded Models: {', '.join(models)}")
                
                # Check for our specific models
                missing = []
                qwen_ok = any(DEFAULT_MODEL in m for m in models)
                nomic_ok = any(EMBEDDING_MODEL in m for m in models)
                if not qwen_ok:
                    missing.append(DEFAULT_MODEL)
                if not nomic_ok:
                    missing.append(EMBEDDING_MODEL)
                
                if missing:
                    print(f"  Warning: Missing models: {', '.join(missing)}")
                else:
                    print("  Model Check: All required models available")
            else:
                print(f"  Ollama Status: Offline (HTTP {resp.status_code})")
        except Exception:
            print("  Ollama Status: Offline (Not Running)")

        # KB size
        from core.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        topics = kb.list_topics()
        print(f"  Knowledge Base: {len(topics)} topics")
        print(f"  Vector Database: {kb.vector_store.count()} vectors")

        # Session memory size
        print(f"  Active Session: {session.count()} exchanges")

        # Queue size
        try:
            from core.task_queue import TaskQueue
            queue = TaskQueue()
            print(f"  Task Queue:")
            print(f"    Pending: {queue.pending_count()}")
            print(f"    Running: {queue.running_count()}")
            print(f"    Completed: {queue.completed_count()}")
            print(f"    Failed: {queue.failed_count()}")
        except Exception:
            print("  Task Queue: Not Available")

        print("\n---\n")
        return True

    # ==============================
    # TOPICS
    # ==============================
    if cmd == "topics":
        from core.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        topics = kb.list_topics()
        if topics:
            print("\n--- Stored Knowledge ---\n")
            for topic in topics:
                print(f"  - {topic}")
            print(f"\n  Total: {len(topics)} topics")
        else:
            print("\nNo knowledge stored yet.")
        print()
        return True

    # ==============================
    # STATS
    # ==============================
    if cmd == "stats":
        journal.display_stats()
        return True

    # ==============================
    # HISTORY
    # ==============================
    if cmd == "history":
        session.display_history()
        return True

    # ==============================
    # CLEAR
    # ==============================
    if cmd == "clear":
        session.exchanges = []
        print("\nConversation cleared.\n")
        return True

    return False


def main():
    print_banner()
    check_ollama_health()

    engine = WorkflowEngine()
    session = SessionMemory()
    journal = LearningJournal()

    while True:
        try:
            goal = input("\n> ").strip()
            if not goal:
                continue

            if goal.lower() in ("quit", "exit", "q"):
                saved = session.save_session()
                if saved:
                    print(f"\nSession saved: {saved}")
                print("\nGoodbye.\n")
                break

            # ==============================
            # SPECIAL COMMANDS
            # ==============================
            if handle_command(goal, session, journal):
                continue

            # ==============================
            # EXECUTE GOAL
            # ==============================
            intent = engine.router.classify(goal)

            # Fast paths: stream directly
            if intent in ("RESPOND", "CONTENT", "QUESTION"):
                print()
                result = engine.execute_goal(
                    goal,
                    stream=True,
                    history=session.get_history()
                )

                generator = result.get("output")
                response_parts = []
                
                if generator and hasattr(generator, "__iter__") and not isinstance(generator, str):
                    for token in generator:
                        print(token, end="", flush=True)
                        response_parts.append(token)
                    print()
                    response = "".join(response_parts)
                else:
                    response = generator or ""

                # Show file save for content
                if intent in ("CONTENT", "QUESTION"):
                    file = result.get("file")
                    if file:
                        print(f"\nSaved: {file}")

                # Show knowledge hit status
                if result.get("knowledge_hit"):
                    print("\n[Knowledge Reuse — No LLM needed]")

                # Store in session
                session.add_exchange(goal, response or "")

            # Workflow: full pipeline
            else:
                result = engine.execute_goal(
                    goal,
                    history=session.get_history()
                )

                if result.get("file"):
                    print(f"\nOutput: {result['file']}")

                session.add_exchange(
                    goal,
                    f"[WORKFLOW completed] {result.get('file', '')}"
                )

        except KeyboardInterrupt:
            saved = session.save_session()
            if saved:
                print(f"\n\nSession saved: {saved}")
            print("\nInterrupted. Goodbye.\n")
            break

        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
