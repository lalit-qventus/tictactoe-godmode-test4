import json
import threading
import urllib.error
import urllib.request

import pytest

from tictactoe.server import _Handler, _ReusableTCPServer, _game


@pytest.fixture()
def server():
    _game.reset()
    httpd = _ReusableTCPServer(("127.0.0.1", 0), _Handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    yield f"http://127.0.0.1:{port}"
    httpd.shutdown()


def _get(url: str) -> dict:
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read())


def _post(url: str, data: dict | None = None) -> tuple[int, dict]:
    body = json.dumps(data or {}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_get_state_returns_empty_board(server):
    state = _get(f"{server}/state")
    assert state["board"] == [[None] * 3 for _ in range(3)]
    assert state["current_player"] == "X"
    assert state["winner"] is None
    assert state["is_draw"] is False


def test_post_move_updates_board(server):
    status, state = _post(f"{server}/move", {"row": 0, "col": 0})
    assert status == 200
    assert state["board"][0][0] == "X"
    assert state["current_player"] == "O"


def test_post_move_occupied_returns_400(server):
    _post(f"{server}/move", {"row": 0, "col": 0})
    _post(f"{server}/move", {"row": 1, "col": 1})
    status, data = _post(f"{server}/move", {"row": 0, "col": 0})
    assert status == 400
    assert "error" in data


def test_post_move_after_game_over_returns_400(server):
    for row, col in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]:
        _post(f"{server}/move", {"row": row, "col": col})
    status, data = _post(f"{server}/move", {"row": 2, "col": 2})
    assert status == 400
    assert "error" in data


def test_post_new_game_resets_state(server):
    _post(f"{server}/move", {"row": 0, "col": 0})
    status, state = _post(f"{server}/new_game")
    assert status == 200
    assert state["board"] == [[None] * 3 for _ in range(3)]
    assert state["current_player"] == "X"
    assert state["winner"] is None


def test_get_root_returns_html(server):
    with urllib.request.urlopen(f"{server}/") as resp:
        assert resp.status == 200
        content_type = resp.headers.get("Content-Type", "")
        assert "text/html" in content_type
        body = resp.read().decode()
        assert "<title>Tic-Tac-Toe</title>" in body
