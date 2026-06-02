from core.knowledge_base import KnowledgeBase

kb = KnowledgeBase()

kb.save_knowledge(
    "Vector Databases",
    "Vector databases store embeddings."
)

print(
    kb.get_knowledge(
        "Vector Databases"
    )
)

print(
    kb.list_topics()
)