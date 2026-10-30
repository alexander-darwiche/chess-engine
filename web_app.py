import json
import mimetypes
import os
import queue
import random
import threading
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse
from copy import deepcopy
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Lock

from chess import Chess
import mcts_ai
import random_ai


ROOT_DIR = Path(__file__).resolve().parent
INDEX_PATH = ROOT_DIR / "index.html"
ABOUT_PATH = ROOT_DIR / "about.html"


PIECE_CODES = {
    1: "P",
    2: "N",
    3: "B",
    4: "R",
    5: "Q",
    6: "K",
}


def to_notation(game: Chess, x: int, y: int) -> str:
    return f"{game.x_notation[x]}{game.y_notation[y]}"


def to_xy(game: Chess, square: str):
    if not isinstance(square, str) or len(square) != 2:
        return None
    file_char = square[0].lower()
    rank_char = square[1]
    if file_char not in game.x_notation or rank_char not in game.y_notation:
        return None
    return game.x_notation.index(file_char), game.y_notation.index(rank_char)


def board_to_payload(game: Chess):
    board_payload = []
    for row in game.board:
        row_payload = []
        for piece in row:
            if piece == 0:
                row_payload.append("")
            else:
                color = "w" if piece > 0 else "b"
                row_payload.append(f"{color}{PIECE_CODES[abs(piece)]}")
        board_payload.append(row_payload)
    return board_payload


def legal_moves_for_current_player(game: Chess):
    moves = game.get_all_moves_dict(for_player=game.current_player)
    serialized = {}
    for start, move_info in moves.items():
        serialized[start] = [to_notation(game, x, y) for x, y in move_info[1]]
    return serialized


def position_key(game: Chess):
    board_key = tuple(tuple(rank) for rank in game.board)
    return board_key, game.current_player, tuple(game.castling)


def board_to_fen(game: Chess, halfmove_clock: int = 0, fullmove_number: int = 1):
    piece_map = {
        1: "p",
        2: "n",
        3: "b",
        4: "r",
        5: "q",
        6: "k",
    }
    rows = []
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
            char = piece_map[abs(piece)]
            fen_row.append(char.upper() if piece > 0 else char)
        if empty > 0:
            fen_row.append(str(empty))
        rows.append("".join(fen_row))

    castling = "-"
    if len(game.castling) >= 4:
        rights = []
        if game.castling[3] == 1:
            rights.append("K")
        if game.castling[2] == 1:
            rights.append("Q")
        if game.castling[1] == 1:
            rights.append("k")
        if game.castling[0] == 1:
            rights.append("q")
        castling = "".join(rights) if rights else "-"

    active = "w" if game.current_player == 1 else "b"
    return f"{'/'.join(rows)} {active} {castling} - {max(0, int(halfmove_clock))} {max(1, int(fullmove_number))}"


class OllamaCommentaryService:
    def __init__(self):
        self.enabled = os.getenv("OLLAMA_ENABLED", "1").strip().lower() not in {"0", "false", "no", "off"}
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
        self.endpoint = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
        self.timeout_seconds = max(5.0, float(os.getenv("OLLAMA_TIMEOUT_SEC", "45")))
        self._queue = queue.Queue(maxsize=32)
        self._comments = []
        self._next_id = 1
        self._lock = Lock()
        self._last_warning_at = 0.0
        self._was_unavailable = False

        self._worker = threading.Thread(target=self._run_worker, daemon=True)
        self._worker.start()

    def enqueue(self, payload):
        if not self.enabled:
            return
        try:
            self._queue.put_nowait(payload)
        except queue.Full:
            return

    def recent(self, limit: int = 20):
        with self._lock:
            return list(self._comments[-limit:])

    def _append_comment(self, text: str):
        with self._lock:
            self._comments.append({
                "id": self._next_id,
                "text": text.strip(),
                "timestamp": time.time(),
            })
            self._next_id += 1
            if len(self._comments) > 120:
                self._comments = self._comments[-120:]

    def _run_worker(self):
        while True:
            payload = self._queue.get()
            try:
                text = self._generate_commentary(payload)
                if text:
                    if self._was_unavailable:
                        self._append_comment("Ollama commentary connected.")
                        self._was_unavailable = False
                    self._append_comment(text)
            except Exception as error:
                self._warn_unavailable(f"Ollama commentary worker error: {error}")
                continue

    def _warn_unavailable(self, reason: str):
        now = time.time()
        if now - self._last_warning_at < 15:
            return
        self._last_warning_at = now
        self._was_unavailable = True
        self._append_comment(reason)

    def _generate_commentary(self, payload):
        prompt = (
            "You are a concise chess commentator.\n"
            "Describe the last move and current position in 1-2 short sentences.\n"
            "Mention tactical threats, checks, or strategic ideas if relevant.\n"
            f"Last move: {payload.get('move', 'unknown')}\n"
            f"Side to move: {payload.get('turn', 'unknown')}\n"
            f"In check: {payload.get('inCheck', False)}\n"
            f"FEN: {payload.get('fen', '')}\n"
        )
        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.4,
                "num_predict": 80,
            },
        }

        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                parsed = json.loads(raw)
                return parsed.get("response", "").strip()
        except urllib.error.HTTPError as error:
            detail = ""
            try:
                detail = error.read().decode("utf-8").strip()
            except Exception:
                detail = ""
            suffix = f" HTTP {error.code}" + (f": {detail}" if detail else "")
            self._warn_unavailable(
                f"Ollama commentary unavailable ({self.endpoint}).{suffix}"
            )
            return ""
        except urllib.error.URLError as error:
            self._warn_unavailable(
                f"Ollama commentary unavailable ({self.endpoint}): {error.reason}"
            )
            return ""
        except TimeoutError:
            self._warn_unavailable(
                f"Ollama commentary timed out after {int(self.timeout_seconds)}s. "
                "Increase OLLAMA_TIMEOUT_SEC or use a smaller model."
            )
            return ""
        except (ValueError, json.JSONDecodeError) as error:
            self._warn_unavailable(f"Ollama commentary parse error: {error}")
            return ""


OLLAMA_COMMENTARY = OllamaCommentaryService()


OPENING_NAME_LINES = [
    ("King's Pawn Game", ["e2e4", "e7e5"]),
    ("Sicilian Defense", ["e2e4", "c7c5"]),
    ("French Defense", ["e2e4", "e7e6"]),
    ("Caro-Kann Defense", ["e2e4", "c7c6"]),
    ("Queen's Gambit", ["d2d4", "d7d5", "c2c4"]),
    ("King's Indian Defense", ["d2d4", "g8f6", "c2c4", "g7g6"]),
    ("English Opening", ["c2c4"]),
    ("Ruy Lopez setup", ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"]),
]


def _player_side_name(player: int) -> str:
    return "white" if player == 1 else "black"


def _square_from_xy(game: Chess, x: int, y: int) -> str:
    return f"{game.x_notation[x]}{game.y_notation[y]}"


def _piece_label(piece: int) -> str:
    color = "White" if piece > 0 else "Black"
    names = {
        1: "pawn",
        2: "knight",
        3: "bishop",
        4: "rook",
        5: "queen",
        6: "king",
    }
    return f"{color} {names.get(abs(piece), 'piece')}"


def _detect_opening(last_moves):
    sequence = []
    for move in last_moves:
        from_square = str(move.get("from", "")).lower()
        to_square = str(move.get("to", "")).lower()
        if len(from_square) == 2 and len(to_square) == 2:
            sequence.append(f"{from_square}{to_square}")

    best_name = "Unclassified opening"
    best_length = 0
    for name, line in OPENING_NAME_LINES:
        prefix_len = min(len(sequence), len(line))
        if prefix_len == 0:
            continue
        if sequence[:prefix_len] == line[:prefix_len] and prefix_len > best_length:
            best_name = name
            best_length = prefix_len
    return best_name


def _attacked_squares(game: Chess, attacker: int):
    attacked = set()
    for y, rank in enumerate(game.board):
        for x, piece in enumerate(rank):
            if piece == 0 or (piece * attacker) <= 0:
                continue
            piece_name = game.chess_pieces_name[abs(piece)]
            moves = getattr(Chess, piece_name).movement(game, attacker, (x, y))
            for move_x, move_y in moves:
                attacked.add((move_x, move_y))
    return attacked


def _collect_captures(game: Chess, player: int):
    moves_dict = game.get_all_moves_dict(for_player=player)
    captures = []
    for from_square, move_data in moves_dict.items():
        for move_x, move_y in move_data[1]:
            target_piece = game.board[move_y][move_x]
            if target_piece == 0:
                continue
            if (target_piece * player) < 0:
                captures.append(f"{from_square}x{to_notation(game, move_x, move_y)}")
    return captures


def _collect_checking_moves(game: Chess, player: int):
    moves_dict = game.get_all_moves_dict(for_player=player)
    checks = []
    for from_square, move_data in moves_dict.items():
        for move_x, move_y in move_data[1]:
            preview = deepcopy(game)
            preview.current_player = player
            to_square = to_notation(game, move_x, move_y)
            preview.move_piece(from_square, to_square)
            preview.promotable_pawns()
            if preview.is_check()[1]:
                checks.append(f"{from_square}->{to_square}")
    return checks


def _find_king_xy(game: Chess, player: int):
    king_piece = 6 * player
    for y, rank in enumerate(game.board):
        for x, piece in enumerate(rank):
            if piece == king_piece:
                return x, y
    return None


def _detect_pins(game: Chess, player: int):
    king_xy = _find_king_xy(game, player)
    if king_xy is None:
        return []
    king_x, king_y = king_xy
    pinned = []
    directions = [
        (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1),
    ]
    for dx, dy in directions:
        x = king_x + dx
        y = king_y + dy
        candidate = None
        while 0 <= x <= 7 and 0 <= y <= 7:
            piece = game.board[y][x]
            if piece == 0:
                x += dx
                y += dy
                continue
            if (piece * player) > 0:
                if candidate is None and abs(piece) != 6:
                    candidate = (x, y, piece)
                    x += dx
                    y += dy
                    continue
                break

            if candidate is None:
                break

            abs_piece = abs(piece)
            straight = dx == 0 or dy == 0
            diagonal = dx != 0 and dy != 0
            if (straight and abs_piece in (4, 5)) or (diagonal and abs_piece in (3, 5)):
                pinned_square = _square_from_xy(game, candidate[0], candidate[1])
                attacker_square = _square_from_xy(game, x, y)
                pinned.append(
                    f"{_piece_label(candidate[2])} on {pinned_square} pinned by {_piece_label(piece)} on {attacker_square}"
                )
            break
    return pinned


def _position_tool_snapshot(game: Chess, last_moves):
    opening_name = _detect_opening(last_moves)
    white_opening_moves = []
    black_opening_moves = []
    for item in last_moves[:8]:
        side = str(item.get("player", "")).lower()
        move_text = f"{item.get('from', '')}->{item.get('to', '')}"
        if side.startswith("white"):
            white_opening_moves.append(move_text)
        elif side.startswith("black"):
            black_opening_moves.append(move_text)
    current_player = game.current_player
    side_to_move = _player_side_name(current_player)
    in_check_info = current_check_info(game)

    captures_for_current = _collect_captures(game, current_player)[:12]
    checks_for_current = _collect_checking_moves(game, current_player)[:10]
    pins_on_current = _detect_pins(game, current_player)[:8]
    pins_on_other = _detect_pins(game, -current_player)[:8]

    attacked_by_opponent = _attacked_squares(game, -current_player)
    pressured = []
    for y, rank in enumerate(game.board):
        for x, piece in enumerate(rank):
            if piece == 0 or (piece * current_player) <= 0:
                continue
            if (x, y) in attacked_by_opponent:
                pressured.append(f"{_piece_label(piece)} on {_square_from_xy(game, x, y)}")

    return {
        "opening": opening_name,
        "whiteOpeningMoves": white_opening_moves[:4],
        "blackOpeningMoves": black_opening_moves[:4],
        "sideToMove": side_to_move,
        "inCheck": in_check_info["inCheck"],
        "checkedKingSquare": in_check_info["checkedKingSquare"],
        "candidateCaptures": captures_for_current,
        "candidateChecks": checks_for_current,
        "pinsOnSideToMove": pins_on_current,
        "pinsOnOpponent": pins_on_other,
        "piecesUnderPressure": pressured[:12],
    }


class StrandsCoachAgent:
    def __init__(self):
        self.enabled = os.getenv("COACH_ENABLED", "1").strip().lower() not in {"0", "false", "no", "off"}
        self.model = os.getenv("COACH_MODEL", os.getenv("OLLAMA_MODEL", "llama3.2:latest"))
        self.endpoint = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
        self.timeout_seconds = max(5.0, float(os.getenv("COACH_TIMEOUT_SEC", os.getenv("OLLAMA_TIMEOUT_SEC", "45"))))
        self._messages = []
        self._next_id = 1
        self._append(
            "assistant",
            "Strands coach ready. Ask about the opening, tactical checks/captures/pins, or plans for the current position.",
        )

    def reset(self):
        self._messages = []
        self._next_id = 1
        self._append(
            "assistant",
            "New game loaded. Ask me to break down the opening or evaluate tactical ideas in the current position.",
        )

    def _append(self, role: str, text: str):
        self._messages.append({
            "id": self._next_id,
            "role": role,
            "text": text.strip(),
            "timestamp": time.time(),
        })
        self._next_id += 1
        if len(self._messages) > 80:
            self._messages = self._messages[-80:]

    def recent(self, limit: int = 24):
        return list(self._messages[-limit:])

    def _fallback_reply(self, tool_snapshot, user_message, error_text=""):
        checks = ", ".join(tool_snapshot["candidateChecks"][:4]) or "none right now"
        captures = ", ".join(tool_snapshot["candidateCaptures"][:4]) or "none right now"
        pins = ", ".join(tool_snapshot["pinsOnSideToMove"][:2]) or "no obvious absolute pins"
        pressure = ", ".join(tool_snapshot["piecesUnderPressure"][:4]) or "no immediate pressure flags"
        white_opening = ", ".join(tool_snapshot.get("whiteOpeningMoves", [])) or "not established yet"
        black_opening = ", ".join(tool_snapshot.get("blackOpeningMoves", [])) or "not established yet"
        prefix = ""
        if error_text:
            prefix = f"(Local coach model unavailable: {error_text}) "
        return (
            f"{prefix}Opening: {tool_snapshot['opening']}. "
            f"White setup: {white_opening}. Black setup: {black_opening}. "
            f"Side to move: {tool_snapshot['sideToMove']}. "
            f"Checks: {checks}. Captures: {captures}. Pins on mover: {pins}. "
            f"Pieces under pressure: {pressure}. "
            f"Given your question ({user_message}), prefer forcing moves first (checks/captures), "
            "then pick a move that improves king safety and piece activity."
        )

    def ask(self, user_message: str, game: Chess, last_moves):
        cleaned = user_message.strip()
        if not cleaned:
            raise ValueError("Coach message must not be empty.")
        self._append("user", cleaned)

        tool_snapshot = _position_tool_snapshot(game, last_moves)
        if not self.enabled:
            reply = self._fallback_reply(tool_snapshot, cleaned, "COACH_ENABLED=0")
            self._append("assistant", reply)
            return reply

        conversation_tail = self.recent(8)
        chat_lines = []
        for item in conversation_tail:
            role = "User" if item["role"] == "user" else "Coach"
            chat_lines.append(f"{role}: {item['text']}")

        prompt = (
            "You are Strands chess coach, a concise tactical guide.\n"
            "Use the provided TOOL_SNAPSHOT as truth for checks/captures/pins/opening.\n"
            "Respond in plain English with:\n"
            "1) current opening/context,\n"
            "2) top tactical ideas,\n"
            "3) one practical candidate move with rationale.\n\n"
            f"TOOL_SNAPSHOT:\n{json.dumps(tool_snapshot, indent=2)}\n\n"
            "RECENT_CHAT:\n"
            + "\n".join(chat_lines)
            + "\n"
        )

        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.25,
                "num_predict": 220,
            },
        }
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                parsed = json.loads(raw)
                reply = str(parsed.get("response", "")).strip()
                if not reply:
                    reply = self._fallback_reply(tool_snapshot, cleaned, "empty model response")
        except urllib.error.HTTPError as error:
            detail = ""
            try:
                detail = error.read().decode("utf-8").strip()
            except Exception:
                detail = ""
            suffix = f"HTTP {error.code}" + (f": {detail}" if detail else "")
            reply = self._fallback_reply(tool_snapshot, cleaned, suffix)
        except urllib.error.URLError as error:
            reply = self._fallback_reply(tool_snapshot, cleaned, str(error.reason))
        except TimeoutError:
            reply = self._fallback_reply(tool_snapshot, cleaned, f"timeout after {int(self.timeout_seconds)}s")
        except (ValueError, json.JSONDecodeError) as error:
            reply = self._fallback_reply(tool_snapshot, cleaned, f"parse error: {error}")

        self._append("assistant", reply)
        return reply


def king_square_for_player(game: Chess, player: int):
    king_piece = 6 * player
    for y, rank in enumerate(game.board):
        for x, piece in enumerate(rank):
            if piece == king_piece:
                return to_notation(game, x, y)
    return None


def current_check_info(game: Chess):
    _, in_check = game.is_check()
    if not in_check:
        return {"inCheck": False, "checkedSide": None, "checkedKingSquare": None}

    checked_side = "white" if game.current_player == 1 else "black"
    checked_square = king_square_for_player(game, game.current_player)
    return {"inCheck": True, "checkedSide": checked_side, "checkedKingSquare": checked_square}


def evaluate_game_state(game: Chess, halfmove_clock: int = 0, repetition_count: int = 1):
    if game.is_check()[1] and game.is_checkmate():
        winner = "White" if game.current_player == -1 else "Black"
        winner_side = "white" if game.current_player == -1 else "black"
        loser_side = "black" if winner_side == "white" else "white"
        user_message = "You win." if winner_side == "white" else "You lose."
        return True, f"Checkmate. {winner} wins. {user_message}", "checkmate", winner_side, loser_side
    if repetition_count >= 3:
        return True, "Draw by threefold repetition.", "threefold_repetition", None, None
    if halfmove_clock >= 100:
        return True, "Draw by 50-move rule.", "fifty_move_rule", None, None
    if game.is_stalemate():
        return True, "Draw by stalemate.", "stalemate", None, None
    if game.is_king_bishop_draw():
        return True, "Draw by insufficient material.", "insufficient_material", None, None
    return False, "", "", None, None


class GameSession:
    def __init__(self):
        self.lock = Lock()
        self.game = Chess()
        self.random_agent = random_ai.random_ai()
        self.commentary = OLLAMA_COMMENTARY
        self.coach = StrandsCoachAgent()
        self.last_moves = []
        self.game_over = False
        self.result = ""
        self.end_reason = ""
        self.winner_side = None
        self.loser_side = None
        self.ai_mode = "mcts_fast"
        self.ai_config = {
            "mctsDepth": 10,
            "mctsIterations": 1200,
            "mctsThinkTimeMs": 2200,
            "mctsBranching": 22,
            "mctsRolloutDepth": 14,
        }
        self.position_history = [position_key(self.game)]
        self.position_history_counts = {position_key(self.game): 1}
        self.halfmove_clock = 0
        self.last_engine_stats = {
            "aiMode": self.ai_mode,
            "nodes": 0,
            "depthReached": 0,
            "evalCp": 0,
            "searchMs": 0,
            "nps": 0,
            "bookMove": False,
        }

    def reset(self):
        self.game = Chess()
        self.last_moves = []
        self.game_over = False
        self.result = ""
        self.end_reason = ""
        self.winner_side = None
        self.loser_side = None
        self.position_history = [position_key(self.game)]
        self.position_history_counts = {position_key(self.game): 1}
        self.halfmove_clock = 0
        self.coach.reset()
        self.last_engine_stats = {
            "aiMode": self.ai_mode,
            "nodes": 0,
            "depthReached": 0,
            "evalCp": 0,
            "searchMs": 0,
            "nps": 0,
            "bookMove": False,
        }

    def _record_position(self):
        key = position_key(self.game)
        self.position_history.append(key)
        self.position_history_counts[key] = self.position_history_counts.get(key, 0) + 1
        if len(self.position_history) > 160:
            removed = self.position_history.pop(0)
            remaining = self.position_history_counts.get(removed, 1) - 1
            if remaining <= 0:
                self.position_history_counts.pop(removed, None)
            else:
                self.position_history_counts[removed] = remaining

    def _current_repetition_count(self):
        key = position_key(self.game)
        return self.position_history_counts.get(key, 0)

    def _move_characteristics(self, from_square: str, to_square: str):
        from_xy = to_xy(self.game, from_square)
        to_xy_pos = to_xy(self.game, to_square)
        if from_xy is None or to_xy_pos is None:
            return False, False
        moving = self.game.board[from_xy[1]][from_xy[0]]
        target = self.game.board[to_xy_pos[1]][to_xy_pos[0]]
        is_capture = target != 0
        is_pawn_move = abs(moving) == 1
        return is_capture, is_pawn_move

    def _enqueue_commentary(self, move_text: str):
        fullmove_number = max(1, len(self.last_moves) // 2 + 1)
        check_info = current_check_info(self.game)
        self.commentary.enqueue({
            "move": move_text,
            "turn": "white" if self.game.current_player == 1 else "black",
            "inCheck": check_info["inCheck"],
            "fen": board_to_fen(self.game, self.halfmove_clock, fullmove_number),
        })

    def set_ai_mode(self, ai_mode: str):
        if ai_mode not in {"random", "mcts_fast", "mcts_strong", "mcts_ultra"}:
            raise ValueError("Unsupported AI mode.")
        self.ai_mode = ai_mode

    def update_ai_config(self, updates):
        validators = {
            "mctsDepth": (4, 30),
            "mctsIterations": (50, 20000),
            "mctsThinkTimeMs": (100, 60000),
            "mctsBranching": (8, 60),
            "mctsRolloutDepth": (6, 48),
        }
        for key, bounds in validators.items():
            if key not in updates:
                continue
            value = updates[key]
            if not isinstance(value, int):
                raise ValueError(f"{key} must be an integer.")
            minimum, maximum = bounds
            if value < minimum or value > maximum:
                raise ValueError(f"{key} must be between {minimum} and {maximum}.")
            self.ai_config[key] = value

    def state_payload(self, message: str = ""):
        current_turn = "white" if self.game.current_player == 1 else "black"
        legal_moves_payload = {}
        if not self.game_over and self.game.current_player == 1:
            legal_moves_payload = legal_moves_for_current_player(self.game)
        check_info = current_check_info(self.game)
        return {
            "board": board_to_payload(self.game),
            "turn": current_turn,
            "isEngineTurn": (not self.game_over and self.game.current_player == -1),
            "legalMoves": legal_moves_payload,
            "inCheck": check_info["inCheck"],
            "checkedSide": check_info["checkedSide"],
            "checkedKingSquare": check_info["checkedKingSquare"],
            "gameOver": self.game_over,
            "result": self.result,
            "endReason": self.end_reason,
            "winnerSide": self.winner_side,
            "loserSide": self.loser_side,
            "message": message,
            "lastMoves": self.last_moves,
            "aiMode": self.ai_mode,
            "availableAis": ["random", "mcts_fast", "mcts_strong", "mcts_ultra"],
            "aiConfig": self.ai_config,
            "aiConfigRanges": {
                "mctsDepth": [4, 30],
                "mctsIterations": [50, 20000],
                "mctsThinkTimeMs": [100, 60000],
                "mctsBranching": [8, 60],
                "mctsRolloutDepth": [6, 48],
            },
            "commentary": self.commentary.recent(14),
            "ollamaEnabled": self.commentary.enabled,
            "ollamaModel": self.commentary.model,
            "coach": {
                "messages": self.coach.recent(24),
                "enabled": self.coach.enabled,
                "model": self.coach.model,
            },
            "engineStats": self.last_engine_stats,
        }

    def ask_coach(self, message: str):
        reply = self.coach.ask(message, self.game, self.last_moves)
        return {
            "reply": reply,
            "messages": self.coach.recent(24),
            "enabled": self.coach.enabled,
            "model": self.coach.model,
        }

    def apply_human_move(self, from_square: str, to_square: str):
        if self.game_over:
            return False, "Game is already over."
        if self.game.current_player != 1:
            return False, "Please wait for the bot move."

        legal_moves = legal_moves_for_current_player(self.game)
        if from_square not in legal_moves or to_square not in legal_moves[from_square]:
            return False, "Illegal move."

        is_capture, is_pawn_move = self._move_characteristics(from_square, to_square)
        self.game.move_piece(from_square, to_square)
        self.game.promotable_pawns()
        self.last_moves.append({"player": "white", "from": from_square, "to": to_square})
        self.halfmove_clock = 0 if (is_capture or is_pawn_move) else self.halfmove_clock + 1
        self._record_position()
        self._enqueue_commentary(f"White: {from_square} to {to_square}")

        self.game_over, self.result, self.end_reason, self.winner_side, self.loser_side = evaluate_game_state(
            self.game,
            self.halfmove_clock,
            self._current_repetition_count(),
        )
        if self.game_over:
            return True, self.result

        check_info = current_check_info(self.game)
        if check_info["inCheck"] and check_info["checkedSide"] == "black":
            return True, "Move played. Black king is in check."

        return True, "Move played."

    def apply_bot_move(self):
        if self.game_over:
            return False, "Game is already over."
        if self.game.current_player != -1:
            return False, "It is not the engine's turn."

        legal_moves = legal_moves_for_current_player(self.game)
        if not legal_moves:
            self.game_over, self.result, self.end_reason, self.winner_side, self.loser_side = evaluate_game_state(
                self.game,
                self.halfmove_clock,
                self._current_repetition_count(),
            )
            message = self.result if self.result else "No legal engine move."
            return True, message

        if self.ai_mode == "random":
            from_square = random.choice(list(legal_moves.keys()))
            to_square = random.choice(legal_moves[from_square])
            self.last_engine_stats = {
                "aiMode": self.ai_mode,
                "nodes": 0,
                "depthReached": 0,
                "evalCp": 0,
                "searchMs": 0,
                "nps": 0,
                "bookMove": False,
            }
        else:
            search_started = time.perf_counter()
            depth = self.ai_config["mctsDepth"]
            iterations = self.ai_config["mctsIterations"]
            think_time_seconds = self.ai_config["mctsThinkTimeMs"] / 1000.0
            max_branching = self.ai_config["mctsBranching"]
            rollout_depth = self.ai_config["mctsRolloutDepth"]
            if self.ai_mode == "mcts_strong":
                depth = max(depth, 14)
                iterations = int(iterations * 2.5)
                think_time_seconds = think_time_seconds * 3.0
                max_branching = max(10, min(max_branching, 16))
                rollout_depth = max(rollout_depth, 18)
            elif self.ai_mode == "mcts_ultra":
                depth = max(depth, 18)
                iterations = int(iterations * 5.0)
                think_time_seconds = think_time_seconds * 6.0
                max_branching = max(10, min(max_branching, 14))
                rollout_depth = max(rollout_depth, 22)
            recent_positions = self.position_history[-24:]
            avoid_position_counts = {}
            for key in recent_positions:
                avoid_position_counts[key] = avoid_position_counts.get(key, 0) + 1
            avoid_position_counts = {key: count for key, count in avoid_position_counts.items() if count >= 2}
            bot = mcts_ai.MCTS_ai(
                game=self.game,
                max_depth=depth,
                rollout_depth=rollout_depth,
                max_branching=max_branching,
                avoid_position_counts=avoid_position_counts,
                position_history_counts=dict(self.position_history_counts),
                root_halfmove_clock=self.halfmove_clock,
            )
            _, move_string = bot.play(
                iterations=iterations,
                time_limit_seconds=think_time_seconds,
                min_depth=depth,
            )
            elapsed_ms = max(1, int((time.perf_counter() - search_started) * 1000))
            nodes = int(bot.nodes_searched)
            self.last_engine_stats = {
                "aiMode": self.ai_mode,
                "nodes": nodes,
                "depthReached": int(bot.last_completed_depth or bot.max_depth_reached),
                "evalCp": int(bot.last_root_score),
                "searchMs": elapsed_ms,
                "nps": int((nodes * 1000) / elapsed_ms),
                "bookMove": bool(bot.used_opening_book),
            }
            if not move_string:
                from_square = random.choice(list(legal_moves.keys()))
                to_square = random.choice(legal_moves[from_square])
            else:
                from_square, _, to_square = move_string.split()
                if from_square not in legal_moves or to_square not in legal_moves[from_square]:
                    from_square = random.choice(list(legal_moves.keys()))
                    to_square = random.choice(legal_moves[from_square])
                else:
                    preview = deepcopy(self.game)
                    preview.move_piece(from_square, to_square)
                    preview.promotable_pawns()
                    candidate_key = position_key(preview)
                    if avoid_position_counts.get(candidate_key, 0) >= 2:
                        non_repeating = []
                        for src in legal_moves:
                            for dest in legal_moves[src]:
                                alt_preview = deepcopy(self.game)
                                alt_preview.move_piece(src, dest)
                                alt_preview.promotable_pawns()
                                alt_key = position_key(alt_preview)
                                if avoid_position_counts.get(alt_key, 0) < 2:
                                    non_repeating.append((src, dest))
                        if non_repeating:
                            from_square, to_square = random.choice(non_repeating)

        previous_black_move = None
        for prior in reversed(self.last_moves):
            if str(prior.get("player", "")).startswith("black"):
                previous_black_move = prior
                break

        if previous_black_move is not None:
            inverse_from = previous_black_move["to"]
            inverse_to = previous_black_move["from"]
            if from_square == inverse_from and to_square == inverse_to:
                alternatives = []
                for src in legal_moves:
                    for dest in legal_moves[src]:
                        if not (src == inverse_from and dest == inverse_to):
                            alternatives.append((src, dest))
                if alternatives:
                    from_square, to_square = random.choice(alternatives)

        is_capture, is_pawn_move = self._move_characteristics(from_square, to_square)
        self.game.move_piece(from_square, to_square)
        self.game.promotable_pawns()
        self.last_moves.append({"player": f"black ({self.ai_mode})", "from": from_square, "to": to_square})
        self.halfmove_clock = 0 if (is_capture or is_pawn_move) else self.halfmove_clock + 1
        self._record_position()
        self._enqueue_commentary(f"Black: {from_square} to {to_square}")

        self.game_over, self.result, self.end_reason, self.winner_side, self.loser_side = evaluate_game_state(
            self.game,
            self.halfmove_clock,
            self._current_repetition_count(),
        )
        if self.game_over:
            return True, self.result

        check_info = current_check_info(self.game)
        if check_info["inCheck"] and check_info["checkedSide"] == "white":
            return True, "Engine move played. Your king is in check."

        return True, "Engine move played."


SESSION = GameSession()


class ChessFrontendHandler(BaseHTTPRequestHandler):
    server_version = "ChessFrontend/1.0"

    def do_GET(self):
        request_path = urlparse(self.path).path.rstrip("/") or "/"
        if request_path == "/" or request_path == "/index.html":
            self.serve_file(INDEX_PATH)
            return
        if request_path == "/about" or request_path == "/about.html":
            self.serve_file(ABOUT_PATH)
            return

        if request_path == "/api/state":
            with SESSION.lock:
                self.write_json(SESSION.state_payload())
            return

        if request_path == "/api/commentary":
            with SESSION.lock:
                self.write_json({
                    "commentary": SESSION.commentary.recent(20),
                    "ollamaEnabled": SESSION.commentary.enabled,
                    "ollamaModel": SESSION.commentary.model,
                })
            return

        if request_path == "/api/coach":
            with SESSION.lock:
                self.write_json({
                    "coach": {
                        "messages": SESSION.coach.recent(24),
                        "enabled": SESSION.coach.enabled,
                        "model": SESSION.coach.model,
                    }
                })
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self):
        request_path = urlparse(self.path).path.rstrip("/") or "/"
        if request_path == "/api/new-game":
            with SESSION.lock:
                SESSION.reset()
                self.write_json(SESSION.state_payload(message="New game started."))
            return

        if request_path == "/api/move":
            data = self.read_json_body()
            if data is None:
                return

            from_square = data.get("from", "")
            to_square = data.get("to", "")

            with SESSION.lock:
                if to_xy(SESSION.game, from_square) is None or to_xy(SESSION.game, to_square) is None:
                    self.write_json({"error": "Invalid square notation. Use values like e2 and e4."}, status=HTTPStatus.BAD_REQUEST)
                    return

                ok, message = SESSION.apply_human_move(from_square.lower(), to_square.lower())
                if not ok:
                    self.write_json({"error": message, "state": SESSION.state_payload()}, status=HTTPStatus.BAD_REQUEST)
                    return

                self.write_json(SESSION.state_payload(message=message))
            return

        if request_path == "/api/bot-move":
            with SESSION.lock:
                ok, message = SESSION.apply_bot_move()
                if not ok:
                    self.write_json({"error": message, "state": SESSION.state_payload()}, status=HTTPStatus.BAD_REQUEST)
                    return
                self.write_json(SESSION.state_payload(message=message))
            return

        if request_path == "/api/ai":
            data = self.read_json_body()
            if data is None:
                return

            with SESSION.lock:
                try:
                    if "aiMode" in data:
                        SESSION.set_ai_mode(data.get("aiMode", ""))
                    SESSION.update_ai_config(data)
                except ValueError as error:
                    self.write_json({"error": str(error), "state": SESSION.state_payload()}, status=HTTPStatus.BAD_REQUEST)
                    return
                self.write_json(SESSION.state_payload(message="AI settings updated."))
            return

        if request_path == "/api/coach":
            data = self.read_json_body()
            if data is None:
                return
            message = str(data.get("message", "")).strip()
            if not message:
                self.write_json({"error": "Coach message must not be empty."}, status=HTTPStatus.BAD_REQUEST)
                return

            with SESSION.lock:
                try:
                    coach_payload = SESSION.ask_coach(message)
                except ValueError as error:
                    self.write_json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)
                    return
                self.write_json({
                    "coach": coach_payload,
                    "state": SESSION.state_payload(),
                })
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def serve_file(self, file_path: Path):
        if not file_path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return

        content_type, _ = mimetypes.guess_type(str(file_path))
        content_type = content_type or "application/octet-stream"
        data = file_path.read_bytes()

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_json_body(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.write_json({"error": "Invalid Content-Length header."}, status=HTTPStatus.BAD_REQUEST)
            return None

        if content_length <= 0:
            self.write_json({"error": "Request body is required."}, status=HTTPStatus.BAD_REQUEST)
            return None

        raw_body = self.rfile.read(content_length)
        try:
            return json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.write_json({"error": "Body must be valid JSON."}, status=HTTPStatus.BAD_REQUEST)
            return None

    def write_json(self, payload, status=HTTPStatus.OK):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format_str, *args):
        return


def run_server(host: str = "127.0.0.1", port: int = 8000):
    server = HTTPServer((host, port), ChessFrontendHandler)
    print(f"Serving chess frontend at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
