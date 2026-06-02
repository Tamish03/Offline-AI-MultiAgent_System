from workflows.engine import WorkflowEngine

engine = WorkflowEngine()

result = engine.execute_goal(
    """
    Research Vector Databases.
    Write a professional report.
    Review and improve the report.
    """
)

print("\n")
print("=" * 60)
print("WORKFLOW COMPLETE")
print("=" * 60)

print(
    "\nSaved File:",
    result["file"]
)