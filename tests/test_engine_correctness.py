import random
import unittest

from chess import Chess
from mcts_ai import MCTS_ai
from web_app import evaluate_game_state, position_key


def apply_move(game: Chess, src: str, dst: str):
    game.move_piece(src, dst)
    game.promotable_pawns()


class EngineCorrectnessTests(unittest.TestCase):
    def test_threefold_repetition_draw(self):
        game = Chess()
        counts = {position_key(game): 1}
        sequence = [
            ("g1", "f3"),
            ("g8", "f6"),
            ("f3", "g1"),
            ("f6", "g8"),
            ("g1", "f3"),
            ("g8", "f6"),
            ("f3", "g1"),
            ("f6", "g8"),
        ]
        for src, dst in sequence:
            apply_move(game, src, dst)
            key = position_key(game)
            counts[key] = counts.get(key, 0) + 1

        repetition_count = counts[position_key(game)]
        is_over, _, reason, _, _ = evaluate_game_state(
            game,
            halfmove_clock=len(sequence),
            repetition_count=repetition_count,
        )
        self.assertTrue(is_over)
        self.assertEqual(reason, "threefold_repetition")

    def test_fifty_move_rule_draw(self):
        game = Chess()
        is_over, _, reason, _, _ = evaluate_game_state(
            game,
            halfmove_clock=100,
            repetition_count=1,
        )
        self.assertTrue(is_over)
        self.assertEqual(reason, "fifty_move_rule")

    def test_fools_mate_checkmate(self):
        game = Chess()
        apply_move(game, "f2", "f3")
        apply_move(game, "e7", "e5")
        apply_move(game, "g2", "g4")
        apply_move(game, "d8", "h4")

        is_over, result, reason, winner_side, loser_side = evaluate_game_state(
            game,
            halfmove_clock=0,
            repetition_count=1,
        )
        self.assertTrue(is_over)
        self.assertEqual(reason, "checkmate")
        self.assertEqual(winner_side, "black")
        self.assertEqual(loser_side, "white")
        self.assertIn("Checkmate", result)

    def test_mcts_returns_legal_move(self):
        game = Chess()
        legal = game.get_all_moves_dict(for_player=game.current_player)
        random.seed(0)
        bot = MCTS_ai(
            game=game,
            max_depth=6,
            rollout_depth=8,
            max_branching=12,
            root_halfmove_clock=0,
        )
        _, move_string = bot.play(
            iterations=120,
            time_limit_seconds=0.25,
            min_depth=4,
        )
        self.assertTrue(move_string)
        src, _, dst = move_string.split()
        self.assertIn(src, legal)
        legal_targets = {
            f"{game.x_notation[x]}{game.y_notation[y]}"
            for x, y in legal[src][1]
        }
        self.assertIn(dst, legal_targets)


if __name__ == "__main__":
    unittest.main()
