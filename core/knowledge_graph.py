import json
import re
import threading
from pathlib import Path


class KnowledgeGraph:
    """
    Manages node connections and topic associations.
    Saves to data/knowledge_graph.json.
    """

    def __init__(self, filepath="data/knowledge_graph.json"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.nodes = set()
        self.edges = set()  # set of frozensets (bidirectional relationships)
        self.lock = threading.Lock()
        self._load()

    def _load(self):
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.nodes = set(data.get("nodes", []))
                # Edges saved as lists of pairs, convert to frozensets
                self.edges = {frozenset(edge) for edge in data.get("edges", [])}
            except Exception:
                self.nodes = set()
                self.edges = set()

    def _save(self):
        with self.lock:
            edges_list = [list(edge) for edge in self.edges]
            data = {
                "nodes": sorted(list(self.nodes)),
                "edges": edges_list
            }
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def add_node(self, topic):
        if topic and topic not in self.nodes:
            self.nodes.add(topic)
            self._save()

    def remove_node(self, topic):
        if topic in self.nodes:
            self.nodes.remove(topic)
            # Remove any edges linked to this node
            self.edges = {edge for edge in self.edges if topic not in edge}
            self._save()

    def add_edge(self, topic_a, topic_b):
        if topic_a == topic_b:
            return
        if topic_a in self.nodes and topic_b in self.nodes:
            edge = frozenset([topic_a, topic_b])
            if edge not in self.edges:
                self.edges.add(edge)
                self._save()

    def auto_map_relations(self, topic, content, all_existing_topics):
        """
        Scan content for keywords matching other topics.
        Create edges if matches are found.
        """
        # Ensure nodes exist
        self.add_node(topic)
        for other in all_existing_topics:
            if other == topic:
                continue
            
            # Match word boundary case-insensitively
            # e.g., if other is "Docker", search for "\bdocker\b"
            pattern = r"\b" + re.escape(other.lower()) + r"\b"
            if re.search(pattern, content.lower()):
                self.add_node(other)
                self.add_edge(topic, other)

    def get_graph_data(self):
        """
        Returns JSON-compatible nodes and links representation.
        Format: {"nodes": [{"id": "topic1"}, ...], "links": [{"source": "topic1", "target": "topic2"}]}
        """
        nodes_list = [{"id": node} for node in sorted(list(self.nodes))]
        links_list = []
        for edge in self.edges:
            pair = list(edge)
            if len(pair) == 2:
                links_list.append({
                    "source": pair[0],
                    "target": pair[1]
                })
        return {
            "nodes": nodes_list,
            "links": links_list
        }
