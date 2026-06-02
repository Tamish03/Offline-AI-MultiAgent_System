import json
from pathlib import Path
from datetime import datetime


class SessionMemory:
    """
    Conversation history for the current session.

    Stores exchanges as message pairs.
    Auto-compresses oldest exchanges to prevent context limit bloat.
    Persists to disk between sessions.
    """

    def __init__(
        self,
        max_exchanges=10,
        session_dir="data/sessions"
    ):
        self.max_exchanges = max_exchanges
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.exchanges = []
        self.summary_context = ""

        # Auto-resume latest session
        self._load_latest_session()

    def _load_latest_session(self):
        """Load the most recent session file from disk."""
        try:
            files = list(self.session_dir.glob("*.json"))
            if not files:
                return
            # Sort by modification time
            files.sort(key=lambda x: x.stat().st_mtime)
            latest_file = files[-1]
            
            with open(latest_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                self.summary_context = data.get("summary_context", "")
                self.exchanges = data.get("exchanges", [])
            elif isinstance(data, list):
                # Legacy compatibility
                self.exchanges = data
                self.summary_context = ""
        except Exception:
            pass

    def add_exchange(
        self,
        user_input,
        ai_response
    ):
        """Store one user-AI exchange and compress if limit exceeded."""
        self.exchanges.append({
            "user": user_input,
            "assistant": ai_response,
            "timestamp": datetime.now().isoformat()
        })

        if len(self.exchanges) > self.max_exchanges:
            self._compress_history()

    def _compress_history(self):
        """
        Compresses the oldest 3 exchanges into a running summary
        using the local qwen2.5:1.5b model, freeing up context space.
        """
        if len(self.exchanges) <= self.max_exchanges:
            return

        to_compress = self.exchanges[:3]
        self.exchanges = self.exchanges[3:]

        text_to_summarize = ""
        for ex in to_compress:
            text_to_summarize += f"User: {ex['user']}\nAI: {ex['assistant']}\n\n"

        prompt = f"""
Summarize the key facts, user preferences, facts, and conclusions from the following conversation.
Keep it extremely concise, brief, and factual. No explanations or meta-commentary.

Prior Summary Context:
{self.summary_context or 'None'}

New Exchanges:
{text_to_summarize}

Return a single consolidated summary paragraph containing all essential context.
"""
        try:
            from core.ollama_client import chat
            summary = chat(prompt, model="qwen2.5:1.5b", temperature=0.3)
            if summary:
                self.summary_context = summary.strip()
        except Exception:
            pass

    def get_history(self):
        """Return message list for Ollama history parameter."""
        messages = []

        if self.summary_context:
            messages.append({
                "role": "system",
                "content": f"Prior Conversation Summary: {self.summary_context}"
            })

        for ex in self.exchanges:
            messages.append({
                "role": "user",
                "content": ex["user"]
            })
            messages.append({
                "role": "assistant",
                "content": ex["assistant"][:500]  # Limit assistant context size
            })

        return messages

    def get_context_summary(self):
        """Short summary of recent conversation."""
        lines = []
        if self.summary_context:
            lines.append(f"[SUMMARY] {self.summary_context[:80]}...")
            
        recent = self.exchanges[-3:]
        for ex in recent:
            lines.append(f"User: {ex['user'][:80]}")
            lines.append(f"AI: {ex['assistant'][:80]}")

        return "\n".join(lines)

    def save_session(self):
        """Save current session to disk."""
        if not self.exchanges and not self.summary_context:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.session_dir / f"session_{timestamp}.json"

        session_data = {
            "summary_context": self.summary_context,
            "exchanges": self.exchanges
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def display_history(self):
        """Print conversation history."""
        if not self.exchanges and not self.summary_context:
            print("\nNo conversation history.\n")
            return

        print("\n--- Conversation History ---\n")
        if self.summary_context:
            print(f"Long-term Summary Context:\n  {self.summary_context}\n")
            print("-" * 30)

        for i, ex in enumerate(self.exchanges, start=1):
            print(f"[{i}] You: {ex['user']}")
            print(
                f"    AI: {ex['assistant'][:120]}"
                f"{'...' if len(ex['assistant']) > 120 else ''}"
            )
            print()
        print("---\n")

    def count(self):
        return len(self.exchanges)

    def load_session_by_name(self, filename):
        """Load a specific session file by its filename."""
        filepath = self.session_dir / filename
        if not filepath.exists():
            return False
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                self.summary_context = data.get("summary_context", "")
                self.exchanges = data.get("exchanges", [])
            elif isinstance(data, list):
                self.exchanges = data
                self.summary_context = ""
            return True
        except Exception:
            return False

    def clear_session(self):
        """Clear current active in-memory session."""
        self.exchanges = []
        self.summary_context = ""
