from chess import Chess

chess = Chess()

# chess.move_piece('f2','f3')

# chess.display_game()

# chess.move_piece('e7','e5')

# chess.display_game()

# chess.move_piece('a2','a4')

# chess.display_game()

# chess.move_piece('c7','c6')

# chess.display_game()

# chess.move_piece('b2','b3')

# chess.display_game()

# chess.move_piece('c6','b5')

# chess.display_game()

# chess.move_piece('c1','a3')

# chess.display_game()

# chess.move_piece('h7','h6')

# chess.display_game()

# chess.move_piece('b3','b4')

# chess.display_game()

# chess.move_piece('c8','b7')

# chess.display_game()

# chess.move_piece('h2','h3')

# chess.display_game()

# chess.move_piece('b7','g2')

# chess.display_game()

# chess.move_piece('h1','h2')

# chess.display_game()

# chess.move_piece('d8','b6')

# chess.display_game()

# chess.move_piece('h3','h4')

# chess.display_game()

# chess.move_piece('b6','f2')

# chess.display_game()

# chess.move_piece('b1','c3')

# chess.display_game()

# chess.move_piece('b8','c6')

# chess.display_game()

# chess.move_piece('e2','e3')

# chess.display_game()

# chess.move_piece('e8','c8')

# chess.display_game()

# chess.move_piece('b7','b6')
# chess.move_piece('a4','a5')
# chess.move_piece('h7','h6')
# chess.move_piece('a5','b6')
# chess.move_piece('h6','h5')
# chess.move_piece('b6','b7')
# chess.move_piece('h5','h4')

chess.display_game()

import random_ai

random_agent = random_ai.random_ai()

keep_playing = True
while keep_playing:
        
    if chess.is_stalemate():
        keep_playing = False

    if chess.current_player == 1:
        print('White\'s Turn')
        random_agent.choose_move(chess)
        # location_current_piece = input("What piece?")
        # location_move = input("Where to?")
        # chess.move_piece(location_current_piece,location_move)
    else:
        print("Black\'s Turn")
        random_agent.choose_move(chess)

    chess.promotable_pawns()
    chess.display_game()
    
    if (chess.is_check()[1]):
        if chess.is_checkmate():
            keep_playing = False
        else: 
            print('King is in check!')

    if chess.is_king_bishop_draw():
            keep_playing = False
        
    
