from agents.reviewer_agent import ReviewerAgent

reviewer = ReviewerAgent()

review = reviewer.review(
    """
    Vector databases are used in AI.
    They store embeddings.
    """
)

print(review)