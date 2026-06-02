import json
import time

from pathlib import Path
from datetime import datetime
from collections import Counter


class LearningJournal:
    """
    Tracks all interactions, outcomes,
    and accumulated lessons.

    Append-only JSON log.
    Zero LLM cost.
    """

    def __init__(
        self,
        journal_path="data/learning_journal.json"
    ):

        self.journal_path = Path(
            journal_path
        )

        self.journal_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.entries = []

        self._load()

    def _load(self):

        if self.journal_path.exists():

            try:

                with open(
                    self.journal_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    self.entries = json.load(f)

            except Exception:

                self.entries = []

    def _save(self):

        with open(
            self.journal_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.entries,
                f,
                indent=2,
                ensure_ascii=False
            )

    def log_interaction(
        self,
        intent,
        goal,
        success=True,
        duration_ms=0,
        knowledge_hit=False
    ):
        """Log a completed interaction."""

        entry = {

            "type": "interaction",

            "intent": intent,

            "goal": goal[:200],

            "success": success,

            "duration_ms": duration_ms,

            "knowledge_hit": knowledge_hit,

            "timestamp": (
                datetime.now().isoformat()
            )
        }

        self.entries.append(entry)

        self._save()

    def log_lesson(
        self,
        category,
        lesson
    ):
        """Store a learned insight."""

        entry = {

            "type": "lesson",

            "category": category,

            "lesson": lesson,

            "timestamp": (
                datetime.now().isoformat()
            )
        }

        self.entries.append(entry)

        self._save()

    def get_stats(self):
        """Return interaction statistics."""

        interactions = [
            e for e in self.entries
            if e.get("type") == "interaction"
        ]

        if not interactions:

            return {
                "total": 0,
                "by_intent": {},
                "success_rate": 0,
                "avg_duration_ms": 0,
                "knowledge_hit_rate": 0
            }

        intent_counts = Counter(
            e["intent"]
            for e in interactions
        )

        successes = sum(
            1 for e in interactions
            if e.get("success")
        )

        kb_hits = sum(
            1 for e in interactions
            if e.get("knowledge_hit")
        )

        durations = [
            e.get("duration_ms", 0)
            for e in interactions
            if e.get("duration_ms", 0) > 0
        ]

        avg_duration = (
            sum(durations) / len(durations)
            if durations
            else 0
        )

        return {

            "total": len(interactions),

            "by_intent": dict(intent_counts),

            "success_rate": round(
                successes / len(interactions)
                * 100,
                1
            ),

            "avg_duration_ms": round(
                avg_duration
            ),

            "knowledge_hit_rate": round(
                kb_hits / len(interactions)
                * 100,
                1
            )
        }

    def get_frequent_topics(self, top_n=5):
        """Most queried topics."""

        interactions = [
            e for e in self.entries
            if e.get("type") == "interaction"
        ]

        topics = Counter(
            e.get("goal", "")[:50]
            for e in interactions
        )

        return topics.most_common(top_n)

    def get_lessons(self, category=None):
        """Retrieve stored lessons."""

        lessons = [
            e for e in self.entries
            if e.get("type") == "lesson"
        ]

        if category:

            lessons = [
                e for e in lessons
                if e.get("category") == category
            ]

        return lessons

    def display_stats(self):
        """Print formatted statistics."""

        stats = self.get_stats()

        print("\n--- AI OS Statistics ---\n")

        print(
            f"  Total Interactions: "
            f"{stats['total']}"
        )

        print(
            f"  Success Rate: "
            f"{stats['success_rate']}%"
        )

        print(
            f"  Avg Duration: "
            f"{stats['avg_duration_ms']}ms"
        )

        print(
            f"  Knowledge Hit Rate: "
            f"{stats['knowledge_hit_rate']}%"
        )

        if stats["by_intent"]:

            print("\n  By Intent:")

            for intent, count in (
                stats["by_intent"].items()
            ):

                print(
                    f"    {intent}: {count}"
                )

        topics = self.get_frequent_topics()

        if topics:

            print("\n  Top Topics:")

            for topic, count in topics:

                print(
                    f"    [{count}x] {topic}"
                )

        print("\n---\n")
