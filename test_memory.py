from core.memory import MemoryManager

memory = MemoryManager()

memory.store(
    "Vector databases store embeddings for semantic search.",
    "doc1"
)

memory.store(
    "SQLite is useful for lightweight local databases.",
    "doc2"
)

memory.store(
    "Qwen2.5 1.5B is a lightweight local language model.",
    "doc3"
)

results = memory.search(
    "How do embeddings work?"
)

print(results)