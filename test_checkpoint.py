from core.checkpoint import CheckpointManager

cp = CheckpointManager()

JOB = "workflow_001"

cp.save_checkpoint(
    JOB,
    1,
    "Research",
    {
        "result":
        "Research completed"
    }
)

cp.save_checkpoint(
    JOB,
    2,
    "Writing",
    {
        "result":
        "Article generated"
    }
)

print(
    "Last Step:",
    cp.get_last_step(JOB)
)

print(
    cp.load_checkpoints(JOB)
)