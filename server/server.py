from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


import chess

def array_to_fen(board_array):
    fen_parts = []

    for row in board_array:
        fen_row = ''
        empty_count = 0

        for square in row:
            if square == '':
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += square

        if empty_count > 0:
            fen_row += str(empty_count)

        fen_parts.append(fen_row)

    fen = '/'.join(fen_parts)
    return fen

# Example usage:
board_array = [
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
]

fen = array_to_fen(board_array)
print("FEN:", fen)