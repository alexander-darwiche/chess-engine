from chess import Chess
import random_ai
import mcts_ai

# Create a chess game
chess = Chess()


# Set a parameter to True for keep playing, continue until draw or checkmate.
keep_playing = True
chess.display_game()
while keep_playing:

    # Check if the game is a stalemate    
    if chess.is_stalemate():
        keep_playing = False
        break
    
    if chess.current_player == 1:
        print('White\'s Turn')
        #random_agent.choose_move(chess)
        location_current_piece = input("What piece?")
        location_move = input("Where to?")
        chess.move_piece(location_current_piece,location_move)
    else:
        print("Black\'s Turn")

        # Instantiate in a random agent
        mcts_agent = mcts_ai.MCTS_ai(game = chess)
        child,move = mcts_agent.play(5)
        location_current_piece = move.split()[0]
        location_move = move.split()[2]
        print(move)
        chess.move_piece(location_current_piece,location_move)

    chess.promotable_pawns()
    chess.display_game()
    
    if (chess.is_check()[1]):
        if chess.is_checkmate():
            keep_playing = False
            print('Checkmate!')
            break
        else: 
            print('King is in check!')

    if chess.is_king_bishop_draw():
            keep_playing = False
            print('A Draw!')
            break
        
    