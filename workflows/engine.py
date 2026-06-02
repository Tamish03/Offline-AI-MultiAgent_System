import time

from agents.router_agent import RouterAgent

from core.tool_router import ToolRouter
from core.tool_parser import ToolParser

from core.checkpoint import CheckpointManager
from core.output_manager import OutputManager

from core.tool_memory import ToolMemory
from core.learning_journal import LearningJournal


class WorkflowEngine:

    def __init__(self):

      

        self.router = RouterAgent()

        self.tool_router = ToolRouter()

        self.tool_parser = ToolParser()

        self.checkpoints = CheckpointManager()

        self.output_manager = OutputManager()

        self.tool_memory = ToolMemory()

        self.journal = LearningJournal()

        

        self._responder = None
        self._content_agent = None
        self._question_agent = None
        self._planner = None
        self._researcher = None
        self._writer = None
        self._reviewer = None
        self._reflection = None
        self._tool_planner = None
        self._tool_agent = None

    

    @property
    def responder(self):
        if self._responder is None:
            from agents.response_agent import ResponseAgent
            self._responder = ResponseAgent()
        return self._responder

    @property
    def content_agent(self):
        if self._content_agent is None:
            from agents.content_agent import ContentAgent
            self._content_agent = ContentAgent()
        return self._content_agent

    @property
    def question_agent(self):
        if self._question_agent is None:
            from agents.question_agent import QuestionAgent
            self._question_agent = QuestionAgent()
        return self._question_agent

    @property
    def planner(self):
        if self._planner is None:
            from agents.planner_agent import PlannerAgent
            self._planner = PlannerAgent()
        return self._planner

    @property
    def researcher(self):
        if self._researcher is None:
            from agents.research_agent import ResearchAgent
            self._researcher = ResearchAgent()
        return self._researcher

    @property
    def writer(self):
        if self._writer is None:
            from agents.writer_agent import WriterAgent
            self._writer = WriterAgent()
        return self._writer

    @property
    def reviewer(self):
        if self._reviewer is None:
            from agents.reviewer_agent import ReviewerAgent
            self._reviewer = ReviewerAgent()
        return self._reviewer

    @property
    def reflection(self):
        if self._reflection is None:
            from agents.reflection_agent import ReflectionAgent
            self._reflection = ReflectionAgent()
        return self._reflection

    @property
    def tool_planner(self):
        if self._tool_planner is None:
            from agents.tool_planner_agent import ToolPlannerAgent
            self._tool_planner = ToolPlannerAgent()
        return self._tool_planner

    @property
    def tool_agent(self):
        if self._tool_agent is None:
            from agents.tool_agent import ToolAgent
            self._tool_agent = ToolAgent()
        return self._tool_agent


    def execute_goal(
        self,
        goal,
        job_id="workflow_001",
        stream=False,
        history=None,
        meta=None,
        status_callback=None
    ):
        start_time = time.time()

        goal_lower = goal.lower()

        tool_keywords = [

            "list files",
            "search folder",
            "read file",
            "open file",
            "run python",
            "execute code"
        ]

        is_tool_request = any(
            keyword in goal_lower
            for keyword in tool_keywords
        )

       

        if is_tool_request:
            if status_callback:
                status_callback("Checking developer tool permissions...")

            tool_plan = (
                self.tool_planner
                .decide_tool(
                    goal
                )
            )

        else:

            tool_plan = {
                "tool": "NONE"
            }

        tool = (
            tool_plan.get(
                "tool",
                "NONE"
            )
        )

       

        if tool == "NONE":

            tool = (
                self.tool_router
                .classify(
                    goal
                )
            )

        

        if tool and tool != "NONE":
            if status_callback:
                status_callback(f"Executing developer tool: {tool}...")

            print(
                f"\nDetected Tool: {tool}\n"
            )

            if tool == "SEARCH_FOLDER":

                folder = (
                    tool_plan.get(
                        "folder",
                        "data"
                    )
                )

                result = (
                    self.tool_agent
                    .search_folder(
                        folder
                    )
                )
                self.tool_memory.save(
                    "SEARCH_FOLDER",
                    result
                )

            elif tool == "READ_FILE":

                filepath = (
                    tool_plan.get(
                        "filepath"
                    )
                )

                if not filepath:

                    filepath = (
                        self.tool_parser
                        .extract_file_path(
                            goal
                        )
                    )

                if filepath:

                    result = (
                        self.tool_agent
                        .read_file(
                            filepath
                        )
                    )
                    self.tool_memory.save(
                        "READ_FILE",
                        result
                    )

                else:

                    result = (
                        "No file path found."
                    )

            elif tool == "EXECUTE_PYTHON":

                code = (
                    tool_plan.get(
                        "code"
                    )
                )

                if not code:

                    code = (
                        self.tool_parser
                        .extract_python_code(
                            goal
                        )
                    )

                if code:

                    result = (
                        self.tool_agent
                        .execute_python(
                            code
                        )
                    )
                    self.tool_memory.save(
                        "EXECUTE_PYTHON",
                        result
                    )

                else:

                    result = (
                        "No Python code found."
                    )

            elif tool == "WRITE_FILE":

                filepath, code = (
                    self.tool_parser
                    .extract_write_file_data(
                        goal
                    )
                )

                if filepath and code is not None:

                    result = (
                        self.tool_agent
                        .write_file(
                            filepath,
                            code
                        )
                    )
                    self.tool_memory.save(
                        "WRITE_FILE",
                        result
                    )

                else:

                    result = (
                        "No file path or content found."
                    )

            elif tool == "GREP_SEARCH":

                query, folder = (
                    self.tool_parser
                    .extract_grep_search_data(
                        goal
                    )
                )

                if query:

                    result = (
                        self.tool_agent
                        .grep_search(
                            query,
                            folder
                        )
                    )
                    self.tool_memory.save(
                        "GREP_SEARCH",
                        result
                    )

                else:

                    result = (
                        "No search query found."
                    )

            else:

                result = (
                    "Unknown tool."
                )

            duration = int(
                (time.time() - start_time)
                * 1000
            )

            self.journal.log_interaction(
                "TOOL", goal,
                duration_ms=duration
            )

            return {
                "intent": "TOOL",
                "output": str(result),
                "file": None
            }

       

        if status_callback:
            status_callback("Classifying user intent...")

        intent = (
            self.router
            .classify(
                goal
            )
        )

        print(
            f"\nDetected Intent: {intent}\n"
        )


        if intent == "RESPOND":
            if status_callback:
                status_callback("Generating response...")

            if stream:

                response = (
                    self.responder
                    .respond_stream(
                        goal,
                        history=history
                    )
                )

                return {
                    "intent": "RESPOND",
                    "output": self._stream_wrapper(response, "RESPOND", goal, start_time, meta=meta),
                    "file": None
                }

            else:

                response = (
                    self.responder
                    .respond(
                        goal,
                        history=history
                    )
                )

                filepath = (
                    self.output_manager
                    .save_markdown(
                        "response",
                        response
                    )
                )

                duration = int(
                    (time.time() - start_time)
                    * 1000
                )

                self.journal.log_interaction(
                    "RESPOND", goal,
                    duration_ms=duration
                )

                return {
                    "intent": "RESPOND",
                    "output": response,
                    "file": filepath
                }

       

        if intent == "CONTENT":
            if status_callback:
                status_callback("Synthesizing creative content...")

            if stream:

                content = (
                    self.content_agent
                    .create_content_stream(
                        goal,
                        history=history
                    )
                )

                return {
                    "intent": "CONTENT",
                    "output": self._stream_wrapper(content, "CONTENT", goal, start_time, meta=meta),
                    "file": None
                }

            else:

                content = (
                    self.content_agent
                    .create_content(
                        goal,
                        history=history
                    )
                )

                filepath = (
                    self.output_manager
                    .save_markdown(
                        "content",
                        content
                    )
                )

                duration = int(
                    (time.time() - start_time)
                    * 1000
                )

                self.journal.log_interaction(
                    "CONTENT", goal,
                    duration_ms=duration
                )

                return {
                    "intent": "CONTENT",
                    "output": content,
                    "file": filepath
                }

        

        if intent == "QUESTION":

            if stream:

                response, kb_hit = (
                    self.question_agent
                    .answer_stream(
                        goal,
                        history=history,
                        status_callback=status_callback
                    )
                )

                return {
                    "intent": "QUESTION",
                    "output": self._stream_wrapper(response, "QUESTION", goal, start_time, kb_hit, meta=meta),
                    "file": None,
                    "knowledge_hit": kb_hit
                }

            else:

                response, kb_hit = (
                    self.question_agent
                    .answer(
                        goal,
                        history=history,
                        status_callback=status_callback
                    )
                )

                filepath = (
                    self.output_manager
                    .save_markdown(
                        "answer",
                        response
                    )
                )

                duration = int(
                    (time.time() - start_time)
                    * 1000
                )

                self.journal.log_interaction(
                    "QUESTION", goal,
                    duration_ms=duration,
                    knowledge_hit=kb_hit
                )

                return {
                    "intent": "QUESTION",
                    "output": response,
                    "file": filepath,
                    "knowledge_hit": kb_hit
                }

        

        if status_callback:
            status_callback("Creating multi-step execution plan...")

        print("\n" + "=" * 60)
        print("CREATING EXECUTION PLAN")
        print("=" * 60)

        plan = (
            self.planner
            .create_plan(
                goal
            )
        )

        previous_output = None

        print("\nGenerated Plan:\n")

        for i, step in enumerate(
            plan,
            start=1
        ):

            print(
                f"{i}. "
                f"[{step['task_type']}] "
                f"{step['description']}"
            )

        print("\n" + "=" * 60)
        print("EXECUTING WORKFLOW")
        print("=" * 60)

        total_steps = len(plan)
        for step_number, task in enumerate(
            plan,
            start=1
        ):

            task_type = task[
                "task_type"
            ]

            description = task[
                "description"
            ]

            if status_callback:
                status_callback(f"Step {step_number}/{total_steps}: Running {task_type} agent...")

            print(
                f"\nSTEP {step_number}: "
                f"{task_type.upper()}"
            )

            if task_type == "deep_research":

                previous_output = (
                    self.researcher
                    .deep_research(
                        description
                    )
                )

            elif task_type == "research":

                previous_output = (
                    self.researcher
                    .research(
                        description
                    )
                )

            elif task_type == "write":

                previous_output = (
                    self.writer
                    .write(
                        description,
                        previous_output
                    )
                )

            elif task_type == "review":

                previous_output = (
                    self.reviewer
                    .review(
                        previous_output
                    )
                )

            self.checkpoints.save_checkpoint(
                job_id,
                step_number,
                description,
                {
                    "task_type": task_type,
                    "output": previous_output
                }
            )

            print(
                f"Step {step_number} completed"
            )

        

        if previous_output:
            if status_callback:
                status_callback("Evaluating output quality check...")

            print(
                "\n" + "=" * 60
            )
            print("REFLECTION CHECK")
            print("=" * 60)

            evaluation = (
                self.reflection
                .reflect(
                    goal,
                    previous_output
                )
            )

            print(
                f"\nScore: "
                f"{evaluation['score']}/10"
            )

            print(
                f"Feedback: "
                f"{evaluation['feedback']}"
            )

            if not evaluation["passed"]:
                if status_callback:
                    status_callback(f"Quality check score {evaluation['score']}/10. Revising output report...")

                print(
                    "\nRevising output...\n"
                )

                previous_output = (
                    self.writer.write(
                        f"{goal}\n\n"
                        f"Feedback: "
                        f"{evaluation['feedback']}",
                        previous_output
                    )
                )

                print(
                    "Revision completed"
                )

            else:
                if status_callback:
                    status_callback(f"Quality check passed with score {evaluation['score']}/10!")

                print(
                    "\nQuality check passed"
                )

        if status_callback:
            status_callback("Compiling final output report...")

        filepath = (
            self.output_manager
            .save_markdown(
                "workflow_result",
                previous_output
            )
        )

        duration = int(
            (time.time() - start_time)
            * 1000
        )

        self.journal.log_interaction(
            "WORKFLOW", goal,
            duration_ms=duration
        )

        return {
            "intent": "WORKFLOW",
            "output": None,
            "file": filepath
        }

    def get_last_tool_result(self):

        return (
            self.tool_memory
            .get_last_result()
        )

    def get_last_tool_name(self):

        return (
            self.tool_memory
            .get_last_tool()
        )

    def _stream_wrapper(self, generator, intent, goal, start_time, kb_hit=False, meta=None):
        """
        Wrapper generator to yield tokens, accumulate response,
        save to markdown output, and log execution details upon completion.
        """
        full_text = []
        for token in generator:
            yield token
            full_text.append(token)
            
        response_str = "".join(full_text)
        
        # Save output file
        filepath = self.output_manager.save_markdown(intent.lower(), response_str)
        if isinstance(meta, dict):
            meta["file"] = filepath
        
        # Log to journal
        duration = int((time.time() - start_time) * 1000)
        self.journal.log_interaction(
            intent,
            goal,
            duration_ms=duration,
            knowledge_hit=kb_hit
        )
