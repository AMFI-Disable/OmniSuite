"""Lightweight Web Viewer application server for OmniSuite.

Provides HTTP REST endpoints, a streaming backend (Server-Sent Events),
database card vault synchronization endpoints, and an interactive HTML/JS viewer.
"""

from __future__ import annotations

import json
import os
import queue
import threading
import time
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from omnishared.database import (
    add_card,
    add_motion,
    delete_card,
    get_db_path,
    get_velocity_stats,
    list_motions,
    read_all_cards,
    read_vault,
    search_cards_fts,
    setup_db,
    update_card,
)
from omnishared.database.extended import (
    get_card_tags,
    get_cards_by_tag,
    list_all_tags,
    set_card_rating,
)
from omnishared.database.sync import (
    SyncStrategy,
    apply_vault_changeset,
    compute_vault_checksum,
    export_vault_changeset,
)

# SSE Event Subscribers
_EVENT_SUBSCRIBERS: list[queue.Queue] = []
_SUBSCRIBERS_LOCK = threading.Lock()


def notify_subscribers(event_type: str, data: dict[str, Any]) -> None:
    """Broadcast an event to all connected SSE clients."""
    payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    with _SUBSCRIBERS_LOCK:
        dead_subscribers = []
        for q in _EVENT_SUBSCRIBERS:
            try:
                q.put_nowait(payload)
            except queue.Full:
                dead_subscribers.append(q)
        for dead in dead_subscribers:
            _EVENT_SUBSCRIBERS.remove(dead)


HTML_VIEWER = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniSuite Web Viewer</title>
    <style>
        :root {
            --bg-dark: #0f172a;
            --panel-bg: #1e293b;
            --accent-cyan: #06b6d4;
            --accent-blue: #3b82f6;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
            --aff-color: #10b981;
            --neg-color: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); line-height: 1.5; padding: 20px; }
        header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid var(--border-color); margin-bottom: 20px; }
        .logo { font-size: 1.5rem; font-weight: bold; color: var(--accent-cyan); display: flex; align-items: center; gap: 10px; }
        .badge { background: rgba(6, 182, 212, 0.1); border: 1px solid var(--accent-cyan); color: var(--accent-cyan); padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; }
        .grid-container { display: grid; grid-template-columns: 280px 1fr; gap: 20px; }
        .sidebar, .main-content { background: var(--panel-bg); border-radius: 8px; border: 1px solid var(--border-color); padding: 20px; }
        h2 { font-size: 1.1rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 15px; }
        .motion-item { padding: 10px; border-radius: 6px; cursor: pointer; display: flex; justify-content: space-between; border: 1px solid transparent; margin-bottom: 5px; }
        .motion-item:hover, .motion-item.active { background: #334155; border-color: var(--accent-cyan); }
        .card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 15px; margin-top: 15px; }
        .card-item { background: #0f172a; border-radius: 6px; border: 1px solid var(--border-color); padding: 15px; position: relative; }
        .card-tag { font-weight: bold; color: var(--accent-cyan); margin-bottom: 5px; font-size: 1.05rem; }
        .card-cite { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 10px; font-style: italic; }
        .card-text { font-size: 0.9rem; max-height: 120px; overflow-y: auto; color: #cbd5e1; }
        .side-badge { position: absolute; top: 15px; right: 15px; padding: 2px 6px; border-radius: 3px; font-size: 0.75rem; font-weight: bold; }
        .side-AFF { background: rgba(16, 185, 129, 0.2); color: var(--aff-color); }
        .side-NEG { background: rgba(239, 68, 68, 0.2); color: var(--neg-color); }
        .controls { display: flex; gap: 10px; margin-bottom: 15px; }
        input[type="text"] { flex: 1; background: #0f172a; border: 1px solid var(--border-color); border-radius: 4px; padding: 8px 12px; color: var(--text-main); }
        button { background: var(--accent-cyan); border: none; color: #0f172a; padding: 8px 16px; border-radius: 4px; font-weight: bold; cursor: pointer; }
        button:hover { opacity: 0.9; }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981; display: inline-block; }
    </style>
</head>
<body>
    <header>
        <div class="logo">
            ⚡ OmniSuite Web Viewer <span class="badge">V1.0</span>
        </div>
        <div style="display: flex; align-items: center; gap: 15px;">
            <span id="conn-status"><span class="status-dot"></span> Live Sync</span>
            <button onclick="triggerSync()">Sync Vault</button>
        </div>
    </header>
    <div class="grid-container">
        <div class="sidebar">
            <h2>Motions</h2>
            <div id="motion-list">Loading motions...</div>
        </div>
        <div class="main-content">
            <div class="controls">
                <input type="text" id="search-input" placeholder="Search cards by tag, citation, or content..." oninput="handleSearch()">
                <button onclick="loadCards()">Refresh</button>
            </div>
            <h2>Evidence Cards (<span id="card-count">0</span>)</h2>
            <div class="card-grid" id="card-grid">Select a motion to view evidence cards.</div>
        </div>
    </div>
    <script>
        let currentMotionId = null;
        async function fetchJSON(url, options = {}) {
            const res = await fetch(url, options);
            return await res.json();
        }
        async function loadMotions() {
            const motions = await fetchJSON('/api/motions');
            const container = document.getElementById('motion-list');
            container.innerHTML = '';
            if (motions.length === 0) {
                container.innerHTML = '<div style="color:var(--text-muted)">No motions found.</div>';
                return;
            }
            motions.forEach(m => {
                const div = document.createElement('div');
                div.className = `motion-item ${m.id === currentMotionId ? 'active' : ''}`;
                div.innerHTML = `<span>${m.name}</span>`;
                div.onclick = () => {
                    currentMotionId = m.id;
                    document.querySelectorAll('.motion-item').forEach(el => el.classList.remove('active'));
                    div.classList.add('active');
                    loadCards();
                };
                container.appendChild(div);
            });
            if (!currentMotionId && motions.length > 0) {
                currentMotionId = motions[0].id;
                document.querySelectorAll('.motion-item')[0].classList.add('active');
                loadCards();
            }
        }
        async function loadCards() {
            if (!currentMotionId) return;
            const q = document.getElementById('search-input').value.trim();
            const url = q ? `/api/cards?q=${encodeURIComponent(q)}` : `/api/cards?motion_id=${currentMotionId}`;
            const cards = await fetchJSON(url);
            const grid = document.getElementById('card-grid');
            document.getElementById('card-count').innerText = cards.length;
            grid.innerHTML = '';
            if (cards.length === 0) {
                grid.innerHTML = '<div style="color:var(--text-muted)">No cards found.</div>';
                return;
            }
            cards.forEach(c => {
                const div = document.createElement('div');
                div.className = 'card-item';
                div.innerHTML = `
                    <span class="side-badge side-${c.side}">${c.side}</span>
                    <div class="card-tag">${c.tag || 'Untitled Tag'}</div>
                    <div class="card-cite">${c.citation || 'No citation'}</div>
                    <div class="card-text">${c.text || ''}</div>
                `;
                grid.appendChild(div);
            });
        }
        function handleSearch() {
            loadCards();
        }
        async function triggerSync() {
            const btn = event.target;
            btn.innerText = 'Syncing...';
            try {
                await fetchJSON('/api/sync', { method: 'POST', body: JSON.stringify({}) });
                alert('Vault synchronized successfully.');
                loadCards();
            } catch (e) {
                alert('Sync failed: ' + e);
            } finally {
                btn.innerText = 'Sync Vault';
            }
        }
        function setupSSE() {
            const eventSource = new EventSource('/api/stream');
            eventSource.addEventListener('sync', e => {
                loadMotions();
                loadCards();
            });
        }
        loadMotions();
        setupSSE();
    </script>
</body>
</html>
"""


class VaultWebHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for OmniSuite Web Viewer API & Frontend."""

    db_path: str | None = None

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress noisy HTTP request logs unless running debug."""
        if os.getenv("OMNISUITE_WEB_DEBUG") == "1":
            super().log_message(format, *args)

    def _send_cors_headers() -> None:
        pass

    def _send_json(self, data: Any, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # Serve Web Viewer UI
        if path in ("/", "/index.html"):
            body = HTML_VIEWER.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Server-Sent Events (SSE) Stream Endpoint
        if path in ("/api/stream", "/api/live-stream"):
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            q: queue.Queue[str] = queue.Queue(maxsize=100)
            with _SUBSCRIBERS_LOCK:
                _EVENT_SUBSCRIBERS.append(q)

            try:
                # Send initial ping event
                init_event = f"event: ping\ndata: {json.dumps({'status': 'connected', 'timestamp': time.time()})}\n\n"
                self.wfile.write(init_event.encode("utf-8"))
                self.wfile.flush()

                while True:
                    try:
                        msg = q.get(timeout=15.0)
                        self.wfile.write(msg.encode("utf-8"))
                        self.wfile.flush()
                    except queue.Empty:
                        # Send heartbeat
                        hb = f"event: heartbeat\ndata: {json.dumps({'time': time.time()})}\n\n"
                        self.wfile.write(hb.encode("utf-8"))
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                with _SUBSCRIBERS_LOCK:
                    if q in _EVENT_SUBSCRIBERS:
                        _EVENT_SUBSCRIBERS.remove(q)
            return

        # API Endpoints
        if path in ("/api/status", "/api/health"):
            motions = list_motions(include_archives=True)
            cards = read_all_cards()
            checksum = compute_vault_checksum(self.db_path)
            self._send_json(
                {
                    "status": "ok",
                    "version": "1.0.0",
                    "db_path": get_db_path(),
                    "vault_checksum": checksum,
                    "motion_count": len(motions),
                    "card_count": len(cards),
                }
            )
            return

        if path == "/api/motions":
            include_archives = query.get("include_archives", ["0"])[0] in ("1", "true")
            motions = list_motions(include_archives=include_archives)
            self._send_json(motions)
            return

        if path == "/api/cards":
            if "q" in query:
                results = search_cards_fts(query["q"][0])
            elif "tag" in query:
                results = get_cards_by_tag(query["tag"][0])
            elif "motion_id" in query:
                try:
                    mid = int(query["motion_id"][0])
                    results = read_vault(mid)
                except ValueError:
                    results = []
            else:
                results = read_all_cards()
            self._send_json(results)
            return

        if path.startswith("/api/cards/"):
            try:
                cid = int(path.split("/")[-1])
                cards = [c for c in read_all_cards() if c["id"] == cid]
                if cards:
                    card = cards[0]
                    card["tags"] = get_card_tags(cid)
                    self._send_json(card)
                else:
                    self._send_json({"error": "Card not found"}, status=HTTPStatus.NOT_FOUND)
            except ValueError:
                self._send_json({"error": "Invalid card ID"}, status=HTTPStatus.BAD_REQUEST)
            return

        if path == "/api/tags":
            tags = list_all_tags()
            self._send_json(tags)
            return

        if path in ("/api/stats", "/api/velocity"):
            stats = get_velocity_stats()
            self._send_json({"velocity": stats, "count": sum(stats)})
            return

        if path == "/api/sync":
            changeset = export_vault_changeset(self.db_path)
            self._send_json(changeset)
            return

        self._send_json({"error": "Not Found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body_data = {}
        if content_length > 0:
            raw_body = self.rfile.read(content_length)
            try:
                body_data = json.loads(raw_body.decode("utf-8"))
            except Exception:
                body_data = {}

        if path == "/api/motions":
            name = body_data.get("name")
            if not name:
                self._send_json({"error": "Motion name required"}, status=HTTPStatus.BAD_REQUEST)
                return
            mid = add_motion(name)
            notify_subscribers("motion_created", {"id": mid, "name": name})
            self._send_json({"status": "created", "id": mid, "name": name}, status=HTTPStatus.CREATED)
            return

        if path == "/api/cards":
            motion_id = body_data.get("motion_id")
            if not motion_id:
                self._send_json({"error": "motion_id is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            add_card(int(motion_id), body_data)
            notify_subscribers("card_created", body_data)
            self._send_json({"status": "created"}, status=HTTPStatus.CREATED)
            return

        if path == "/api/sync":
            strategy = body_data.get("strategy", SyncStrategy.LAST_WRITE_WINS)
            stats = apply_vault_changeset(body_data, db_path=self.db_path, strategy=strategy)
            notify_subscribers("sync", stats)
            self._send_json({"status": "ok", "stats": stats})
            return

        if path.endswith("/rating"):
            parts = path.split("/")
            try:
                cid = int(parts[-2])
                rating = int(body_data.get("rating", 0))
                set_card_rating(cid, rating)
                notify_subscribers("card_rated", {"id": cid, "rating": rating})
                self._send_json({"status": "ok", "id": cid, "rating": rating})
                return
            except ValueError:
                self._send_json({"error": "Invalid card ID or rating"}, status=HTTPStatus.BAD_REQUEST)
                return

        self._send_json({"error": "Not Found"}, status=HTTPStatus.NOT_FOUND)

    def do_PUT(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/cards/"):
            try:
                cid = int(path.split("/")[-1])
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length > 0:
                    card_data = json.loads(self.rfile.read(content_length).decode("utf-8"))
                    update_card(cid, card_data)
                    notify_subscribers("card_updated", {"id": cid, "data": card_data})
                    self._send_json({"status": "updated", "id": cid})
                    return
            except ValueError:
                self._send_json({"error": "Invalid card ID"}, status=HTTPStatus.BAD_REQUEST)
                return

        self._send_json({"error": "Not Found"}, status=HTTPStatus.NOT_FOUND)

    def do_DELETE(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/cards/"):
            try:
                cid = int(path.split("/")[-1])
                query = urllib.parse.parse_qs(parsed.query)
                motion_id = int(query.get("motion_id", [1])[0])
                delete_card(cid, motion_id)
                notify_subscribers("card_deleted", {"id": cid})
                self._send_json({"status": "deleted", "id": cid})
                return
            except ValueError:
                self._send_json({"error": "Invalid card ID"}, status=HTTPStatus.BAD_REQUEST)
                return

        self._send_json({"error": "Not Found"}, status=HTTPStatus.NOT_FOUND)


class OmniWebServer:
    """Encapsulates the OmniSuite lightweight web viewer HTTP server instance."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8080, db_path: str | None = None) -> None:
        self.host = host
        self.port = port
        self.db_path = db_path
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None

        class BoundHandler(VaultWebHandler):
            pass

        BoundHandler.db_path = db_path
        self.handler_class = BoundHandler

    def start(self) -> None:
        """Start the HTTP server in a background daemon thread."""
        if self._server:
            return

        setup_db()

        self._server = HTTPServer((self.host, self.port), self.handler_class)
        # Update bound port if assigned dynamically (port 0)
        self.port = self._server.server_address[1]

        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Gracefully shut down the web server."""
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def is_running(self) -> bool:
        return self._server is not None and self._thread is not None and self._thread.is_alive()


def run_web_server(host: str = "127.0.0.1", port: int = 8080, blocking: bool = True) -> OmniWebServer:
    """Launch and run the OmniSuite Web Viewer server."""
    server = OmniWebServer(host=host, port=port)
    server.start()
    print(f"⚡ OmniSuite Web Viewer running at http://{server.host}:{server.port}")

    if blocking:
        try:
            while server.is_running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nShutting down OmniSuite Web Viewer...")
            server.stop()

    return server


def main(argv: list[str] | None = None) -> None:
    """Command-line entry point for web server."""
    import argparse

    parser = argparse.ArgumentParser(description="OmniSuite Web Viewer Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address to bind")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind")
    args = parser.parse_args(argv)

    run_web_server(host=args.host, port=args.port, blocking=True)


if __name__ == "__main__":
    main()
