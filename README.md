# Python Chess Engine

[![Visits Badge](https://badges.pufler.dev/visits/alexander-darwiche/chess-engine)](#)

A chess engine written from scratch in pure Python, including the rules engine, the search, and a browser UI. You play White against a bot. Optionally, a coach powered by a local LLM explains the position as you play.

## Features

- **Rules engine** ([chess.py](chess.py)): legal move generation, check, checkmate, stalemate, castling, promotion, threefold repetition, the 50-move rule and insufficient material.
- **Search engine** ([mcts_ai.py](mcts_ai.py)): iterative-deepening alpha-beta with:
  - a transposition table, quiescence search, null-move pruning, late-move reductions and aspiration windows
  - killer and history move ordering
  - a small opening book
  - optional Syzygy endgame tablebases
- **Evaluation:** material, piece-square tables, development, king safety, pawn structure and mobility.
- **Web UI** ([index.html](index.html), [web_app.py](web_app.py)):
  - drag-and-drop or click-to-move board
  - selectable bot strength and tunable search settings
  - live engine stats (depth, nodes, NPS, eval) and a search-tree visualisation
- **Coach and commentary:** a chat coach that reads the position before answering. It checks the opening, the available checks and captures, pins, and pieces under attack. When [Ollama](https://ollama.com) is running, a local model writes the answers and per-move commentary. Without Ollama, the coach falls back to summarising the position itself.

## Quick start

Requires Python 3.11+ and [Poetry](https://python-poetry.org/docs/). There are no third-party runtime dependencies.

```bash
poetry install
poetry run python web_app.py
```

Open <http://127.0.0.1:8000>. The **How it works** link (`/about.html`) gives an overview of the algorithms.

### Bot modes

| Mode | Description |
| --- | --- |
| Random | Plays a random legal move |
| Fast | Alpha-beta search with your chosen settings |
| Strong | The same search with about 3× the think time and a deeper minimum depth |
| Ultra | About 6× the think time, for deep local analysis |

The **Blitz / Rapid / Deep Think** slider applies preset search settings. **Max strength** switches to Ultra and raises every setting to its maximum.

### Terminal play

```bash
poetry run python main.py        # vs random bot
poetry run python main_mcts.py   # vs search engine
```

Enter moves as squares: type the square of the piece you want to move (for example `e2`), then the square to move it to (for example `e4`).

## Configuration

All optional, set via environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `OLLAMA_URL` | `http://127.0.0.1:11434/api/generate` | Ollama endpoint |
| `OLLAMA_MODEL` | `llama3.2:latest` | Model for move commentary |
| `OLLAMA_ENABLED` | `1` | Set to `0` to disable commentary |
| `COACH_MODEL` | `OLLAMA_MODEL` | Model for the coach chat |
| `COACH_ENABLED` | `1` | Set to `0` to turn off the model (the coach still summarises the position) |
| `COACH_TIMEOUT_SEC` / `OLLAMA_TIMEOUT_SEC` | `45` | LLM request timeout |
| `SYZYGY_PATH` | — | Directory of Syzygy tablebases (requires `python-chess`) |

## Project layout

```
chess.py           Board representation and rules
mcts_ai.py         Search engine (alpha-beta; class kept as MCTS_ai for history)
random_ai.py       Random-move bot
web_app.py         HTTP server, game session, coach and commentary services
index.html         Board UI
about.html         Algorithm overview page
main.py            Terminal game vs random bot
main_mcts.py       Terminal game vs search engine
tests/             Regression tests
```

## Tests

```bash
poetry run python -m unittest tests.test_engine_correctness
```

The tests cover threefold repetition, the 50-move rule, checkmate detection (Fool's Mate) and checking that the engine only returns legal moves.
