from agents.planner_agent import PlannerAgent

planner = PlannerAgent()

plan = planner.create_plan(
    """
    Research AI agents.
    Write a report.
    Review the report.
    """
)

print(plan)