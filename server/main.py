from chess import Chess
import random_ai

# Create a chess game
chess = Chess()

# Instantiate in a random agent
random_agent = random_ai.random_ai()

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
        random_agent.choose_move(chess)

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
        
    
