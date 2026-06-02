from agents.research_agent import ResearchAgent

agent = ResearchAgent()

print(
    agent.research(
        "Vector Databases"
    )
)

print("\n\n--- SECOND QUERY ---\n\n")

print(
    agent.research(
        "Embeddings"
    )
)