import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import traceback

from workflows.engine import WorkflowEngine
from core.session_memory import SessionMemory
from core.learning_journal import LearningJournal
from core.knowledge_base import KnowledgeBase
from core.task_queue import TaskQueue


class DashboardRequestHandler(BaseHTTPRequestHandler):

    # We reuse instances to avoid loading database and configurations on every request
    engine = None
    session = None
    journal = None
    kb = None
    queue = None

    @classmethod
    def init_instances(cls):
        if cls.engine is None:
            cls.engine = WorkflowEngine()
            cls.session = SessionMemory()
            cls.journal = LearningJournal()
            cls.kb = KnowledgeBase()
            cls.queue = TaskQueue()

    def _set_headers(self, content_type="application/json", status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(status=204)

    def do_GET(self):
        self.init_instances()
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # Serve SPA index
        if path in ["", "/", "/index.html"]:
            self._serve_static("static/index.html", "text/html")
            return

       
        if path == "/api/status":
            try:
                import requests
                from config import OLLAMA_URL, DEFAULT_MODEL, EMBEDDING_MODEL
                ollama_running = False
                models = []
                try:
                    resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=1)
                    if resp.status_code == 200:
                        ollama_running = True
                        models = [m["name"] for m in resp.json().get("models", [])]
                except Exception:
                    pass

                stats = self.journal.get_stats()
                
                status_data = {
                    "ollama_running": ollama_running,
                    "default_model": DEFAULT_MODEL,
                    "embedding_model": EMBEDDING_MODEL,
                    "available_models": models,
                    "kb_topics_count": len(self.kb.list_topics()),
                    "vector_store_count": self.kb.vector_store.count(),
                    "active_session_count": self.session.count(),
                    "summary_context": self.session.summary_context,
                    "queue": {
                        "pending": self.queue.pending_count(),
                        "running": self.queue.running_count(),
                        "completed": self.queue.completed_count(),
                        "failed": self.queue.failed_count()
                    },
                    "stats": stats
                }
                self._send_json(status_data)
            except Exception as e:
                self._send_error(500, f"Error compiling system status: {e}")
            return

        elif path == "/api/knowledge":
            try:
                topics = self.kb.list_topics()
                items = []
                for topic in topics:
                    k = self.kb.get_knowledge(topic)
                    if k:
                        items.append(k)
                self._send_json(items)
            except Exception as e:
                self._send_error(500, f"Error loading knowledge: {e}")
            return

        elif path == "/api/graph":
            try:
                graph_data = self.kb.graph.get_graph_data()
                self._send_json(graph_data)
            except Exception as e:
                self._send_error(500, f"Error building knowledge graph: {e}")
            return

        elif path == "/api/history":
            try:
                history_data = self.session.exchanges
                self._send_json({
                    "summary_context": self.session.summary_context,
                    "exchanges": history_data
                })
            except Exception as e:
                self._send_error(500, f"Error fetching history: {e}")
            return

        elif path == "/api/queue":
            try:
                tasks = self.queue.get_all_tasks()
                self._send_json(tasks)
            except Exception as e:
                self._send_error(500, f"Error loading queue tasks: {e}")
            return

        elif path == "/api/sessions":
            try:
                files = list(self.session.session_dir.glob("*.json"))
                files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                sessions = []
                for file in files:
                    try:
                        with open(file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        
                        exchanges = data.get("exchanges", [])
                        summary = data.get("summary_context", "")
                        
                        title = "New Conversation"
                        if exchanges:
                            first_user = exchanges[0].get("user", "")
                            if first_user:
                                title = first_user if len(first_user) <= 40 else first_user[:37] + "..."
                        elif summary:
                            title = summary if len(summary) <= 40 else summary[:37] + "..."
                            
                        sessions.append({
                            "filename": file.name,
                            "title": title,
                            "timestamp": file.stat().st_mtime,
                            "exchanges_count": len(exchanges),
                            "summary": summary[:120] + "..." if len(summary) > 120 else summary
                        })
                    except Exception:
                        continue
                self._send_json(sessions)
            except Exception as e:
                self._send_error(500, f"Error listing sessions: {e}")
            return

        # Fallback to serving files if any exist
        static_file = Path(path.lstrip("/"))
        if static_file.exists() and static_file.is_file():
            content_type = "text/plain"
            if static_file.suffix == ".html":
                content_type = "text/html"
            elif static_file.suffix == ".css":
                content_type = "text/css"
            elif static_file.suffix == ".js":
                content_type = "application/javascript"
            elif static_file.suffix == ".json":
                content_type = "application/json"
            self._serve_static(str(static_file), content_type)
            return

        self._send_error(404, "Endpoint not found.")

    def do_POST(self):
        self.init_instances()
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/chat":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                
                goal = data.get("prompt", "").strip()
                if not goal:
                    self._send_error(400, "Prompt is required.")
                    return

                # Submit to task queue if user wants background processing,
                # otherwise process synchronously (fast path / direct chat).
                run_in_background = data.get("background", False)
                priority = data.get("priority", 5)

                if run_in_background:
                    task_id = self.queue.add_task("goal", {"goal": goal}, priority=priority)
                    self._send_json({
                        "status": "queued",
                        "task_id": task_id,
                        "message": "Goal added to background task queue."
                    })
                    return

                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "close")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

                def send_status(status_text):
                    status_chunk = {"status": status_text}
                    try:
                        self.wfile.write(f"data: {json.dumps(status_chunk)}\n\n".encode("utf-8"))
                        self.wfile.flush()
                    except Exception:
                        pass

                # Check for scraper / ingest command
                import re
                
                def is_url(text):
                    text = text.strip()
                    if text.startswith(("http://", "https://", "www.")):
                        return True
                    pattern = r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}(/.*)?$"
                    return bool(re.match(pattern, text))

                g_lower = goal.lower()
                url = None
                if g_lower.startswith("ingest "):
                    url = goal[len("ingest "):].strip()
                elif g_lower.startswith("scrape "):
                    url = goal[len("scrape "):].strip()
                elif is_url(goal):
                    url = goal.strip()

                if url:
                    send_status(f"Parsing URL target: {url}...")
                    from tools.web_scraper import scrape_url
                    send_status("Scraping webpage offline...")
                    res = scrape_url(url)
                    
                    if not res["success"]:
                        error_msg = f"Failed to scrape webpage: {res.get('error', 'Unknown error')}"
                        send_status(error_msg)
                        
                        chunk = {
                            "token": error_msg,
                            "intent": "RESPOND"
                        }
                        self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode("utf-8"))
                        self.wfile.flush()
                        
                        final_chunk = {
                            "done": True,
                            "intent": "RESPOND"
                        }
                        self.wfile.write(f"data: {json.dumps(final_chunk)}\n\n".encode("utf-8"))
                        self.wfile.flush()
                        return
                    
                    title = res["title"]
                    content = res["content"]
                    
                    # Dynamically update Knowledge Graph with prompt
                    try:
                        last_query = None
                        if self.session.exchanges:
                            last_query = self.session.exchanges[-1].get("user")
                        
                        self.kb.graph.add_node(title)
                        if last_query:
                            self.kb.graph.add_node(last_query)
                            self.kb.graph.add_edge(last_query, title)
                    except Exception:
                        pass
                    
                    send_status("Indexing text content to LSH vector store...")
                    filepath = self.kb.save_knowledge(title, content)
                    
                    send_status("Auto-mapping relation graph connections...")
                    summary_text = f"Successfully ingested web page: '{title}' from {url}. Stored to {filepath}."
                    self.session.add_exchange(goal, summary_text)
                    self.session.save_session()
                    
                    send_status("Ingestion complete!")
                    
                    chunk = {
                        "token": f"Successfully ingested and mapped knowledge from web page:\n\n**Title**: {title}\n**URL**: {url}\n\nClean text content has been added to the LSH vector store and auto-linked in the knowledge graph.",
                        "intent": "RESPOND"
                    }
                    self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    
                    final_chunk = {
                        "done": True,
                        "intent": "RESPOND",
                        "knowledge_hit": True,
                        "ingested_topic": title
                    }
                    self.wfile.write(f"data: {json.dumps(final_chunk)}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    return

                # Check if it's a dashboard clear command
                if goal.lower() == "clear":
                    self.session.exchanges = []
                    self.session.summary_context = ""
                    
                    chunk = {
                        "token": "Conversation and summary context cleared.",
                        "intent": "RESPOND"
                    }
                    self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    
                    final_chunk = {
                        "done": True,
                        "intent": "RESPOND"
                    }
                    self.wfile.write(f"data: {json.dumps(final_chunk)}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    return

                # Dynamically update Knowledge Graph with prompt
                try:
                    last_query = None
                    if self.session.exchanges:
                        last_query = self.session.exchanges[-1].get("user")
                    
                    self.kb.graph.add_node(goal)
                    if last_query:
                        self.kb.graph.add_node(last_query)
                        self.kb.graph.add_edge(last_query, goal)
                except Exception:
                    pass
                
                meta = {}
                result = self.engine.execute_goal(
                    goal,
                    history=self.session.get_history(),
                    stream=True,
                    meta=meta,
                    status_callback=send_status
                )
                
                output = result.get("output")
                intent = result.get("intent", "RESPOND")
                kb_hit = result.get("knowledge_hit", False)

                if hasattr(output, "__iter__") and not isinstance(output, (str, bytes)):
                    full_response = []
                    for token in output:
                        full_response.append(token)
                        chunk = {
                            "token": token,
                            "intent": intent,
                            "knowledge_hit": kb_hit
                        }
                        self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode("utf-8"))
                        self.wfile.flush()

                    response_str = "".join(full_response)
                    self.session.add_exchange(goal, response_str)
                    self.session.save_session()

                    file_path = meta.get("file")
                    final_chunk = {
                        "done": True,
                        "intent": intent,
                        "file": file_path,
                        "knowledge_hit": kb_hit
                    }
                    self.wfile.write(f"data: {json.dumps(final_chunk)}\n\n".encode("utf-8"))
                    self.wfile.flush()
                else:
                    response_str = output
                    if intent == "WORKFLOW":
                        file_path = result.get("file")
                        if file_path and os.path.exists(file_path):
                            try:
                                with open(file_path, "r", encoding="utf-8") as f:
                                    response_str = f.read()
                            except Exception:
                                response_str = f"[Workflow completed. Output saved to {file_path}]"
                        else:
                            response_str = "[Workflow completed]"

                    self.session.add_exchange(goal, response_str or "")
                    self.session.save_session()

                    chunk = {
                        "token": response_str or "",
                        "intent": intent,
                        "knowledge_hit": kb_hit
                    }
                    self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode("utf-8"))
                    self.wfile.flush()

                    final_chunk = {
                        "done": True,
                        "intent": intent,
                        "file": result.get("file"),
                        "knowledge_hit": kb_hit
                    }
                    self.wfile.write(f"data: {json.dumps(final_chunk)}\n\n".encode("utf-8"))
                    self.wfile.flush()

            except Exception as e:
                traceback.print_exc()
                self._send_error(500, f"Error processing chat: {e}")
            return

        elif path == "/api/knowledge/clear":
            try:
                # Delete JSON files
                files = list(self.kb.knowledge_dir.glob("*.json"))
                for f in files:
                    try:
                        f.unlink()
                    except Exception:
                        pass
                
                # Clear vector store
                with self.kb.vector_store.lock:
                    self.kb.vector_store.documents = {}
                    self.kb.vector_store._save()
                
                # Clear graph
                with self.kb.graph.lock:
                    self.kb.graph.nodes = set()
                    self.kb.graph.edges = set()
                    self.kb.graph._save()
                
                self._send_json({"status": "success", "message": "All knowledge cleared."})
            except Exception as e:
                self._send_error(500, f"Error clearing knowledge: {e}")
            return

        elif path == "/api/knowledge/delete":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                topic = data.get("topic", "").strip()
                if not topic:
                    self._send_error(400, "Topic is required.")
                    return
                
                deleted = self.kb.delete_knowledge(topic)
                self._send_json({"status": "success", "deleted": deleted})
            except Exception as e:
                self._send_error(500, f"Error deleting topic: {e}")
            return

        elif path == "/api/sessions/new":
            try:
                self.session.save_session()
                self.session.clear_session()
                self._send_json({"status": "success", "message": "New session created."})
            except Exception as e:
                self._send_error(500, f"Error initializing new session: {e}")
            return

        elif path == "/api/sessions/load":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                filename = data.get("filename", "").strip()
                if not filename:
                    self._send_error(400, "Filename is required.")
                    return
                
                self.session.save_session()
                loaded = self.session.load_session_by_name(filename)
                if loaded:
                    self._send_json({
                        "status": "success",
                        "exchanges": self.session.exchanges,
                        "summary_context": self.session.summary_context
                    })
                else:
                    self._send_error(404, f"Session file '{filename}' not found.")
            except Exception as e:
                self._send_error(500, f"Error loading session: {e}")
            return

        elif path == "/api/sessions/delete":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(post_data)
                filename = data.get("filename", "").strip()
                if not filename:
                    self._send_error(400, "Filename is required.")
                    return
                
                filepath = self.session.session_dir / filename
                deleted = False
                if filepath.exists() and filepath.is_file():
                    filepath.unlink()
                    deleted = True
                self._send_json({"status": "success", "deleted": deleted})
            except Exception as e:
                self._send_error(500, f"Error deleting session: {e}")
            return

        self._send_error(404, "Endpoint not found.")

    def _serve_static(self, filepath, content_type):
        path = Path(filepath)
        if not path.exists() or not path.is_file():
            self._send_error(404, "Static file not found.")
            return

        try:
            with open(path, "rb") as f:
                content = f.read()
            self._set_headers(content_type, 200)
            self.wfile.write(content)
        except Exception as e:
            self._send_error(500, f"Error reading static file: {e}")

    def _send_json(self, data, status=200):
        self._set_headers("application/json", status)
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _send_error(self, code, message):
        self._send_json({"error": message}, status=code)


def run_server(port=8000):
    DashboardRequestHandler.init_instances()
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardRequestHandler)
    print(f"\n==========================================")
    print(f"  OFFLINE AI OS WEB SERVER RUNNING")
    print(f"  Access the Dashboard at: http://localhost:{port}")
    print(f"==========================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping web server...")
        httpd.server_close()
        print("Server stopped.")
