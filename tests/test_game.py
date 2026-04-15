import pytest

from tictactoe.game import Game

_WIN_LINES = [
    [(0, 0), (0, 1), (0, 2)],
    [(1, 0), (1, 1), (1, 2)],
    [(2, 0), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (2, 0)],
    [(0, 1), (1, 1), (2, 1)],
    [(0, 2), (1, 2), (2, 2)],
    [(0, 0), (1, 1), (2, 2)],
    [(0, 2), (1, 1), (2, 0)],
]


@pytest.mark.parametrize("winning_line", _WIN_LINES)
def test_win_detection_all_eight_lines(winning_line):
    game = Game()
    other_cells = [(r, c) for r in range(3) for c in range(3) if (r, c) not in winning_line]
    for i, (wr, wc) in enumerate(winning_line):
        game.make_move(wr, wc)
        if i < len(winning_line) - 1:
            game.make_move(other_cells[i][0], other_cells[i][1])
    assert game.winner == "X"
    assert not game.is_draw


def test_draw_detection():
    game = Game()
    # Fills board with no winner: X O X / X X O / O X O
    for row, col in [(0, 0), (0, 1), (0, 2), (1, 2), (1, 0), (2, 0), (1, 1), (2, 2), (2, 1)]:
        game.make_move(row, col)
    assert game.is_draw
    assert game.winner is None


def test_illegal_move_occupied_cell():
    game = Game()
    game.make_move(0, 0)
    game.make_move(1, 1)
    with pytest.raises(ValueError, match="occupied"):
        game.make_move(0, 0)


def test_illegal_move_after_game_over():
    game = Game()
    for row, col in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]:
        game.make_move(row, col)
    assert game.winner == "X"
    with pytest.raises(ValueError, match="already over"):
        game.make_move(2, 2)


def test_reset_clears_state():
    game = Game()
    game.make_move(0, 0)
    game.reset()
    assert game.board == [[None] * 3 for _ in range(3)]
    assert game.current_player == "X"
    assert game.winner is None
    assert not game.is_draw


def test_players_alternate():
    game = Game()
    assert game.current_player == "X"
    game.make_move(0, 0)
    assert game.current_player == "O"
    game.make_move(1, 1)
    assert game.current_player == "X"
