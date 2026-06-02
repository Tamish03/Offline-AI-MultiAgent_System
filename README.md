# Offline AI OS: Local Multi-Agent Workspace & Interactive Dashboard

A fully offline, local-first artificial intelligence workspace. It runs completely on local compute to ensure 100% privacy, utilizing Ollama for LLM and embeddings generation, a custom LSH-based vector database, and SQLite task queues. 

The project features a developer command-line live console interface and a glassmorphism dashboard that visualizes relation graphs, background tasks, and agent execution paths in real time.

---

## 🌟 Key Features

*   **100% Local & Private**: No cloud API calls, zero data leakage. Powered entirely by Ollama models (e.g. Llama 3, Mistral) and local embeddings.
*   **Recruiter-Grade Glassmorphic UI**: Sleek, tech-focused interface featuring frosted glass styling, custom hover transitions, linear gradients, and radial background grid overlays.
*   **Interactive SVG Knowledge Graph**: Renders ingested web pages, queries, and topics as dynamic hexagonal nodes with pulsing flow connections. Supports drag-to-pan, mousewheel zoom-to-scale, and quick-access HUD controls.
*   **Anti-Hallucination Caching Filters**: Enforces a minimum $70\%$ word/phrase overlap ratio matching constraint within semantic retrieval memory, blocking irrelevant background slides or out-of-context documents from polluting chat scopes.
*   **Multi-Session Chat Manager**: Supports creating new conversations via a dedicated workspace button, switching between active workspaces in a left sidebar history panel, and loading/deleting session logs directly from disk.
*   **Asynchronous Priority Task Queue**: SQLite-backed scheduler running background processes with collapsible visual details, start/stop timestamp logs, execution statuses, and running task animations.
*   **Performance Tracking Metrics**: Features SVG radial progress bars showing total run cycles and success ratios alongside real-time dynamic sparkline trend paths for latency and cache hits.
*   **Terminal Autocomplete Engine**: Console-style terminal with custom prompts, blinking cursors, and prefix commands autocompletion (supporting `ingest `, `scrape `, and `clear`) navigable using Arrow keys, Tab, or Enter.

---

## 🏗️ Core Architecture & Directory Layout

```
├── agents/                  # Multi-Agent system definitions (Planner, Reviewer, etc.)
├── core/                    # Core OS backend systems
│   ├── checkpoint.py        # System state and checkpoint databases
│   ├── dashboard_server.py  # HTTP server serving dashboard APIs and client files
│   ├── embeddings.py        # Embedding utilities linking Ollama
│   ├── knowledge_base.py    # Local vector matching, parsing, and caching rules
│   ├── knowledge_graph.py   # Relation graphs connecting nodes & edges
│   ├── session_memory.py    # JSON-based chat session serializer
│   ├── task_queue.py        # SQLite task manager scheduler
│   └── vector_store.py      # Cosine similarity & LSH indexing logic
├── data/                    # App data directories (session logs, LSH maps, DBs)
├── static/                  # Single Page Application frontend (HTML/CSS/JS)
├── tools/                   # Extensible agent tools (web scraper, python sandbox)
├── workflows/               # Orchestration engine loops and scheduler tasks
├── launch_dashboard.bat     # One-click Windows command launcher
├── PROJECT_DNA.md           # Technical specs and architecture breakdowns
└── DEVELOPER_GUIDE.md       # Roadmap on how to build this from scratch
```

---

## 🚀 Quick Start

### Prerequisites
Make sure you have [Ollama](https://ollama.com/) installed and running locally:
```bash
# Pull an instruction model
ollama pull mistral

# Pull an embeddings model
ollama pull nomic-embed-text
```

### Windows (One-Click Launch)
Simply double-click the `launch_dashboard.bat` script in the root directory. 

The launcher will automatically:
1. Detect or initialize your local Python virtual environment (`venv`).
2. Run sanity checks to ensure Python is in your PATH and Ollama is active.
3. Start the dashboard web server in a separate debug window.
4. Launch your default web browser to the OS workstation URL at `http://localhost:8000`.

### Manual Launch
If you prefer to start manually via CLI:
```bash
# 1. Activate venv
venv\Scripts\activate

# 2. Run the server
python dashboard.py

# 3. Access in browser
# Open http://localhost:8000
```

---

## 🤖 Cognitive Agent Workflow

When you submit a goal:
1. **Planner Agent**: Evaluates the objective and breaks it down into structured sub-tasks, ensuring each task contains full context to prevent downstream drift.
2. **Task Queue**: Places sub-tasks in a SQLite queue based on priority.
3. **Execution & Tools**: Sub-agents call tools to compile data (e.g. Scraper parses target websites, Sandbox runs test code scripts).
4. **Reviewer Agent**: Evaluates logs, checks compliance, and verifies accuracy. If changes are needed, it triggers a revision execution cycle.
5. **Output Delivery**: Results are added to your sessions history, vector database, and visually linked in the relation graph.
