"""
AI OS Web Dashboard Runner

Usage:
    python dashboard.py
"""

from core.dashboard_server import run_server

if __name__ == "__main__":
    run_server(port=8000)
