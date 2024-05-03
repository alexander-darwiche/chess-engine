


import math
import random

class random_ai:

    def __init__(self):
        pass

    def choose_move(self, chess_game):
        all_moves = chess_game.get_all_moves_dict(for_player = chess_game.current_player)
        #import pdb;pdb.set_trace()
        key = random.choice(list(all_moves.keys()))

        value = random.randint(0,len(all_moves[key][1])-1)

        current_position = key
        next_position = chess_game.x_notation[all_moves[key][1][value][0]] + chess_game.y_notation[all_moves[key][1][value][1]] 

        #print(current_position + " to " + next_position)
        chess_game.move_piece(current_position, next_position)

