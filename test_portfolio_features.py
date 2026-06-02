import unittest
import numpy as np
import json
from pathlib import Path
from html.parser import HTMLParser
import re
import shutil

# Import features to test
from tools.web_scraper import scrape_url, TextExtractParser
from core.vector_store import VectorStore


class TestPortfolioFeatures(unittest.TestCase):

    def setUp(self):
        # Create temp directory for tests
        self.test_dir = Path("data/test_kb")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.test_dir / "test_embeddings.json"
        if self.db_path.exists():
            self.db_path.unlink()

    def tearDown(self):
        # Cleanup
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_html_scraper_parser(self):
        """Test HTML parsing removes ignored tags and keeps title/content."""
        raw_html = """
        <html>
        <head>
            <title>Mock Page Title</title>
            <style>
                body { background-color: black; }
            </style>
            <script>
                console.log("ignore me");
            </script>
        </head>
        <body>
            <header>
                <nav>Header Nav Link</nav>
            </header>
            <h1>Main Heading</h1>
            <div id="sidebar-wrapper" class="vector-menu-portal">
                Sidebar navigation links
            </div>
            <p>This is standard content that should be retrieved.</p>
            <noscript>JavaScript disabled</noscript>
            <aside class="languages">
                English, Español, Français
            </aside>
            <div>Some other text content.</div>
            <footer>Copyright 2026</footer>
        </body>
        </html>
        """
        parser = TextExtractParser()
        parser.feed(raw_html)
        
        self.assertEqual(parser.title.strip(), "Mock Page Title")
        text = parser.get_text()
        
        # Style/script/noscript/nav/footer/aside contents should be excluded
        self.assertNotIn("background-color", text)
        self.assertNotIn("console.log", text)
        self.assertNotIn("JavaScript disabled", text)
        self.assertNotIn("Header Nav Link", text)
        self.assertNotIn("Sidebar navigation links", text)
        self.assertNotIn("English, Español, Français", text)
        self.assertNotIn("Copyright 2026", text)
        
        # Valid texts should be present
        self.assertIn("Main Heading", text)
        self.assertIn("This is standard content", text)
        self.assertIn("Some other text content", text)

    def test_lsh_vector_store(self):
        """Test LSH hashing, bucketing, and retrieval in VectorStore."""
        vs = VectorStore(store_path=str(self.db_path))
        
        # Check projection matrix is lazy-loaded
        self.assertIsNone(vs.projection_matrix)
        
        # Generate mock embeddings (dimension 768)
        rng = np.random.default_rng(123)
        emb_query = rng.normal(size=768)
        
        # Documents
        emb_doc1 = emb_query + rng.normal(scale=0.01, size=768) # Highly similar
        emb_doc2 = emb_query + rng.normal(scale=0.1, size=768)  # Somewhat similar
        emb_doc3 = rng.normal(size=768)                         # Dissimilar
        
        vs.add("doc1", "Document one content", emb_doc1)
        vs.add("doc2", "Document two content", emb_doc2)
        vs.add("doc3", "Document three content", emb_doc3)
        
        # Verify indexing
        self.assertIsNotNone(vs.projection_matrix)
        self.assertEqual(vs.projection_matrix.shape, (16, 768))
        self.assertTrue(len(vs.buckets) > 0)
        
        # Check that search returns doc1 as highest score
        results = vs.search(emb_query, top_k=3)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0][0], "doc1")
        self.assertEqual(results[1][0], "doc2")
        self.assertEqual(results[2][0], "doc3")
        
        # Check scores decrease
        self.assertTrue(results[0][1] > results[1][1])
        self.assertTrue(results[1][1] > results[2][1])


if __name__ == "__main__":
    unittest.main()
