from chess import Chess

chess = Chess()

chess.move_piece('a2','a4')

chess.display_game()

chess.move_piece('b7','b5')

chess.display_game()

chess.move_piece('a4','b5')

chess.display_game()

chess.move_piece('c7','c6')

chess.display_game()

chess.move_piece('b2','b3')

chess.display_game()

chess.move_piece('c6','b5')

chess.display_game()

chess.move_piece('c1','a3')

chess.display_game()

chess.move_piece('h7','h6')

chess.display_game()

chess.move_piece('b3','b4')

chess.display_game()

chess.move_piece('c8','b7')

chess.display_game()

chess.move_piece('h2','h3')

chess.display_game()

chess.move_piece('b7','g2')

chess.display_game()

chess.move_piece('h1','h2')

chess.display_game()

chess.move_piece('d8','b6')

chess.display_game()

chess.move_piece('h3','h4')

chess.display_game()

chess.move_piece('b6','f2')

chess.display_game()

chess.move_piece('b1','c3')

chess.display_game()

chess.move_piece('b8','c6')

chess.display_game()

chess.move_piece('e2','e3')

chess.display_game()

chess.move_piece('e8','c8')

chess.display_game()

chess.move_piece('d2','d4')
chess.move_piece('d7','d6')
chess.move_piece('d1','d2')
chess.move_piece('d6','d5')
chess.move_piece('a1','a2')
chess.move_piece('a7','a6')
chess.move_piece('a2','a1')
chess.move_piece('a6','a5')
chess.display_game()


while True:
    if chess.current_player == 1:
        print('White\'s Turn')
    else:
        print("Black\'s Turn")
    userInput = input("What piece?")
    userInput2 = input("Where to?")
    chess.move_piece(userInput,userInput2)
    chess.display_game()

