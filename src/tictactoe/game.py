from __future__ import annotations


class Game:
    WIN_LINES: tuple[tuple[tuple[int, int], ...], ...] = (
        ((0, 0), (0, 1), (0, 2)),
        ((1, 0), (1, 1), (1, 2)),
        ((2, 0), (2, 1), (2, 2)),
        ((0, 0), (1, 0), (2, 0)),
        ((0, 1), (1, 1), (2, 1)),
        ((0, 2), (1, 2), (2, 2)),
        ((0, 0), (1, 1), (2, 2)),
        ((0, 2), (1, 1), (2, 0)),
    )

    def __init__(self) -> None:
        self.board: list[list[str | None]] = [[None] * 3 for _ in range(3)]
        self.current_player: str = "X"
        self.winner: str | None = None
        self.is_draw: bool = False

    def make_move(self, row: int, col: int) -> None:
        if self.winner or self.is_draw:
            raise ValueError("Game is already over")
        if not (0 <= row <= 2 and 0 <= col <= 2):
            raise ValueError("Position out of range")
        if self.board[row][col] is not None:
            raise ValueError("Cell already occupied")
        self.board[row][col] = self.current_player
        self._check_winner()
        if not self.winner:
            if all(self.board[r][c] is not None for r in range(3) for c in range(3)):
                self.is_draw = True
            else:
                self.current_player = "O" if self.current_player == "X" else "X"

    def _check_winner(self) -> None:
        for line in self.WIN_LINES:
            values = [self.board[r][c] for r, c in line]
            if values[0] and values[0] == values[1] == values[2]:
                self.winner = values[0]
                return

    def reset(self) -> None:
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = "X"
        self.winner = None
        self.is_draw = False

    def to_dict(self) -> dict:
        return {
            "board": self.board,
            "current_player": self.current_player,
            "winner": self.winner,
            "is_draw": self.is_draw,
        }
