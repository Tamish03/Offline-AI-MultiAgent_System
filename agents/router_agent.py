import re

from agents.base_agent import BaseAgent


class RouterAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Router Agent",
            role="Intent Router",
            system_prompt=""
        )

      

        self.respond_keywords = [

            "hello",
            "hey",

            "how are you",

            "good morning",
            "good afternoon",
            "good evening",

            "thank you",
            "thanks",

            "bye",
            "goodbye",
        ]

        # Short greetings that need
        # exact or start-of-string match

        self.respond_exact = [
            "hi",
            "hey",
        ]

        

        self.content_keywords = [

            "linkedin post",
            "post for linkedin",

            "blog post",
            "blog",

            "article",

            "tweet",
            "thread",

            "email",
            "newsletter",

            "product description",

            "caption",

            "social media post",

            "proposal",

            "cover letter",
        ]

       

        self.question_keywords = [

            "what is",
            "what are",
            "what does",
            "what was",

            "how does",
            "how do",
            "how is",

            "why is",
            "why do",
            "why does",

            "who is",
            "who was",

            "when was",
            "when is",

            "where is",
            "where was",

            "explain",
            "define",
            "describe",

            "tell me about",
            "tell me what",

            "meaning of",

            "difference between",
        ]


        self.workflow_keywords = [

            # Research

            "research",
            "reserach",
            "reseach",

            "study",
            "analyze",
            "analyse",
            "analize",

            "investigate",
            "investigte",

            "compare",

            # Workflow

            "report",
            "documentation",
            "workflow",
            "roadmap",

            "deep research",

            "review and improve",

            # Knowledge Tasks

            "learn about",
            "tell me everything about",
            "explain in detail",
            "full analysis",
            "detailed analysis",
        ]

    def _word_match(
        self,
        keyword,
        text
    ):
        """
        Match keyword with word boundaries.
        Prevents 'hi' matching 'machine'.
        """

        pattern = (
            r"(?:^|[\s,;!?.])"
            + re.escape(keyword)
            + r"(?:$|[\s,;!?.])"
        )

        return bool(
            re.search(pattern, text)
        )

    def classify(
        self,
        goal
    ):

        goal_lower = (
            goal
            .strip()
            .lower()
        )


        # Exact short greetings

        goal_words = goal_lower.split()

        if (
            goal_words
            and goal_words[0] in
            self.respond_exact
        ):
            return "RESPOND"

        for keyword in self.respond_keywords:

            if self._word_match(
                keyword,
                goal_lower
            ):
                return "RESPOND"


        for keyword in self.content_keywords:

            if keyword in goal_lower:

                return "CONTENT"


        for keyword in self.workflow_keywords:

            if self._word_match(
                keyword,
                goal_lower
            ):
                return "WORKFLOW"

      

        for keyword in self.question_keywords:

            if keyword in goal_lower:

                return "QUESTION"

       

        if len(goal_words) >= 5:

            return "QUESTION"


        return "RESPOND"
