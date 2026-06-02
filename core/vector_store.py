import json
import numpy as np
import threading

from pathlib import Path


class VectorStore:
    """
    Pure numpy vector store.

    No external dependencies beyond numpy.
    Cosine similarity search over embeddings.
    Persists to JSON file.
    """

    def __init__(
        self,
        store_path="data/embeddings.json"
    ):

        self.store_path = Path(store_path)

        self.store_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.documents = {}
        self.lock = threading.Lock()
        
        self.num_bits = 16
        self.projection_matrix = None
        self.buckets = {}

        self._load()

    def _load(self):

        if self.store_path.exists():

            try:

                with open(
                    self.store_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    self.documents = json.load(f)

            except Exception:

                self.documents = {}
        self._build_index()

    def _save(self):

        with self.lock:
            with open(
                self.store_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.documents,
                    f,
                    ensure_ascii=False
                )

    def _get_projection_matrix(self, dim):
        if self.projection_matrix is None or self.projection_matrix.shape[1] != dim:
            # Deterministic projection matrix
            rng = np.random.default_rng(42)
            self.projection_matrix = rng.normal(size=(self.num_bits, dim))

    def _compute_hash(self, embedding):
        v = np.array(embedding, dtype=np.float32)
        self._get_projection_matrix(v.shape[0])
        projected = np.dot(self.projection_matrix, v)
        binary = (projected >= 0).astype(int)
        return "".join(str(b) for b in binary)

    def _build_index(self):
        self.buckets = {}
        if not self.documents:
            return
        # Get first document to inspect embedding dimension
        first_doc = next(iter(self.documents.values()))
        emb = first_doc.get("embedding")
        if emb is not None:
            dim = len(emb)
            self._get_projection_matrix(dim)
            for doc_id, doc in self.documents.items():
                h_str = self._compute_hash(doc["embedding"])
                if h_str not in self.buckets:
                    self.buckets[h_str] = []
                self.buckets[h_str].append(doc_id)

    def add(
        self,
        doc_id,
        preview,
        embedding
    ):
        """Store document with embedding."""

        if embedding is None:
            return

        emb_list = (
            embedding.tolist()
            if hasattr(embedding, "tolist")
            else embedding
        )

        self.documents[doc_id] = {
            "preview": preview[:200],
            "embedding": emb_list
        }

        # Update buckets
        h_str = self._compute_hash(emb_list)
        if h_str not in self.buckets:
            self.buckets[h_str] = []
        if doc_id not in self.buckets[h_str]:
            self.buckets[h_str].append(doc_id)

        self._save()

    def remove(self, doc_id):

        if doc_id in self.documents:

            del self.documents[doc_id]
            self._build_index()
            self._save()

    def search(
        self,
        query_embedding,
        top_k=3
    ):
        """
        Cosine similarity search with LSH candidate selection.

        Returns list of (doc_id, score, preview).
        """

        if (
            query_embedding is None
            or not self.documents
        ):
            return []

        q = (
            query_embedding
            if isinstance(
                query_embedding, np.ndarray
            )
            else np.array(
                query_embedding,
                dtype=np.float32
            )
        )

        q_norm = np.linalg.norm(q)

        if q_norm == 0:
            return []

        # Get query hash
        q_hash_str = self._compute_hash(q)
        q_hash_arr = np.array([int(c) for c in q_hash_str], dtype=np.int8)

        # Calculate Hamming distance to all active buckets
        bucket_candidates = []
        for h_str, doc_ids in self.buckets.items():
            h_arr = np.array([int(c) for c in h_str], dtype=np.int8)
            dist = np.sum(q_hash_arr != h_arr)
            bucket_candidates.append((dist, doc_ids))

        # Sort buckets by Hamming distance
        bucket_candidates.sort(key=lambda x: x[0])

        # Gather candidates up to threshold
        candidates = []
        min_candidates = max(top_k * 5, 20)
        for dist, doc_ids in bucket_candidates:
            candidates.extend(doc_ids)
            if len(candidates) >= min_candidates:
                break

        candidates = list(set(candidates))

        results = []

        for doc_id in candidates:
            doc = self.documents.get(doc_id)
            if not doc:
                continue

            emb = np.array(
                doc["embedding"],
                dtype=np.float32
            )

            emb_norm = np.linalg.norm(emb)

            if emb_norm == 0:
                continue

            score = float(
                np.dot(q, emb)
                / (q_norm * emb_norm)
            )

            results.append((
                doc_id,
                score,
                doc.get("preview", "")
            ))

        results.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return results[:top_k]

    def count(self):

        return len(self.documents)
