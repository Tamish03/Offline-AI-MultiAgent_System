from agents.writer_agent import WriterAgent

writer = WriterAgent()

output = writer.write(
    topic="Vector Databases",
    research="""
Vector databases store embeddings.
Used in semantic search.
Common tools are ChromaDB and Pinecone.
"""
)

print(output)