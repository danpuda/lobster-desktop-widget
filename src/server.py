#!/usr/bin/env python3
from __future__ import annotations

import json
import mimetypes
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = 8765

SRC_DIR = Path(__file__).resolve().parent
REPO_ROOT = SRC_DIR.parent
AGENTS_PATH = Path("/tmp/pixoo-agents.json")
TODO_PATH = Path("/mnt/c/Users/danpu/OneDrive/Desktop/obsidianVault/openclaw/memory/tasks/todo-priority.md")


def clean_markdown(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\[(.*?)\]\([^)]*\)", r"\1", text)
    text = text.replace("← NEXT", "")
    text = text.replace("✅", "")
    return " ".join(text.strip().strip("-").split())


def extract_top_priority(todo_markdown: str) -> str:
    lines = todo_markdown.splitlines()

    # 優先セクション（"今日・今週の最優先"）を優先して探索
    in_priority = False
    scoped_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            if "今日・今週の最優先" in stripped:
                in_priority = True
                continue
            if in_priority:
                break
        if in_priority:
            scoped_lines.append(line)

    candidates = scoped_lines if scoped_lines else lines

    checkbox_re = re.compile(r"^\s*[-*]\s*\[\s\]\s*(.+?)\s*$")
    heading_re = re.compile(r"^\s*###\s+(.+?)\s*$")

    for line in candidates:
        m = checkbox_re.match(line)
        if m:
            task = clean_markdown(m.group(1))
            if task:
                return task

    for line in candidates:
        m = heading_re.match(line)
        if m:
            title = clean_markdown(m.group(1))
            if title and "完了" not in title:
                return title

    for line in candidates:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
            text = clean_markdown(stripped)
            if text:
                return text

    return ""


class Handler(BaseHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path

        if path == "/agents":
            self.serve_agents()
            return

        if path == "/todo":
            self.serve_todo()
            return

        if path == "/" or path == "/prototype.html":
            self.serve_file(SRC_DIR / "prototype.html")
            return

        if path.startswith("/assets/"):
            self.serve_file(REPO_ROOT / path.lstrip("/"))
            return

        if path.startswith("/src/"):
            self.serve_file(REPO_ROOT / path.lstrip("/"))
            return

        self.send_error(404, "Not Found")

    def serve_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, file_path: Path) -> None:
        try:
            resolved = file_path.resolve(strict=True)
        except FileNotFoundError:
            self.send_error(404, "File Not Found")
            return

        try:
            if not resolved.is_relative_to(REPO_ROOT):
                self.send_error(403, "Forbidden")
                return
        except AttributeError:
            # Python < 3.9 fallback
            if REPO_ROOT not in resolved.parents and resolved != REPO_ROOT:
                self.send_error(403, "Forbidden")
                return

        if not resolved.is_file():
            self.send_error(404, "File Not Found")
            return

        content = resolved.read_bytes()
        content_type, _ = mimetypes.guess_type(str(resolved))

        self.send_response(200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def serve_agents(self) -> None:
        if not AGENTS_PATH.exists():
            self.serve_json({"agents": []})
            return

        try:
            raw = AGENTS_PATH.read_text(encoding="utf-8")
            parsed = json.loads(raw)
        except Exception as exc:  # noqa: BLE001
            self.serve_json({"agents": [], "error": f"invalid json: {exc}"}, status=200)
            return

        if isinstance(parsed, list):
            parsed = {"agents": parsed}
        elif not isinstance(parsed, dict):
            parsed = {"agents": []}

        if "agents" not in parsed or not isinstance(parsed.get("agents"), list):
            parsed["agents"] = []

        self.serve_json(parsed)

    def serve_todo(self) -> None:
        if not TODO_PATH.exists():
            self.serve_json({"todo": "", "error": "todo-priority.md not found"}, status=200)
            return

        try:
            markdown = TODO_PATH.read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            self.serve_json({"todo": "", "error": f"read failed: {exc}"}, status=200)
            return

        todo = extract_top_priority(markdown)
        self.serve_json({"todo": todo})

    def log_message(self, fmt: str, *args) -> None:
        # Keep server output readable
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {fmt % args}")


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Serving on http://localhost:{PORT}")
    print(f"Agents source: {AGENTS_PATH}")
    print(f"TODO source: {TODO_PATH}")
    server.serve_forever()


if __name__ == "__main__":
    main()
