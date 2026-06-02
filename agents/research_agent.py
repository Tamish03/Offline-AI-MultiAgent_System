import json
import re

from agents.base_agent import BaseAgent

from core.knowledge_base import KnowledgeBase


class ResearchAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Research Agent",
            role="Research Specialist",
            system_prompt="""
You are an expert researcher.

Provide:

1. Explanation
2. Key Concepts
3. Important Facts
4. Practical Applications

Be structured.
"""
        )

        self.knowledge_base = (
            KnowledgeBase()
        )

    def research(
        self,
        topic
    ):
        """
        Standard research.

        Knowledge-first approach:
        check KB before LLM.
        """

        

        existing = (
            self.knowledge_base
            .get_knowledge(
                topic
            )
        )

        if existing:

            print(
                "\nKnowledge Found In "
                "Knowledge Base\n"
            )

            return existing[
                "content"
            ]

        

        smart_match = (
            self.knowledge_base
            .smart_search(topic)
        )

        if smart_match:

            content = smart_match.get(
                "content",
                ""
            )

            if content and len(content) > 50:

                print(
                    "\nRelevant Knowledge Found\n"
                )

                return content

       

        print(
            "\nNo Knowledge Found. "
            "Researching...\n"
        )

        result = self.think(
            f"""
Research this topic:

{topic}

Provide:

1. Explanation
2. Key Concepts
3. Important Facts
4. Practical Applications
"""
        )

        self.knowledge_base.save_knowledge(
            topic,
            result
        )

        print(
            "\nKnowledge Saved To "
            "Knowledge Base\n"
        )

        return result

    def deep_research(
        self,
        topic
    ):
        """
        Multi-step research for
        WORKFLOW intent.

        1. Main research
        2. Identify 2 sub-topics
        3. Research sub-topics
        4. Combine findings

        Deterministic limits:
        max 2 sub-topics, depth 1.
        """

        print(
            "\n--- Deep Research Mode ---\n"
        )


        print("Step 1: Main Research\n")

        main_research = self.research(topic)

      

        print(
            "\nStep 2: Identifying "
            "Sub-Topics\n"
        )

        subtopic_response = self.think(
            f"""
Given this topic: {topic}

What are 2 important sub-topics
that would deepen understanding?

Return ONLY a JSON array of strings.
Example: ["sub-topic 1", "sub-topic 2"]
"""
        )

        sub_topics = (
            self._parse_subtopics(
                subtopic_response
            )
        )


        from concurrent.futures import ThreadPoolExecutor

        print("\nStep 3: Researching Sub-Topics in Parallel...\n")

        sub_research = []

        with ThreadPoolExecutor(max_workers=2) as executor:
            
            # Map sub-topics to research calls
            futures = {
                executor.submit(self.research, sub): sub 
                for sub in sub_topics
            }
            
            for i, future in enumerate(futures, start=1):
                
                sub = futures[future]
                
                try:
                    
                    result = future.result()
                    
                    sub_research.append(
                        f"### {sub}\n\n{result}"
                    )
                    
                    print(f"  [OK] Research completed for: {sub}")
                    
                except Exception as e:
                    
                    print(f"  [ERROR] Research failed for '{sub}': {e}")

    

        combined = (
            f"# {topic}\n\n"
            f"{main_research}\n\n"
        )

        if sub_research:

            combined += (
                "## Additional Research\n\n"
                + "\n\n".join(sub_research)
            )

        print(
            "\n--- Deep Research Complete ---\n"
        )

        return combined

    def _parse_subtopics(
        self,
        response
    ):
        """
        Extract sub-topic list from
        LLM response.

        Deterministic: max 2 sub-topics.
        """

        response = re.sub(
            r"```json|```",
            "",
            response,
            flags=re.IGNORECASE
        ).strip()

        try:

            topics = json.loads(response)

            if isinstance(topics, list):

                return [
                    str(t).strip()
                    for t in topics[:2]
                    if str(t).strip()
                ]

        except Exception:
            pass

        match = re.search(
            r"\[.*\]",
            response,
            re.DOTALL
        )

        if match:

            try:

                topics = json.loads(
                    match.group()
                )

                return [
                    str(t).strip()
                    for t in topics[:2]
                    if str(t).strip()
                ]

            except Exception:
                pass

        return []
