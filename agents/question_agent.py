from agents.base_agent import BaseAgent
from core.knowledge_base import KnowledgeBase


class QuestionAgent(BaseAgent):
    """
    Knowledge-First Intelligence Path with Semantic Caching and RAG.

    1. Search KB (exact match or semantic score >= 0.80 -> instant return)
    2. Loose semantic match (0.30 <= score < 0.80 -> RAG with context)
    3. Else -> Standard LLM research
    4. Save new research to KB for future reuse
    """

    def __init__(self):
        super().__init__(
            name="Question Agent",
            role="Knowledge Specialist",
            system_prompt="""
You are a knowledgeable AI assistant.

Rules:
- Answer the question directly.
- Be clear and structured.
- Use bullet points where helpful.
- Include practical examples.
- Keep answers concise (max 400 words).
- Do not create reports.
- Do not add unnecessary sections.
"""
        )
        self.knowledge_base = KnowledgeBase()

    def answer(
        self,
        question,
        history=None,
        status_callback=None
    ):
        """
        Answer a question using semantic caching and RAG.
        Returns (response, knowledge_hit).
        """
        if status_callback:
            status_callback("Checking exact knowledge cache...")

        # 1. Check exact match
        exact = self.knowledge_base.get_knowledge(question)
        if exact:
            if status_callback:
                status_callback("Exact match found in cache. Retrieving...")
            print("\n[Exact Cache Hit] — Answering Instantly\n")
            return exact.get("content", ""), True

        if status_callback:
            status_callback("Performing semantic vector search...")

        # 2. Check semantic cache
        semantic_matches = self.knowledge_base.semantic_search(question)
        best_semantic = semantic_matches[0] if semantic_matches else None
        
        is_valid_match = False
        if best_semantic:
            query_words = set(self.knowledge_base._normalize_topic(question).split("_"))
            candidate_words = set(self.knowledge_base._normalize_topic(best_semantic.get("topic", "")).split("_"))
            overlap = query_words & candidate_words
            min_len = min(len(query_words), len(candidate_words))
            overlap_ratio = len(overlap) / min_len if min_len > 0 else 0.0
            if overlap_ratio >= 0.70:
                is_valid_match = True
            else:
                print(f"\n[Semantic Match Rejected: '{best_semantic.get('topic')}' vs '{question}'] — Overlap ratio {overlap_ratio:.2f} < 0.70\n")
        
        if best_semantic and is_valid_match:
            score = best_semantic.get("_semantic_score", 0)
            if score >= 0.80:
                if status_callback:
                    status_callback(f"High-confidence semantic cache hit ({score:.2f}). Retrieving...")
                print(f"\n[Semantic Cache Hit: {score:.2f}] — Answering Instantly\n")
                return best_semantic.get("content", ""), True

        # 3. Compile prompt (RAG vs Standard)
        if best_semantic and is_valid_match and 0.30 <= best_semantic.get("_semantic_score", 0) < 0.80:
            score = best_semantic.get("_semantic_score", 0)
            if status_callback:
                status_callback(f"Found related context ({score:.2f}). Generating RAG response...")
            print(f"\n[Loose KB Match: {score:.2f}] — Using Retrieval-Augmented Context\n")
            prompt = f"""
Answer the question based on the retrieved context below:

Retrieved Context:
{best_semantic.get("content", "")}

Question:
{question}

Provide:
1. Clear explanation
2. Key points
3. Practical example if relevant

Be concise.
"""
        else:
            if status_callback:
                status_callback("No cache hits. Researching topic via LLM...")
            print("\nNo Knowledge Found — Researching...\n")
            prompt = f"""
Answer this question:

{question}

Provide:
1. Clear explanation
2. Key points
3. Practical example if relevant

Be concise.
"""

        # 4. Execute LLM research
        result = self.think(prompt, history=history)

        # 5. Save to KB for reuse
        if status_callback:
            status_callback("Saving response to local knowledge base...")
        self.knowledge_base.save_knowledge(question, result)
        print("\nKnowledge Saved For Future Reuse\n")

        return result, False

    def answer_stream(
        self,
        question,
        history=None,
        status_callback=None
    ):
        """
        Stream answer. Returns (generator, knowledge_hit).
        Saves output to KB upon generator completion.
        """
        if status_callback:
            status_callback("Checking exact knowledge cache...")

        # 1. Check exact match
        exact = self.knowledge_base.get_knowledge(question)
        if exact:
            if status_callback:
                status_callback("Exact match found in cache. Retrieving...")
            print("\n[Exact Cache Hit] — Answering Instantly\n")
            def kb_generator():
                yield exact.get("content", "")
            return kb_generator(), True

        if status_callback:
            status_callback("Performing semantic vector search...")

        # 2. Check semantic cache
        semantic_matches = self.knowledge_base.semantic_search(question)
        best_semantic = semantic_matches[0] if semantic_matches else None
        
        is_valid_match = False
        if best_semantic:
            query_words = set(self.knowledge_base._normalize_topic(question).split("_"))
            candidate_words = set(self.knowledge_base._normalize_topic(best_semantic.get("topic", "")).split("_"))
            overlap = query_words & candidate_words
            min_len = min(len(query_words), len(candidate_words))
            overlap_ratio = len(overlap) / min_len if min_len > 0 else 0.0
            if overlap_ratio >= 0.70:
                is_valid_match = True
            else:
                print(f"\n[Semantic Match Rejected: '{best_semantic.get('topic')}' vs '{question}'] — Overlap ratio {overlap_ratio:.2f} < 0.70\n")
        
        if best_semantic and is_valid_match:
            score = best_semantic.get("_semantic_score", 0)
            if score >= 0.80:
                if status_callback:
                    status_callback(f"High-confidence semantic cache hit ({score:.2f}). Retrieving...")
                print(f"\n[Semantic Cache Hit: {score:.2f}] — Answering Instantly\n")
                def semantic_generator():
                    yield best_semantic.get("content", "")
                return semantic_generator(), True

        # 3. Compile prompt (RAG vs Standard)
        if best_semantic and is_valid_match and 0.30 <= best_semantic.get("_semantic_score", 0) < 0.80:
            score = best_semantic.get("_semantic_score", 0)
            if status_callback:
                status_callback(f"Found related context ({score:.2f}). Generating RAG response...")
            print(f"\n[Loose KB Match: {score:.2f}] — Using Retrieval-Augmented Context\n")
            prompt = f"""
Answer the question based on the retrieved context below:

Retrieved Context:
{best_semantic.get("content", "")}

Question:
{question}

Provide:
1. Clear explanation
2. Key points
3. Practical example if relevant

Be concise.
"""
        else:
            if status_callback:
                status_callback("No cache hits. Researching topic via LLM...")
            print("\nNo Knowledge Found — Researching...\n")
            prompt = f"""
Answer this question:

{question}

Provide:
1. Clear explanation
2. Key points
3. Practical example if relevant

Be concise.
"""

        # 4. Stream and save wrapper
        def stream_saver():
            full_text = []
            for token in self.think_stream(prompt, history=history):
                yield token
                full_text.append(token)
            
            # Save to KB on completion
            if status_callback:
                status_callback("Saving response to local knowledge base...")
            result = "".join(full_text)
            self.knowledge_base.save_knowledge(question, result)
            print("\nKnowledge Saved For Future Reuse")

        return stream_saver(), False
