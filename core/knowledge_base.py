import json
import re
import os

from pathlib import Path
from datetime import datetime




STRIP_PREFIXES = [
    "tell me everything about",
    "explain in detail",
    "research about",
    "tell me about",
    "learn about",
    "what is an",
    "what is a",
    "what are",
    "how does",
    "what is",
    "describe",
    "explain",
    "how do",
    "how to",
    "why is",
    "why do",
    "define",
    "research",
]



STOPWORDS = {
    "a", "an", "the", "is", "are",
    "was", "were", "in", "on", "at",
    "to", "for", "of", "with", "by",
    "from", "about", "into", "and",
    "or", "but", "not", "this", "that",
    "these", "those", "it", "its",
    "my", "your", "our", "their",
    "me", "we", "you", "they",
    "he", "she", "do", "does", "did",
    "has", "have", "had", "be", "been",
    "being", "will", "would", "could",
    "should", "can", "may", "might",
    "shall", "very", "really", "just",
    "also", "too", "please", "need",
    "want", "like", "know",
}


class KnowledgeBase:

    def __init__(
        self,
        knowledge_dir="data/knowledge"
    ):

        self.knowledge_dir = Path(
            knowledge_dir
        )

        self.knowledge_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self._vector_store = None
        self._migrated = False

        self._migrate_legacy_files()
        self._auto_index_unmapped_files()

        from core.knowledge_graph import KnowledgeGraph
        self.graph = KnowledgeGraph()

  

    @property
    def vector_store(self):

        if self._vector_store is None:

            from core.vector_store import (
                VectorStore
            )

            self._vector_store = VectorStore()

        return self._vector_store

   

    def _normalize_topic(self, topic):
        """
        Normalize topic to canonical key.

        Strips known prefixes,
        removes stopwords,
        cleans special characters.
        """

        topic = topic.lower().strip()

        topic = topic.rstrip("?.!,;:")

        for prefix in STRIP_PREFIXES:

            if topic.startswith(prefix):

                topic = (
                    topic[len(prefix):]
                    .strip()
                )

                break

        topic = re.sub(
            r"[^a-z0-9\s]",
            "",
            topic
        )

        words = topic.split()

        words = [
            w for w in words
            if w not in STOPWORDS
        ]

        if not words:
            return "general"

        return "_".join(words)

    def _sanitize_topic(self, topic):
        """
        Backward-compatible wrapper.
        Now uses normalization.
        """

        return self._normalize_topic(topic)



    def _migrate_legacy_files(self):
        """
        Rename old knowledge files
        to normalized filenames.
        Merge duplicates.
        """

        if self._migrated:
            return

        self._migrated = True

        files = list(
            self.knowledge_dir.glob("*.json")
        )

        if not files:
            return

        migration_needed = False
        file_map = {}

        for file in files:

            try:

                with open(
                    file, "r",
                    encoding="utf-8"
                ) as f:

                    data = json.load(f)

                topic = data.get(
                    "topic",
                    file.stem
                )

                normalized = (
                    self._normalize_topic(topic)
                )

                expected_name = (
                    f"{normalized}.json"
                )

                if file.name != expected_name:

                    migration_needed = True

                if normalized not in file_map:

                    file_map[normalized] = {
                        "data": data,
                        "files": [file]
                    }

                else:

                    existing = (
                        file_map[normalized]
                    )

                    if len(
                        data.get("content", "")
                    ) > len(
                        existing["data"]
                        .get("content", "")
                    ):
                        existing["data"] = data

                    existing["files"].append(file)

                    migration_needed = True

            except Exception:
                continue

        if not migration_needed:
            return

        for normalized, info in file_map.items():

            target = (
                self.knowledge_dir /
                f"{normalized}.json"
            )

            with open(
                target, "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    info["data"],
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            for old_file in info["files"]:

                if old_file != target:

                    try:
                        old_file.unlink()
                    except Exception:
                        pass

    def _auto_index_unmapped_files(self):
        """
        Scan all knowledge files and ensure they are indexed in the vector store.
        If a file lacks a vector store entry, generate the embedding and index it.
        """
        files = list(self.knowledge_dir.glob("*.json"))
        if not files:
            return

        # Trigger lazy load of vector store
        vs = self.vector_store

        unindexed_files = []
        for file in files:
            normalized = file.stem
            if normalized not in vs.documents:
                unindexed_files.append((normalized, file))

        if not unindexed_files:
            return

        print(f"\nAuto-indexing {len(unindexed_files)} unmapped knowledge files...")
        
        from core.embeddings import get_embedding

        for normalized, file in unindexed_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                topic = data.get("topic", normalized)
                content = data.get("content", "")
                
                if content:
                    embed_text = f"{topic}. {content[:500]}"
                    embedding = get_embedding(embed_text)
                    if embedding is not None:
                        vs.add(
                            normalized,
                            content[:200],
                            embedding
                        )
                        print(f"  Indexed: {topic}")
            except Exception as e:
                print(f"  Failed to index {file.name}: {e}")


    def save_knowledge(
        self,
        topic,
        content
    ):

        normalized = self._normalize_topic(
            topic
        )

        filepath = (
            self.knowledge_dir /
            f"{normalized}.json"
        )

        knowledge = {

            "topic": topic,

            "normalized_key": normalized,

            "content": content,

            "created_at": (
                datetime.now()
                .isoformat()
            )
        }

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                knowledge,
                f,
                indent=4,
                ensure_ascii=False
            )

      

        try:

            from core.embeddings import (
                get_embedding
            )

            embed_text = (
                f"{topic}. {content[:500]}"
            )

            embedding = get_embedding(
                embed_text
            )

            if embedding is not None:

                self.vector_store.add(
                    normalized,
                    content[:200],
                    embedding
                )

        except Exception:
            pass

        # Update Knowledge Graph topic connections
        try:
            all_topics = self.list_topics()
            if topic not in all_topics:
                all_topics.append(topic)
            self.graph.auto_map_relations(topic, content, all_topics)
        except Exception:
            pass

        return str(filepath)

   

    def get_knowledge(self, topic):

        normalized = self._normalize_topic(
            topic
        )

        filepath = (
            self.knowledge_dir /
            f"{normalized}.json"
        )

        if not filepath.exists():
            return None

        try:

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception:

            return None


    def search_knowledge(self, query):

        normalized_query = (
            self._normalize_topic(query)
        )

        query_words = set(
            normalized_query.split("_")
        )

        matches = []

        for file in self.knowledge_dir.glob(
            "*.json"
        ):

            try:

                with open(
                    file,
                    "r",
                    encoding="utf-8"
                ) as f:

                    knowledge = json.load(f)

                file_key = file.stem
                file_words = set(
                    file_key.split("_")
                )

                overlap = (
                    query_words & file_words
                )

                if overlap:

                    score = (
                        len(overlap)
                        / max(
                            len(query_words),
                            len(file_words)
                        )
                    )

                    matches.append({
                        **knowledge,
                        "_score": score
                    })

            except Exception:
                continue

        matches.sort(
            key=lambda x: x.get(
                "_score", 0
            ),
            reverse=True
        )

        return matches

  

    def semantic_search(
        self,
        query,
        top_k=3
    ):
        """
        Search knowledge using
        embedding similarity.
        """

        try:

            from core.embeddings import (
                get_embedding
            )

            query_embedding = get_embedding(
                query
            )

            if query_embedding is None:
                return []

            results = self.vector_store.search(
                query_embedding,
                top_k=top_k
            )

            matches = []

            for doc_id, score, preview in results:

                if score < 0.3:
                    continue

                knowledge = self.get_knowledge(
                    doc_id
                )

                if knowledge:

                    knowledge["_semantic_score"] = (
                        score
                    )

                    matches.append(knowledge)

                else:

                    filepath = (
                        self.knowledge_dir /
                        f"{doc_id}.json"
                    )

                    if filepath.exists():

                        try:

                            with open(
                                filepath,
                                "r",
                                encoding="utf-8"
                            ) as f:

                                k = json.load(f)

                            k["_semantic_score"] = (
                                score
                            )

                            matches.append(k)

                        except Exception:
                            pass

            return matches

        except Exception:

            return []

    

    def smart_search(self, query):
        """
        Best-effort knowledge retrieval.

        1. Exact match (fastest)
        2. Keyword match
        3. Semantic search (if available)

        Returns best single result or None.
        """

        # 1. Exact match

        exact = self.get_knowledge(query)

        if exact:
            return exact

        # 2. Keyword search

        keyword_matches = (
            self.search_knowledge(query)
        )

        # 3. Semantic search

        semantic_matches = (
            self.semantic_search(query)
        )

        # Merge and deduplicate

        all_matches = {}

        for m in keyword_matches:

            key = m.get(
                "normalized_key",
                m.get("topic", "")
            )

            if key not in all_matches:

                all_matches[key] = m

        for m in semantic_matches:

            key = m.get(
                "normalized_key",
                m.get("topic", "")
            )

            if key not in all_matches:

                all_matches[key] = m

        if all_matches:

            best = list(
                all_matches.values()
            )[0]

            query_normalized = self._normalize_topic(query)
            best_normalized = self._normalize_topic(best.get("topic", ""))
            query_words = set(query_normalized.split("_"))
            candidate_words = set(best_normalized.split("_"))
            overlap = query_words & candidate_words
            min_len = min(len(query_words), len(candidate_words))
            overlap_ratio = len(overlap) / min_len if min_len > 0 else 0.0

            if overlap_ratio >= 0.70:
                return best
            else:
                print(f"[Smart Search Rejected: '{best.get('topic')}' vs '{query}'] — Overlap ratio {overlap_ratio:.2f} < 0.70")

        return None

    

    def list_topics(self):

        topics = []

        for file in self.knowledge_dir.glob(
            "*.json"
        ):

            try:

                with open(
                    file,
                    "r",
                    encoding="utf-8"
                ) as f:

                    knowledge = json.load(f)

                topics.append(
                    knowledge.get(
                        "topic",
                        file.stem
                    )
                )

            except Exception:

                topics.append(
                    file.stem
                )

        return sorted(topics)

   

    def delete_knowledge(self, topic):

        normalized = self._normalize_topic(
            topic
        )

        filepath = (
            self.knowledge_dir /
            f"{normalized}.json"
        )

        if filepath.exists():

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                display_topic = data.get("topic", topic)
                self.graph.remove_node(display_topic)
            except Exception:
                self.graph.remove_node(topic)

            filepath.unlink()

            self.vector_store.remove(
                normalized
            )

            return True

        return False
