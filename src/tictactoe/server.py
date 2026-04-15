from __future__ import annotations

import json
import socketserver
from http.server import BaseHTTPRequestHandler
from pathlib import Path

from tictactoe.game import Game

_game = Game()
_STATIC_DIR = Path(__file__).parent / "static"


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def _send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/":
            html = (_STATIC_DIR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
        elif self.path == "/state":
            self._send_json(_game.to_dict())
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        if self.path == "/move":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                row = int(data["row"])
                col = int(data["col"])
            except (KeyError, ValueError, json.JSONDecodeError) as exc:
                self._send_json({"error": str(exc)}, 400)
                return
            try:
                _game.make_move(row, col)
                self._send_json(_game.to_dict())
            except ValueError as exc:
                self._send_json({"error": str(exc)}, 400)
        elif self.path == "/new_game":
            _game.reset()
            self._send_json(_game.to_dict())
        else:
            self.send_error(404)


class _ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def run_server(host: str, port: int) -> None:
    with _ReusableTCPServer((host, port), _Handler) as httpd:
        httpd.serve_forever()


def main() -> None:
    host = "0.0.0.0"
    port = 8000
    print(f"Serving at http://localhost:{port}/")
    run_server(host, port)
