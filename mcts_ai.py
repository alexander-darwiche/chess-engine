import math
import os
import random
import sys
import time
from copy import deepcopy
from pathlib import Path

from chess import Chess


MATE_SCORE = 100000
NULL_MOVE_REDUCTION = 2
LMR_MIN_DEPTH = 3
LMR_MIN_MOVE_INDEX = 4
ASPIRATION_INITIAL_WINDOW = 60
ASPIRATION_MAX_WINDOW = 2200

PIECE_VALUES = {
    1: 100,
    2: 320,
    3: 330,
    4: 500,
    5: 900,
    6: 20000,
}

MOVE_ORDER_COST = {
    1: 12,
    2: 20,
    3: 22,
    4: 28,
    5: 38,
    6: 44,
}

PAWN_PST = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [0, 0, 0, 25, 25, 0, 0, 0],
    [5, 5, 10, 35, 35, 10, 5, 5],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

KNIGHT_PST = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]

BISHOP_PST = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20],
]

ROOK_PST = [
    [0, 0, 0, 5, 5, 0, 0, 0],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

QUEEN_PST = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 5, 0, -10],
    [-10, 0, 5, 5, 5, 5, 5, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20],
]

KING_MID_PST = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20],
]

PST_BY_PIECE = {
    1: PAWN_PST,
    2: KNIGHT_PST,
    3: BISHOP_PST,
    4: ROOK_PST,
    5: QUEEN_PST,
    6: KING_MID_PST,
}

OPENING_LINES = [
    ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6", "d2d3", "f8c5", "c2c3", "d7d6"],
    ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4", "g8f6", "b1c3", "a7a6"],
    ["d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6", "c1g5", "f8e7", "e2e3", "e8g8"],
    ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "f8g7", "e2e4", "d7d6", "g1f3", "e8g8"],
    ["c2c4", "e7e5", "b1c3", "g8f6", "g2g3", "d7d5", "c4d5", "f6d5", "f1g2", "d5b6"],
    ["e2e4", "e7e6", "d2d4", "d7d5", "b1c3", "g8f6", "c1g5", "f8b4", "e4e5", "h7h6"],
]


class SearchTimeout(Exception):
    pass


_PYTHON_CHESS = None
_SYZYGY = None
_SYZYGY_TABLEBASE = None
_SYZYGY_INIT_TRIED = False


def _maybe_load_python_chess_syzygy():
    global _PYTHON_CHESS, _SYZYGY, _SYZYGY_INIT_TRIED
    if _SYZYGY_INIT_TRIED:
        return _PYTHON_CHESS is not None and _SYZYGY is not None
    _SYZYGY_INIT_TRIED = True

    project_dir = Path(__file__).resolve().parent
    original_sys_path = list(sys.path)
    local_chess_module = sys.modules.get("chess")

    removed_local = False
    if local_chess_module is not None and str(getattr(local_chess_module, "__file__", "")).lower().endswith("chess.py"):
        del sys.modules["chess"]
        removed_local = True

    try:
        filtered_path = []
        for entry in sys.path:
            try:
                if Path(entry).resolve() == project_dir:
                    continue
            except Exception:
                pass
            filtered_path.append(entry)
        sys.path = filtered_path

        import importlib

        pychess = importlib.import_module("chess")
        syzygy = importlib.import_module("chess.syzygy")
        _PYTHON_CHESS = pychess
        _SYZYGY = syzygy
        return True
    except Exception:
        _PYTHON_CHESS = None
        _SYZYGY = None
        return False
    finally:
        sys.path = original_sys_path
        if removed_local and local_chess_module is not None:
            sys.modules["chess"] = local_chess_module


def _piece_placement_fen(game):
    rows = []
    piece_chars = {
        1: "p",
        2: "n",
        3: "b",
        4: "r",
        5: "q",
        6: "k",
    }
    for row in game.board:
        empty = 0
        fen_row = []
        for piece in row:
            if piece == 0:
                empty += 1
                continue
            if empty > 0:
                fen_row.append(str(empty))
                empty = 0
            char = piece_chars[abs(piece)]
            fen_row.append(char.upper() if piece > 0 else char)
        if empty > 0:
            fen_row.append(str(empty))
        rows.append("".join(fen_row))
    return "/".join(rows)


def _castling_fen(game):
    rights = []
    if len(game.castling) >= 4:
        if game.castling[3] == 1:
            rights.append("K")
        if game.castling[2] == 1:
            rights.append("Q")
        if game.castling[1] == 1:
            rights.append("k")
        if game.castling[0] == 1:
            rights.append("q")
    return "".join(rights) if rights else "-"


def _to_fen(game, halfmove_clock, fullmove_number):
    active = "w" if game.current_player == 1 else "b"
    return f"{_piece_placement_fen(game)} {active} {_castling_fen(game)} - {halfmove_clock} {max(1, fullmove_number)}"


def _position_key(game):
    board_key = tuple(tuple(rank) for rank in game.board)
    return board_key, game.current_player, tuple(game.castling)


def _legal_moves(game):
    moves_dict = game.get_all_moves_dict(for_player=game.current_player)
    moves = []
    for from_square, move_data in moves_dict.items():
        for x, y in move_data[1]:
            to_square = game.x_notation[x] + game.y_notation[y]
            moves.append((from_square, to_square))
    return moves


def _piece_at(game, square):
    x = game.x_notation.index(square[0])
    y = game.y_notation.index(square[1])
    return game.board[y][x]


def _square_xy(game, square):
    x = game.x_notation.index(square[0])
    y = game.y_notation.index(square[1])
    return x, y


def _apply_move(game, move):
    from_square, to_square = move
    next_game = deepcopy(game)
    next_game.move_piece(from_square, to_square)
    next_game.promotable_pawns()
    return next_game


def _is_terminal(game):
    if game.is_stalemate() or game.is_king_bishop_draw():
        return True
    if game.is_check()[1] and game.is_checkmate():
        return True
    return False


def _is_capture(game, move):
    _, to_square = move
    return _piece_at(game, to_square) != 0


def _build_opening_book():
    book = {}
    for line in OPENING_LINES:
        game = Chess()
        for move_uci in line:
            from_square = move_uci[:2]
            to_square = move_uci[2:]
            legal = _legal_moves(game)
            move = (from_square, to_square)
            if move not in legal:
                break
            key = _position_key(game)
            bucket = book.setdefault(key, [])
            if move not in bucket:
                bucket.append(move)
            game.move_piece(from_square, to_square)
            game.promotable_pawns()
    return book


OPENING_BOOK = _build_opening_book()


class MCTS_ai:
    def __init__(
        self,
        game,
        parent=None,
        parent_move=None,
        possible_moves=None,
        max_depth=10,
        rollout_depth=14,
        max_branching=18,
        exploration=1.35,
        avoid_position_counts=None,
        position_history_counts=None,
        root_halfmove_clock=0,
        syzygy_path=None,
    ):
        self.game = deepcopy(game)
        self.parent = parent
        self.parent_move = parent_move
        self.possible_moves = possible_moves
        self.max_depth = max_depth
        self.rollout_depth = rollout_depth
        self.max_branching = max_branching
        self.exploration = exploration
        self.max_depth_reached = 0
        self.root_player = self.game.current_player
        self.avoid_position_counts = avoid_position_counts or {}
        self.position_history_counts = position_history_counts or {_position_key(self.game): 1}
        self.root_halfmove_clock = max(0, int(root_halfmove_clock))
        self.syzygy_path = syzygy_path if syzygy_path is not None else os.getenv("SYZYGY_PATH", "")

        self.nodes_searched = 0
        self.node_budget = 20000
        self.deadline = 0.0
        self.transposition = {}
        self.killer_moves = {}
        self.history_heuristic = {}
        self.ply_counter = 1
        self.use_syzygy = False
        self.last_root_score = 0
        self.last_completed_depth = 0
        self.quiescence_depth = max(3, min(24, int(self.rollout_depth)))
        self.used_opening_book = False

        self._initialize_syzygy()

    def _piece_square_score(self, piece, x, y):
        table = PST_BY_PIECE.get(abs(piece))
        if table is None:
            return 0
        row = y if piece > 0 else 7 - y
        return table[row][x]

    def _pawn_structure_score(self, game, player):
        files = {i: [] for i in range(8)}
        for y, rank in enumerate(game.board):
            for x, piece in enumerate(rank):
                if piece == player:
                    files[x].append(y)

        score = 0
        for file_idx, pawns in files.items():
            if len(pawns) > 1:
                score -= 14 * (len(pawns) - 1)
            if not pawns:
                continue
            left = files[file_idx - 1] if file_idx > 0 else []
            right = files[file_idx + 1] if file_idx < 7 else []
            if not left and not right:
                score -= 18
        return score

    def _development_score(self, game, player):
        score = 0
        back_rank = 7 if player == 1 else 0
        minor_targets = {
            (1, back_rank): 2 * player,
            (6, back_rank): 2 * player,
            (2, back_rank): 3 * player,
            (5, back_rank): 3 * player,
        }
        for (x, y), expected in minor_targets.items():
            if game.board[y][x] != expected:
                score += 15
        return score

    def _king_safety_score(self, game, player):
        king_piece = 6 * player
        king_x = None
        king_y = None
        for y, rank in enumerate(game.board):
            for x, piece in enumerate(rank):
                if piece == king_piece:
                    king_x = x
                    king_y = y
                    break
            if king_x is not None:
                break

        if king_x is None:
            return -500

        score = 0
        pawn_piece = 1 * player
        shield_y = king_y - 1 if player == 1 else king_y + 1
        if 0 <= shield_y <= 7:
            for dx in (-1, 0, 1):
                x = king_x + dx
                if 0 <= x <= 7 and game.board[shield_y][x] == pawn_piece:
                    score += 8

        if (player == 1 and king_y >= 6) or (player == -1 and king_y <= 1):
            score += 12
        return score

    def _pseudo_mobility(self, game, player):
        knight_jumps = (
            (1, 2), (2, 1), (-1, 2), (-2, 1),
            (1, -2), (2, -1), (-1, -2), (-2, -1),
        )
        bishop_dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))
        rook_dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))

        score = 0
        for y, rank in enumerate(game.board):
            for x, piece in enumerate(rank):
                if piece == 0 or piece * player <= 0:
                    continue

                abs_piece = abs(piece)
                if abs_piece == 1:
                    step = -1 if piece > 0 else 1
                    ny = y + step
                    if 0 <= ny <= 7:
                        if game.board[ny][x] == 0:
                            score += 1
                        for nx in (x - 1, x + 1):
                            if 0 <= nx <= 7 and game.board[ny][nx] * piece < 0:
                                score += 1
                elif abs_piece == 2:
                    for dx, dy in knight_jumps:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx <= 7 and 0 <= ny <= 7 and game.board[ny][nx] * piece <= 0:
                            score += 1
                elif abs_piece in (3, 4, 5):
                    directions = bishop_dirs
                    if abs_piece == 4:
                        directions = rook_dirs
                    elif abs_piece == 5:
                        directions = bishop_dirs + rook_dirs
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        while 0 <= nx <= 7 and 0 <= ny <= 7:
                            target = game.board[ny][nx]
                            if target == 0:
                                score += 1
                            elif target * piece < 0:
                                score += 1
                                break
                            else:
                                break
                            nx += dx
                            ny += dy
                elif abs_piece == 6:
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx <= 7 and 0 <= ny <= 7 and game.board[ny][nx] * piece <= 0:
                                score += 1
        return score

    def _evaluate_for(self, game, player):
        material = 0
        pst = 0
        center = 0

        for y, rank in enumerate(game.board):
            for x, piece in enumerate(rank):
                if piece == 0:
                    continue
                sign = 1 if piece * player > 0 else -1
                material += sign * PIECE_VALUES[abs(piece)]
                pst += sign * self._piece_square_score(piece, x, y)

                dist_to_center = abs(3.5 - x) + abs(3.5 - y)
                center_bonus = max(0, 5 - dist_to_center)
                center += sign * int(center_bonus * 6)

        my_pawns = self._pawn_structure_score(game, player)
        opp_pawns = self._pawn_structure_score(game, -player)
        dev = self._development_score(game, player) - self._development_score(game, -player)
        king = self._king_safety_score(game, player) - self._king_safety_score(game, -player)
        mobility = (self._pseudo_mobility(game, player) - self._pseudo_mobility(game, -player)) * 2

        return material + pst + center + (my_pawns - opp_pawns) + dev + king + mobility

    def _initialize_syzygy(self):
        global _SYZYGY_TABLEBASE
        if not self.syzygy_path:
            return
        if not _maybe_load_python_chess_syzygy():
            return
        if _SYZYGY_TABLEBASE is None:
            try:
                _SYZYGY_TABLEBASE = _SYZYGY.open_tablebase(self.syzygy_path)
            except Exception:
                _SYZYGY_TABLEBASE = None
                return
        self.use_syzygy = _SYZYGY_TABLEBASE is not None

    def _probe_syzygy(self, game, halfmove_clock, ply):
        if not self.use_syzygy or _SYZYGY_TABLEBASE is None:
            return None
        piece_count = sum(1 for rank in game.board for piece in rank if piece != 0)
        if piece_count > 7:
            return None

        try:
            fullmove_number = max(1, self.ply_counter // 2)
            fen = _to_fen(game, halfmove_clock, fullmove_number)
            board = _PYTHON_CHESS.Board(fen=fen)
            wdl = _SYZYGY_TABLEBASE.probe_wdl(board)
        except Exception:
            return None

        if wdl >= 2:
            return MATE_SCORE - 150 + ply
        if wdl == 1:
            return 1200
        if wdl == 0:
            return 0
        if wdl == -1:
            return -1200
        return -MATE_SCORE + 150 - ply

    def _is_pawn_move(self, game, move):
        from_square, _ = move
        return abs(_piece_at(game, from_square)) == 1

    def _move_details(self, game, move):
        is_capture = _is_capture(game, move)
        is_pawn = self._is_pawn_move(game, move)
        return is_capture, is_pawn

    def _terminal_score(self, game, ply, halfmove_clock, repetition_counts):
        if repetition_counts.get(_position_key(game), 0) >= 3:
            return 0
        if halfmove_clock >= 100:
            return 0

        syzygy_score = self._probe_syzygy(game, halfmove_clock, ply)
        if syzygy_score is not None:
            return syzygy_score

        if game.is_stalemate() or game.is_king_bishop_draw():
            return 0
        if game.is_check()[1] and game.is_checkmate():
            return -MATE_SCORE + ply
        return None

    def _move_order_key(self, game, move):
        from_square, to_square = move
        moving_piece = _piece_at(game, from_square)
        moving = abs(moving_piece)
        captured_piece = abs(_piece_at(game, to_square))

        from_x, from_y = _square_xy(game, from_square)
        to_x, to_y = _square_xy(game, to_square)

        capture_bonus = PIECE_VALUES.get(captured_piece, 0) - MOVE_ORDER_COST.get(moving, 0)
        promotion_bonus = 0
        if moving == 1 and (to_y == 0 or to_y == 7):
            promotion_bonus = 800

        center_distance = abs(3.5 - to_x) + abs(3.5 - to_y)
        center_bonus = int((7.0 - center_distance) * 5)

        development_bonus = 0
        if moving in (2, 3):
            if moving_piece > 0 and from_y == 7:
                development_bonus += 20
            elif moving_piece < 0 and from_y == 0:
                development_bonus += 20

        forward_bonus = 0
        if moving_piece > 0:
            forward_bonus = max(0, from_y - to_y) * 2
        else:
            forward_bonus = max(0, to_y - from_y) * 2

        return capture_bonus + promotion_bonus + center_bonus + development_bonus + forward_bonus

    def _history_key(self, game, move):
        from_square, to_square = move
        return game.current_player, from_square, to_square

    def _branch_cap_for_ply(self, ply, in_check):
        if in_check:
            return self.max_branching
        if ply <= 0:
            return self.max_branching
        if ply == 1:
            return max(12, self.max_branching - 4)
        if ply <= 3:
            return max(8, self.max_branching // 2)
        return max(6, self.max_branching // 3)

    def _order_moves(self, game, moves, tt_move=None, ply=0, captures_only=False, in_check=False):
        ordered = list(moves)
        random.shuffle(ordered)
        killer_bucket = self.killer_moves.get(ply, [])

        def sort_key(move):
            score = self._move_order_key(game, move)
            history_bonus = self.history_heuristic.get(self._history_key(game, move), 0)
            score += history_bonus
            if move in killer_bucket:
                score += 1200
            return score

        ordered.sort(key=sort_key, reverse=True)
        if tt_move is not None and tt_move in ordered:
            ordered.remove(tt_move)
            ordered.insert(0, tt_move)
        if captures_only:
            return ordered
        branch_cap = self._branch_cap_for_ply(ply, in_check)
        return ordered[: branch_cap]

    def _check_limits(self):
        if self.nodes_searched >= self.node_budget:
            raise SearchTimeout()
        if time.perf_counter() >= self.deadline:
            raise SearchTimeout()

    def _quiescence(self, game, alpha, beta, q_depth, ply, halfmove_clock, repetition_counts):
        self._check_limits()
        self.nodes_searched += 1

        terminal = self._terminal_score(game, ply, halfmove_clock, repetition_counts)
        if terminal is not None:
            return terminal

        stand_pat = self._evaluate_for(game, game.current_player)
        if q_depth >= self.quiescence_depth:
            return stand_pat

        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat

        captures = [move for move in _legal_moves(game) if _is_capture(game, move)]
        if not captures:
            return stand_pat

        ordered_captures = self._order_moves(game, captures, ply=ply, captures_only=True)
        for move in ordered_captures:
            child = _apply_move(game, move)
            is_capture, is_pawn = self._move_details(game, move)
            child_halfmove = 0 if (is_capture or is_pawn) else halfmove_clock + 1
            child_key = _position_key(child)
            repetition_counts[child_key] = repetition_counts.get(child_key, 0) + 1
            score = -self._quiescence(child, -beta, -alpha, q_depth + 1, ply + 1, child_halfmove, repetition_counts)
            repetition_counts[child_key] -= 1
            if repetition_counts[child_key] <= 0:
                del repetition_counts[child_key]
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    def _alphabeta(self, game, depth, alpha, beta, ply, halfmove_clock, repetition_counts, allow_null=True):
        self._check_limits()
        self.nodes_searched += 1
        self.max_depth_reached = max(self.max_depth_reached, ply)

        terminal = self._terminal_score(game, ply, halfmove_clock, repetition_counts)
        if terminal is not None:
            return terminal

        if depth <= 0:
            return self._quiescence(game, alpha, beta, 0, ply, halfmove_clock, repetition_counts)

        in_check = game.is_check()[1]
        if allow_null and depth >= 3 and not in_check:
            null_game = deepcopy(game)
            null_game.current_player = -null_game.current_player
            null_key = _position_key(null_game)
            repetition_counts[null_key] = repetition_counts.get(null_key, 0) + 1
            score = -self._alphabeta(
                null_game,
                depth - 1 - NULL_MOVE_REDUCTION,
                -beta,
                -beta + 1,
                ply + 1,
                halfmove_clock + 1,
                repetition_counts,
                allow_null=False,
            )
            repetition_counts[null_key] -= 1
            if repetition_counts[null_key] <= 0:
                del repetition_counts[null_key]
            if score >= beta:
                return beta

        key = _position_key(game)
        tt_entry = self.transposition.get(key)
        alpha_orig = alpha
        tt_move = None
        if tt_entry is not None and tt_entry["depth"] >= depth:
            tt_move = tt_entry["move"]
            if tt_entry["flag"] == "exact":
                return tt_entry["value"]
            if tt_entry["flag"] == "lower":
                alpha = max(alpha, tt_entry["value"])
            elif tt_entry["flag"] == "upper":
                beta = min(beta, tt_entry["value"])
            if alpha >= beta:
                return tt_entry["value"]

        legal_moves = _legal_moves(game)
        if not legal_moves:
            if in_check:
                return -MATE_SCORE + ply
            return 0

        ordered_moves = self._order_moves(game, legal_moves, tt_move=tt_move, ply=ply, in_check=in_check)

        best_value = -math.inf
        best_move = ordered_moves[0]
        move_index = 0

        for move in ordered_moves:
            child = _apply_move(game, move)
            is_capture, is_pawn = self._move_details(game, move)
            child_halfmove = 0 if (is_capture or is_pawn) else halfmove_clock + 1
            child_key = _position_key(child)
            repetition_counts[child_key] = repetition_counts.get(child_key, 0) + 1

            gives_check = False
            reduction = 0
            if (
                depth >= LMR_MIN_DEPTH
                and move_index >= LMR_MIN_MOVE_INDEX
                and not is_capture
                and not is_pawn
                and not in_check
                and not gives_check
            ):
                reduction = 1
                if depth >= 6 and move_index >= 8:
                    reduction = 2

            if reduction > 0:
                score = -self._alphabeta(
                    child,
                    depth - 1 - reduction,
                    -alpha - 1,
                    -alpha,
                    ply + 1,
                    child_halfmove,
                    repetition_counts,
                )
                if score > alpha:
                    score = -self._alphabeta(
                        child,
                        depth - 1,
                        -beta,
                        -alpha,
                        ply + 1,
                        child_halfmove,
                        repetition_counts,
                    )
            else:
                score = -self._alphabeta(
                    child,
                    depth - 1,
                    -beta,
                    -alpha,
                    ply + 1,
                    child_halfmove,
                    repetition_counts,
                )

            repetition_counts[child_key] -= 1
            if repetition_counts[child_key] <= 0:
                del repetition_counts[child_key]

            if score > best_value:
                best_value = score
                best_move = move

            if score > alpha:
                alpha = score
            if alpha >= beta:
                if not is_capture:
                    bucket = self.killer_moves.setdefault(ply, [])
                    if move not in bucket:
                        bucket.insert(0, move)
                        del bucket[2:]
                    hist_key = self._history_key(game, move)
                    self.history_heuristic[hist_key] = self.history_heuristic.get(hist_key, 0) + (depth * depth)
                break
            move_index += 1

        if best_value <= alpha_orig:
            flag = "upper"
        elif best_value >= beta:
            flag = "lower"
        else:
            flag = "exact"
        self.transposition[key] = {"depth": depth, "value": best_value, "flag": flag, "move": best_move}

        return best_value

    def _search_root(self, depth, halfmove_clock, repetition_counts, alpha=-math.inf, beta=math.inf):
        legal_moves = _legal_moves(self.game)
        if not legal_moves:
            return None, -math.inf

        key = _position_key(self.game)
        tt_entry = self.transposition.get(key)
        tt_move = tt_entry["move"] if tt_entry is not None else None
        in_check = self.game.is_check()[1]
        ordered_moves = self._order_moves(self.game, legal_moves, tt_move=tt_move, ply=0, in_check=in_check)

        best_move = ordered_moves[0]
        best_score = -math.inf

        for move_index, move in enumerate(ordered_moves):
            child = _apply_move(self.game, move)
            child_key = _position_key(child)
            is_capture, is_pawn = self._move_details(self.game, move)
            child_halfmove = 0 if (is_capture or is_pawn) else halfmove_clock + 1
            repetition_counts[child_key] = repetition_counts.get(child_key, 0) + 1
            if move_index == 0:
                score = -self._alphabeta(child, depth - 1, -beta, -alpha, 1, child_halfmove, repetition_counts)
            else:
                score = -self._alphabeta(child, depth - 1, -alpha - 1, -alpha, 1, child_halfmove, repetition_counts)
                if score > alpha:
                    score = -self._alphabeta(child, depth - 1, -beta, -alpha, 1, child_halfmove, repetition_counts)
            repetition_counts[child_key] -= 1
            if repetition_counts[child_key] <= 0:
                del repetition_counts[child_key]

            repeat_count = self.avoid_position_counts.get(child_key, 0)
            if repeat_count > 0:
                score -= 220 * repeat_count

            if child.is_check()[1] and child.current_player == -self.root_player:
                score += 60

            score += self._evaluate_for(child, self.root_player) * 0.02

            if score > best_score:
                best_score = score
                best_move = move
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break

        return best_move, best_score

    def _book_move(self):
        key = _position_key(self.game)
        options = OPENING_BOOK.get(key, [])
        if not options:
            return None
        legal = set(_legal_moves(self.game))
        legal_options = [move for move in options if move in legal]
        if not legal_options:
            return None
        return random.choice(legal_options)

    def play(self, iterations=600, time_limit_seconds=1.5, min_depth=10):
        self.used_opening_book = False
        book_move = self._book_move()
        if book_move is not None:
            from_square, to_square = book_move
            self.max_depth_reached = 0
            self.last_completed_depth = 0
            self.last_root_score = 0
            self.used_opening_book = True
            return None, f"{from_square} to {to_square}"

        self.max_depth_reached = 0
        self.nodes_searched = 0
        self.transposition = {}
        self.killer_moves = {}
        self.history_heuristic = {}
        self.node_budget = max(1500, int(iterations) * 50)
        self.deadline = time.perf_counter() + max(0.05, time_limit_seconds)
        self.ply_counter += 1

        target_depth = max(1, min(self.max_depth, min_depth))
        best_move = None
        best_score = -math.inf
        reached_depth = 0

        try:
            root_repetition = dict(self.position_history_counts)
            root_key = _position_key(self.game)
            root_repetition[root_key] = max(1, root_repetition.get(root_key, 0))
            aspiration_center = None
            for depth in range(1, target_depth + 1):
                if aspiration_center is None or depth <= 2:
                    move, score = self._search_root(depth, self.root_halfmove_clock, root_repetition)
                else:
                    window = ASPIRATION_INITIAL_WINDOW
                    move = None
                    score = None
                    while True:
                        alpha = aspiration_center - window
                        beta = aspiration_center + window
                        candidate_move, candidate_score = self._search_root(
                            depth,
                            self.root_halfmove_clock,
                            root_repetition,
                            alpha=alpha,
                            beta=beta,
                        )
                        move = candidate_move
                        score = candidate_score
                        if score <= alpha:
                            window = min(window * 2, ASPIRATION_MAX_WINDOW)
                            if window >= ASPIRATION_MAX_WINDOW:
                                move, score = self._search_root(depth, self.root_halfmove_clock, root_repetition)
                                break
                            continue
                        if score >= beta:
                            window = min(window * 2, ASPIRATION_MAX_WINDOW)
                            if window >= ASPIRATION_MAX_WINDOW:
                                move, score = self._search_root(depth, self.root_halfmove_clock, root_repetition)
                                break
                            continue
                        break
                if move is not None:
                    best_move = move
                    best_score = score
                    reached_depth = depth
                    aspiration_center = score
        except SearchTimeout:
            pass

        if best_move is None:
            legal = _legal_moves(self.game)
            if not legal:
                return None, ""
            best_move = random.choice(legal)

        self.max_depth_reached = reached_depth
        self.last_completed_depth = reached_depth
        if best_score != -math.inf:
            self.last_root_score = int(best_score)
        from_square, to_square = best_move
        return None, f"{from_square} to {to_square}"

    def mcts_viz_helper(self):
        print("Search core: alpha-beta iterative deepening with transposition/quiescence")
        print("Nodes searched:", self.nodes_searched)
        print("Depth reached:", self.max_depth_reached)
