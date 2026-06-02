from core.output_manager import OutputManager

manager = OutputManager()

file = manager.save_markdown(
    "vector_database_report",
    "# Report\n\nThis is a test."
)

print(file)