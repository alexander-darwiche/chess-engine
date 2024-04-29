# Chess Class 
# This includes the rules and moves generation for a chess game.

import math
from copy import deepcopy


class Chess():
    

    # Initalize Chess Game 
    def __init__(self):
        '''
            This is the initialization of the Chess Game. Will hold all base assumptions for a chess match.
        '''
        self.x_notation = ['a','b','c','d','e','f','g','h'] # the chess board is 8x8, this is the x-axis Notation/Coordinate
        self.y_notation = ['8','7','6','5','4','3','2','1'] # the chess board is 8x8, this is the x-axis Notation/Coordinate
        self.castling = [1,1,1,1] # These will be changed to 1 if the rooks or the king change position. This indicates the allowability of castling.
        self.checked = [False, False]
        self.check_escapes = {1: [], -1: []}
 
        self.chess_pieces = {
            'p': 1, 
            'n': 2, 
            'b': 3,
            'r': 4,
            'q': 5,
            'k': 6 
            }
        self.chess_pieces_name = {
            1: 'Pawn',
            2: 'Knight',
            3: 'Bishop',
            4: 'Rook',
            5: 'Queen',
            6: 'King'
            }
        
        self.current_player = 1 # This alternates back and forth, White is first to play (1) and then Black is -1
        self.set_inital_position()
        self.display_game()
        self.get_all_moves()

    
    def set_inital_position(self):
        '''
            This method creates a board with pieces on either side.
        '''
        self.board = [[0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0]] # Empty 2D Array representing a Board with no pieces
        
        current_rank = 0
        for rank in self.board:
            if current_rank in [0,7]:
                rank[0] = 4 # Rook
                rank[1] = 2 # Knight
                rank[2] = 3 # Bishop
                rank[3] = 5 # Queen
                rank[4] = 6 # King 
                rank[5] = 3 # Bishop
                rank[6] = 2 # Knight
                rank[7] = 4 # Rook
            elif current_rank in [1,6]:
                rank = 8*[1]
            
            if current_rank in [0,1]:
                rank = [-1*x for x in rank]

            self.board[current_rank] = rank
            
            current_rank += 1

    
    def display_game(self):
        

        print("+----------------------------+")
        print("| Current State of the Game: |")
        print("+----------------------------+\n\n")
        print("Black Side")
        print("+-----------------+")
        for rank in self.board:
            full_rank = ""
            for file in rank:
                if file > 0:
                    full_rank = full_rank + " " + str(list(self.chess_pieces.keys())[list(self.chess_pieces.values()).index(file)]).upper()
                elif file < 0:
                    full_rank = full_rank + " " + str(list(self.chess_pieces.keys())[list(self.chess_pieces.values()).index(-1*file)]).lower()
                else:
                    full_rank = full_rank + " -"

            print("|" + full_rank + " |" )
        print("+-----------------+")
        print("White Side")

    
    def move_piece(self,current_position_notation, next_position_notation):
        
        # Read in notation
        current_position_x = list(current_position_notation)[0].lower()
        current_position_y = list(current_position_notation)[1]

        # Read in notation
        next_position_x = list(next_position_notation)[0].lower()
        next_position_y = list(next_position_notation)[1]
        

        if (current_position_x not in self.x_notation) or (current_position_y not in self.y_notation) or (next_position_x not in self.x_notation) or (next_position_y not in self.y_notation):
            print('Invalid Move')
        else:
            current_position_x = self.x_notation.index(current_position_x)
            current_position_y = self.y_notation.index(current_position_y)
            current_position = [current_position_x,current_position_y]

            next_position_x = self.x_notation.index(next_position_x)
            next_position_y = self.y_notation.index(next_position_y)
            next_position = [next_position_x,next_position_y]

            # First check if this is a valid move
            valid_move = self.check_valid_move(current_position,next_position)
            
            if (valid_move):
                
                # Castle Queen Side as Black
                if current_position == [4,0] and next_position == [2,0]:
                    if self.castling[0] == 1:
                        rook_current_position_x = 0
                        rook_current_position_y = 0
                        rook_next_position_x = 3
                        rook_next_position_y = 0
                        
                        self.board[next_position_y][next_position_x] = self.board[current_position_y][current_position_x]
                        self.board[current_position_y][current_position_x] = 0
                        self.board[rook_next_position_y][rook_next_position_x] = self.board[rook_current_position_y][rook_current_position_x]
                        self.board[rook_current_position_y][rook_current_position_x] = 0
        
                        self.current_player = self.current_player * -1 
                        print('This is a vaild Move!\n\n\n\n')
                    else:
                        print("Invalid Move!\n\n\n\n")
                # Castle King Side as Black
                elif current_position == [4,0] and next_position == [6,0]:
                    if self.castling[1] == 1:
                        rook_current_position_x = 7
                        rook_current_position_y = 0
                        rook_next_position_x = 5
                        rook_next_position_y = 0
                        
                        self.board[next_position_y][next_position_x] = self.board[current_position_y][current_position_x]
                        self.board[current_position_y][current_position_x] = 0
                        self.board[rook_next_position_y][rook_next_position_x] = self.board[rook_current_position_y][rook_current_position_x]
                        self.board[rook_current_position_y][rook_current_position_x] = 0
                
                        self.current_player = self.current_player * -1 
                    else:
                        print("Invalid Move!\n\n\n\n")
                # Castle Queen Side as Black
                elif current_position == [4,7] and next_position == [2,7]:
                    if self.castling[2] == 1:
                        rook_current_position_x = 0
                        rook_current_position_y = 7
                        rook_next_position_x = 3
                        rook_next_position_y = 7
                        
                        self.board[next_position_y][next_position_x] = self.board[current_position_y][current_position_x]
                        self.board[current_position_y][current_position_x] = 0
                        self.board[rook_next_position_y][rook_next_position_x] = self.board[rook_current_position_y][rook_current_position_x]
                        self.board[rook_current_position_y][rook_current_position_x] = 0
        
                        self.current_player = self.current_player * -1 
                        print('This is a vaild Move!\n\n\n\n')
                    else:
                        print("Invalid Move!\n\n\n\n")
                # Castle King Side as Black
                elif current_position == [4,7] and next_position == [6,7]:
                    if self.castling[3] == 1:
                        rook_current_position_x = 7
                        rook_current_position_y = 7
                        rook_next_position_x = 5
                        rook_next_position_y = 7
                        
                        self.board[next_position_y][next_position_x] = self.board[current_position_y][current_position_x]
                        self.board[current_position_y][current_position_x] = 0
                        self.board[rook_next_position_y][rook_next_position_x] = self.board[rook_current_position_y][rook_current_position_x]
                        self.board[rook_current_position_y][rook_current_position_x] = 0
                
                        self.current_player = self.current_player * -1 
                    else:
                        print("Invalid Move!\n\n\n\n")
                else:
                    self.board[next_position_y][next_position_x] = self.board[current_position_y][current_position_x]
                    self.board[current_position_y][current_position_x] = 0
                    self.current_player = self.current_player * -1 


                    if current_position == [0,0] or next_position == [0,0]: # If rook moves disable castling to that side
                        self.castling[0] = 0
                    elif current_position == [7,0] or next_position == [7,0]: # If rook moves disable castling to that side
                        self.castling[1] = 0
                    elif current_position == [0,7] or next_position == [0,7]: # If rook moves disable castling to that side
                        self.castling[2] = 0
                    elif current_position == [7,7] or next_position == [7,7]: # If rook moves disable castling to that side
                        self.castling[3] = 0
                    elif current_position == [4,0]: # If King moves, disable all castling
                        self.castling[0] = 0
                        self.castling[1] = 0
                    elif current_position == [4,7]: # If King moves, disable all castling
                        self.castling[2] = 0
                        self.castling[3] = 0
                
            else:
                print("Invalid Move!\n\n\n\n")

            
    def check_valid_move(self,current_position,next_position):

        # Ensure white player is moving white pieces, and black player is moving black pieces
        if self.current_player == 1 and self.board[current_position[1]][current_position[0]] < 0:
            return False
        elif self.current_player == -1 and self.board[current_position[1]][current_position[0]] > 0:
            return False
        
        
        # Determine what type of piece is being moved
        type_of_piece = self.chess_pieces_name[self.board[current_position[1]][current_position[0]] * self.current_player]

        # Check the places the Chess Piece can move.
        valid_moves = getattr(Chess,type_of_piece).movement(self, self.current_player, current_position)

        # Check if the King is currently checked
        if self.is_check(valid_moves)[1]:
            valid_moves = [move for move in valid_moves in self.check_escapes[self.current_player]]
        
        # Valid moves that do not cause the king to be in check
        valid_moves_no_check = []
        for move in valid_moves:
            test_game = deepcopy(self)
            test_game.board[move[1]][move[0]] = test_game.board[current_position[1]][current_position[0]]
            test_game.board[current_position[1]][current_position[0]] = 0
            valid_moves_test = test_game.get_all_moves()
            piece, test_check = test_game.is_check(valid_moves_test)
            if not test_check or piece*test_game.current_player < 0:
                valid_moves_no_check.append(move)
            del test_game

        if tuple(next_position) in valid_moves_no_check:
            return True
        else:
            return False
    
    # Get all possible moves for both players
    def get_all_moves(self):
        valid_moves = []
        for y, rank in enumerate(self.board):
            for x, piece in enumerate(rank):
                if piece != 0:
                    piece_name = self.chess_pieces_name[abs(piece)]
                    player = 1 if piece > 0 else -1
                    valid_moves = valid_moves + [i for i in getattr(Chess, piece_name).movement(self, player, [x, y])]
        return valid_moves
    
    # Get all possible moves for both players
    def is_check(self,valid_moves):
        
        for y, rank in enumerate(self.board):
            for x, piece in enumerate(rank):
                if piece in [6,-6]:
                    if (x,y) in valid_moves:
                        return piece, True

        return piece, False
    
    def is_checkmate(self,current_player):
        check_escapes = []
        for y, rank in enumerate(self.board): # Loop through rows
            for x, piece in enumerate(rank): # Loop through columns
                if piece*current_player > 0: # If the piece is the current player's piece
                    piece_name = self.chess_pieces_name[abs(piece)]
                    player = 1 if piece > 0 else -1
                    valid_moves = [i for i in getattr(Chess, piece_name).movement(self, player, [x, y])]
                    for move in valid_moves:
                        test_game = deepcopy(self)
                        test_game.board[move[1]][move[0]] = test_game.board[y][x]
                        test_game.board[y][x] = 0
                        valid_moves_test = test_game.get_all_moves()
                        piece, test_check = test_game.is_check(valid_moves_test)
                        if not test_check:
                            check_escapes.append(move)
                        del test_game
                        
        if (check_escapes == []):
            print('CHECKMATE! ' + str("Black" if current_player == 1 else "White") + " wins!")
            return True
        
        self.check_escapes[current_player] = check_escapes
        return False

    def promotable_pawns(self):
        for y, rank in enumerate(self.board):
            if y in [0,7]:
                for x, piece in enumerate(rank):
                    if piece in [1,-1]:
                        new_piece = input('What piece would you like to change the pawn to? ')
                        self.board[y][x] = self.chess_pieces[new_piece]

        



    class King:
        def __init__(self):
            self.value = 8 # Numerical value of piece
            self.notation = 'Q' # Chess notation
            moves = 0

        def movement(chess_game, current_player, current_position):

            '''
                Some things to think about with Rook Movement:
                    - Rooks can only move in straight lines.
                    - Rooks can only capture straight.
                    - Rooks cannot leap over other pieces.
            '''
            
            places_king_can_move = []

            # Queen can move in all 8 directions on each diagonal.
            # Direction 1 (+1,0)
            if current_position[0] + 1 <= 7 and chess_game.board[current_position[1]][current_position[0]+1] == 0:
                places_king_can_move.append((current_position[0]+1, current_position[1]))
            elif current_position[0] + 1 <= 7 and chess_game.board[current_position[1]][current_position[0]+1]*current_player < 0:
                places_king_can_move.append((current_position[0]+1, current_position[1]))
            
            # Direction 2 (-1,0)
            if current_position[0] - 1 >= 0 and chess_game.board[current_position[1]][current_position[0]-1] == 0:
                places_king_can_move.append((current_position[0]-1, current_position[1]))
            elif current_position[0] - 1 >= 0 and chess_game.board[current_position[1]][current_position[0]-1]*current_player < 0:
                places_king_can_move.append((current_position[0]-1, current_position[1]))

            # Direction 3 (0,+1)
            if current_position[1] + 1 <= 7 and chess_game.board[current_position[1]+1][current_position[0]] == 0:
                places_king_can_move.append((current_position[0], current_position[1]+1))
            elif current_position[1] + 1 <= 7 and chess_game.board[current_position[1]+1][current_position[0]]*current_player < 0:
                places_king_can_move.append((current_position[0], current_position[1]+1))
            
            # Direction 4 (0,-1)
            if current_position[1] - 1 >= 0 and chess_game.board[current_position[1]-1][current_position[0]] == 0:
                places_king_can_move.append((current_position[0], current_position[1]-1))
            elif current_position[1] - 1 >= 0 and chess_game.board[current_position[1]-1][current_position[0]]*current_player < 0:
                places_king_can_move.append((current_position[0], current_position[1]-1))

            # Direction 5 (+1,+1)
            if current_position[1] + 1 <= 7 and current_position[0] + 1 <= 7 and chess_game.board[current_position[1]+1][current_position[0]+1] == 0:
                places_king_can_move.append((current_position[0]+1, current_position[1]+1))
            elif current_position[1] + 1 <= 7 and current_position[0] + 1 <= 7 and chess_game.board[current_position[1]+1][current_position[0]+1]*current_player < 0:
                places_king_can_move.append((current_position[0]+1, current_position[1]+1))

            # Direction 6 (-1,-1)
            if current_position[1] - 1 >= 0 and current_position[0] - 1 >= 0 and chess_game.board[current_position[1]-1][current_position[0]-1] == 0:
                places_king_can_move.append((current_position[0]-1, current_position[1]-1))
            elif current_position[1] - 1 >= 0 and current_position[0] - 1 >= 0 and chess_game.board[current_position[1]-1][current_position[0]-1]*current_player < 0:
                places_king_can_move.append((current_position[0]-1, current_position[1]-1))
            
            # Direction 7 (+1,-1)
            if current_position[1] + 1 <= 7 and current_position[0] - 1 >= 0 and chess_game.board[current_position[1]+1][current_position[0]-1] == 0:
                places_king_can_move.append((current_position[0]-1, current_position[1]+1))
            elif current_position[1] + 1 <= 7 and current_position[0] - 1 >= 0 and chess_game.board[current_position[1]+1][current_position[0]-1]*current_player < 0:
                places_king_can_move.append((current_position[0]-1, current_position[1]+1))

            # Direction 8 (-1,+1)
            if current_position[1] - 1 >= 0 and current_position[0] + 1 <= 7 and chess_game.board[current_position[1]-1][current_position[0]+1] == 0:
                places_king_can_move.append((current_position[0]+1, current_position[1]-1))
            elif current_position[1] - 1 >= 0 and current_position[0] + 1 <= 7 and chess_game.board[current_position[1]-1][current_position[0]+1]*current_player < 0:
                places_king_can_move.append((current_position[0]+1, current_position[1]-1))
            
            # Castle Queen Side
            if current_position in [[4,0],[4,7]] and chess_game.board[current_position[1]][current_position[0]-1] == 0 and chess_game.board[current_position[1]][current_position[0]-2] == 0 and chess_game.board[current_position[1]][current_position[0]-3] == 0:
                places_king_can_move.append((current_position[0]-2, current_position[1]))

            # Castle King Side
            if current_position in [[4,0],[4,7]] and chess_game.board[current_position[1]][current_position[0]+1] == 0 and chess_game.board[current_position[1]][current_position[0]+2] == 0:
                places_king_can_move.append((current_position[0]+2, current_position[1]))

            return places_king_can_move

    class Queen:

        def __init__(self):
            self.value = 8 # Numerical value of piece
            self.notation = 'Q' # Chess notation

        def movement(chess_game, current_player, current_position):

            '''
                Some things to think about with Rook Movement:
                    - Rooks can only move in straight lines.
                    - Rooks can only capture straight.
                    - Rooks cannot leap over other pieces.
            '''
            
            places_queen_can_move = []

            continue_searching = [True,True,True,True,True,True,True,True]
            for squares in range(1,8):

                # Queen can move in all 8 directions on each diagonal.
                # Direction 1 (+,0)
                if continue_searching[0] and current_position[0] + squares <= 7 and chess_game.board[current_position[1]][current_position[0]+squares] == 0:
                    places_queen_can_move.append((current_position[0]+squares, current_position[1]))
                elif continue_searching[0] and current_position[0] + squares <= 7 and chess_game.board[current_position[1]][current_position[0]+squares]*current_player < 0:
                    places_queen_can_move.append((current_position[0]+squares, current_position[1]))
                    continue_searching[0] = False
                elif continue_searching[0]:
                    continue_searching[0] = False
                
                # Direction 2 (-,0)
                if continue_searching[1] and current_position[0] - squares >= 0 and chess_game.board[current_position[1]][current_position[0]-squares] == 0:
                    places_queen_can_move.append((current_position[0]-squares, current_position[1]))
                elif continue_searching[1] and current_position[0] - squares >= 0 and chess_game.board[current_position[1]][current_position[0]-squares]*current_player < 0:
                    places_queen_can_move.append((current_position[0]-squares, current_position[1]))
                    continue_searching[1] = False
                elif continue_searching[1]:
                    continue_searching[1] = False
                
                # Direction 3 (0,+)
                if continue_searching[2] and current_position[1] + squares <= 7 and chess_game.board[current_position[1]+squares][current_position[0]] == 0:
                    places_queen_can_move.append((current_position[0], current_position[1]+squares))
                elif continue_searching[2] and current_position[1] + squares <= 7 and chess_game.board[current_position[1]+squares][current_position[0]]*current_player < 0:
                    places_queen_can_move.append((current_position[0], current_position[1]+squares))
                    continue_searching[2] = False
                elif continue_searching[2]:
                    continue_searching[2] = False
                
                # Direction 4 (0,-)
                if continue_searching[3] and current_position[1] - squares >= 0 and chess_game.board[current_position[1]-squares][current_position[0]] == 0:
                    places_queen_can_move.append((current_position[0], current_position[1]-squares))
                elif continue_searching[3] and current_position[1] - squares >= 0 and chess_game.board[current_position[1]-squares][current_position[0]]*current_player < 0:
                    places_queen_can_move.append((current_position[0], current_position[1]-squares))
                    continue_searching[3] = False
                elif continue_searching[3]:
                    continue_searching[3] = False

                # Direction 5 (+,+)
                if continue_searching[4] and current_position[1] + squares <= 7 and current_position[0] + squares <= 7 and chess_game.board[current_position[1]+squares][current_position[0]+squares] == 0:
                    places_queen_can_move.append((current_position[0]+squares, current_position[1]+squares))
                elif continue_searching[4] and current_position[1] + squares <= 7 and current_position[0] + squares <= 7 and chess_game.board[current_position[1]+squares][current_position[0]+squares]*current_player < 0:
                    places_queen_can_move.append((current_position[0]+squares, current_position[1]+squares))
                    continue_searching[4] = False
                elif continue_searching[4]:
                    continue_searching[4] = False
                
                # Direction 6 (-,-)
                if continue_searching[5] and current_position[1] - squares >= 0 and current_position[0] - squares >= 0 and chess_game.board[current_position[1]-squares][current_position[0]-squares] == 0:
                    places_queen_can_move.append((current_position[0]-squares, current_position[1]-squares))
                elif continue_searching[5] and current_position[1] - squares >= 0 and current_position[0] - squares >= 0 and chess_game.board[current_position[1]-squares][current_position[0]-squares]*current_player < 0:
                    places_queen_can_move.append((current_position[0]-squares, current_position[1]-squares))
                    continue_searching[5] = False
                elif continue_searching[5]:
                    continue_searching[5] = False
                
                # Direction 7 (+,-)
                if continue_searching[6] and current_position[1] + squares <= 7 and current_position[0] - squares >= 0 and chess_game.board[current_position[1]+squares][current_position[0]-squares] == 0:
                    places_queen_can_move.append((current_position[0]-squares, current_position[1]+squares))
                elif continue_searching[6] and current_position[1] + squares <= 7 and current_position[0] - squares >= 0 and chess_game.board[current_position[1]+squares][current_position[0]-squares]*current_player < 0:
                    places_queen_can_move.append((current_position[0]-squares, current_position[1]+squares))
                    continue_searching[6] = False
                elif continue_searching[6]:
                    continue_searching[6] = False
                
                # Direction 8 (-,+)
                if continue_searching[7] and current_position[1] - squares >= 0 and current_position[0] + squares <= 7 and chess_game.board[current_position[1]-squares][current_position[0]+squares] == 0:
                    places_queen_can_move.append((current_position[0]+squares, current_position[1]-squares))
                elif continue_searching[7] and current_position[1] - squares >= 0 and current_position[0] + squares <= 7 and chess_game.board[current_position[1]-squares][current_position[0]+squares]*current_player < 0:
                    places_queen_can_move.append((current_position[0]+squares, current_position[1]-squares))
                    continue_searching[7] = False
                elif continue_searching[7]:
                    continue_searching[7] = False


            return places_queen_can_move

    class Rook:

        def __init__(self):
            self.value = 5 # Numerical value of piece
            self.notation = 'R' # Chess notation

        def movement(chess_game, current_player, current_position):

            '''
                Some things to think about with Rook Movement:
                    - Rooks can only move in straight lines.
                    - Rooks can only capture straight.
                    - Rooks cannot leap over other pieces.
            '''
            
            places_rook_can_move = []

            continue_searching = [True,True,True,True]
            for squares in range(1,8):
 
                # Bishop can move in 4 directions on each diagonal.
                # Direction 1 (+,0)
                if continue_searching[0] and current_position[0] + squares <= 7 and chess_game.board[current_position[1]][current_position[0]+squares] == 0:
                    places_rook_can_move.append((current_position[0]+squares, current_position[1]))
                elif continue_searching[0] and current_position[0] + squares <= 7 and chess_game.board[current_position[1]][current_position[0]+squares] < 0:
                    places_rook_can_move.append((current_position[0]+squares, current_position[1]))
                    continue_searching[0] = False
                elif continue_searching[0]:
                    continue_searching[0] = False
                
                # Direction 2 (-,0)
                if continue_searching[1] and current_position[0] - squares >= 0 and chess_game.board[current_position[1]][current_position[0]-squares] == 0:
                    places_rook_can_move.append((current_position[0]-squares, current_position[1]))
                elif continue_searching[1] and current_position[0] - squares >= 0 and chess_game.board[current_position[1]][current_position[0]-squares]*current_player < 0:
                    places_rook_can_move.append((current_position[0]-squares, current_position[1]))
                    continue_searching[1] = False
                elif continue_searching[1]:
                    continue_searching[1] = False
                
                # Direction 3 (0,+)
                if continue_searching[2] and current_position[1] + squares <= 7 and chess_game.board[current_position[1]+squares][current_position[0]] == 0:
                    places_rook_can_move.append((current_position[0], current_position[1]+squares))
                elif continue_searching[2] and current_position[1] + squares <= 7 and chess_game.board[current_position[1]+squares][current_position[0]]*current_player < 0:
                    places_rook_can_move.append((current_position[0], current_position[1]+squares))
                    continue_searching[2] = False
                elif continue_searching[2]:
                    continue_searching[2] = False
                
                # Direction 4 (0,-)
                if continue_searching[3] and current_position[1] - squares >= 0 and chess_game.board[current_position[1]-squares][current_position[0]] == 0:
                    places_rook_can_move.append((current_position[0], current_position[1]-squares))
                elif continue_searching[3] and current_position[1] - squares >= 0 and chess_game.board[current_position[1]-squares][current_position[0]]*current_player < 0:
                    places_rook_can_move.append((current_position[0], current_position[1]-squares))
                    continue_searching[3] = False
                elif continue_searching[3]:
                    continue_searching[3] = False


            return places_rook_can_move

    class Bishop:
        def __init__(self):
            self.value = 3 # Numerical value of piece
            self.notation = 'B' # Chess notation

        def movement(chess_game, current_player, current_position):

            '''
                Some things to think about with Pawn Movement:
                    - Bishops can only move diagonally.
                    - Bishops can only capture diagonally.
                    - Bishops cannot leap over other pieces.
            '''
            
            places_bishop_can_move = []

            continue_searching = [True,True,True,True]
            for squares in range(1,8):
 
                # Bishop can move in 4 directions on each diagonal.
                # Direction 1 (+,+)
                if continue_searching[0] and current_position[1] + squares <= 7 and current_position[0] + squares <= 7 and chess_game.board[current_position[1]+squares][current_position[0]+squares] == 0:
                    places_bishop_can_move.append((current_position[0]+squares, current_position[1]+squares))
                elif continue_searching[0] and current_position[1] + squares <= 7 and current_position[0] + squares <= 7 and chess_game.board[current_position[1]+squares][current_position[0]+squares]*current_player < 0:
                    places_bishop_can_move.append((current_position[0]+squares, current_position[1]+squares))
                    continue_searching[0] = False
                elif continue_searching[0]:
                    continue_searching[0] = False
                
                # Direction 2 (-,-)
                if continue_searching[1] and current_position[1] - squares >= 0 and current_position[0] - squares >= 0 and chess_game.board[current_position[1]-squares][current_position[0]-squares] == 0:
                    places_bishop_can_move.append((current_position[0]-squares, current_position[1]-squares))
                elif continue_searching[1] and current_position[1] - squares >= 0 and current_position[0] - squares >= 0 and chess_game.board[current_position[1]-squares][current_position[0]-squares]*current_player < 0:
                    places_bishop_can_move.append((current_position[0]-squares, current_position[1]-squares))
                    continue_searching[1] = False
                elif continue_searching[1]:
                    continue_searching[1] = False
                
                # Direction 3 (+,-)
                if continue_searching[2] and current_position[1] + squares <= 7 and current_position[0] - squares >= 0 and chess_game.board[current_position[1]+squares][current_position[0]-squares] == 0:
                    places_bishop_can_move.append((current_position[0]-squares, current_position[1]+squares))
                elif continue_searching[2] and current_position[1] + squares <= 7 and current_position[0] - squares >= 0 and chess_game.board[current_position[1]+squares][current_position[0]-squares]*current_player < 0:
                    places_bishop_can_move.append((current_position[0]-squares, current_position[1]+squares))
                    continue_searching[2] = False
                elif continue_searching[2]:
                    continue_searching[2] = False
                
                # Direction 4 (-,+)
                if continue_searching[3] and current_position[1] - squares >= 0 and current_position[0] + squares <= 7 and chess_game.board[current_position[1]-squares][current_position[0]+squares] == 0:
                    places_bishop_can_move.append((current_position[0]+squares, current_position[1]-squares))
                elif continue_searching[3] and current_position[1] - squares >= 0 and current_position[0] + squares <= 7 and chess_game.board[current_position[1]-squares][current_position[0]+squares]*current_player < 0:
                    places_bishop_can_move.append((current_position[0]+squares, current_position[1]-squares))
                    continue_searching[3] = False
                elif continue_searching[3]:
                    continue_searching[3] = False



            return places_bishop_can_move

    class Knight:
        
        def __init__(self):
            self.value = 3 # Numerical value of piece
            self.notation = 'N' # Chess notation

        def movement(chess_game, current_player, current_position):

            '''
                Some things to think about with Rook Movement:
                    - Rooks can only move in straight lines.
                    - Rooks can only capture straight.
                    - Rooks cannot leap over other pieces.
            '''
            
            places_knight_can_move = []

            continue_searching = [True,True,True,True,True,True,True,True] 
            # Queen can move in all 8 directions on each diagonal.
            # Direction 1 (+2,+1)
            if current_position[1] + 1 <= 7 and current_position[0] + 2 <= 7 and chess_game.board[current_position[1]+1][current_position[0]+2] == 0:
                places_knight_can_move.append((current_position[0]+2, current_position[1]+1))
            elif current_position[1] + 1 <= 7 and current_position[0] + 2 <= 7 and chess_game.board[current_position[1]+1][current_position[0]+2] < 0:
                places_knight_can_move.append((current_position[0]+2, current_position[1]+1))
            
            # Direction 2 (+2,-1)
            if current_position[1] - 1 >= 0 and current_position[0] + 2 <= 7 and chess_game.board[current_position[1]-1][current_position[0]+2] == 0:
                places_knight_can_move.append((current_position[0]+2, current_position[1]-1))
            elif current_position[1] - 1 >= 0 and current_position[0] + 2 <= 7 and chess_game.board[current_position[1]-1][current_position[0]+2] < 0:
                places_knight_can_move.append((current_position[0]+2, current_position[1]-1))
            
            # Direction 3 (-2,+1)
            if current_position[1] + 1 <= 7 and current_position[0] - 2 >= 0 and chess_game.board[current_position[1]+1][current_position[0]-2] == 0:
                places_knight_can_move.append((current_position[0]-2, current_position[1]+1))
            elif current_position[1] + 1 <= 7 and current_position[0] - 2 >= 0 and chess_game.board[current_position[1]+1][current_position[0]-2] < 0:
                places_knight_can_move.append((current_position[0]-2, current_position[1]+1))
            
            # Direction 4 (-2,-1)
            if current_position[1] - 1 >= 0 and current_position[0] - 2 >= 0 and chess_game.board[current_position[1]-1][current_position[0]-2] == 0:
                places_knight_can_move.append((current_position[0]-2, current_position[1]-1))
            elif current_position[1] - 1 >= 0 and current_position[0] - 2 >= 0 and chess_game.board[current_position[1]-1][current_position[0]-2] < 0:
                places_knight_can_move.append((current_position[0]-2, current_position[1]-1))

            # Direction 5 (+1,+2)
            if current_position[1] + 2 <= 7 and current_position[0] + 1 <= 7 and chess_game.board[current_position[1]+2][current_position[0]+1] == 0:
                places_knight_can_move.append((current_position[0]+1, current_position[1]+2))
            elif current_position[1] + 2 <= 7 and current_position[0] + 1 <= 7 and chess_game.board[current_position[1]+2][current_position[0]+1] < 0:
                places_knight_can_move.append((current_position[0]+1, current_position[1]+2))
            
            # Direction 6 (-1,+2)
            if current_position[1] + 2 <= 7 and current_position[0] - 1 >= 0 and chess_game.board[current_position[1]+2][current_position[0]-1] == 0:
                places_knight_can_move.append((current_position[0]-1, current_position[1]+2))
            elif current_position[1] + 2 <= 7 and current_position[0] - 1 >= 0 and chess_game.board[current_position[1]+2][current_position[0]-1] < 0:
                places_knight_can_move.append((current_position[0]-1, current_position[1]+2))
            
            # Direction 7 (+1,-2)
            if current_position[1] - 2 >= 0 and current_position[0] + 1 <= 7 and chess_game.board[current_position[1]-2][current_position[0]+1] == 0:
                places_knight_can_move.append((current_position[0]+1, current_position[1]-2))
            elif current_position[1] - 2 >= 0 and current_position[0] + 1 <= 7 and chess_game.board[current_position[1]-2][current_position[0]+1] < 0:
                places_knight_can_move.append((current_position[0]+1, current_position[1]-2))
            
            # Direction 8 (-1,-2)
            if current_position[1] - 2 >= 0 and current_position[0] - 1 >= 0 and chess_game.board[current_position[1]-2][current_position[0]-1] == 0:
                places_knight_can_move.append((current_position[0]-1, current_position[1]-2))
            elif current_position[1] - 2 >= 0 and current_position[0] - 1 >= 0 and chess_game.board[current_position[1]-2][current_position[0]-1] < 0:
                places_knight_can_move.append((current_position[0]-1, current_position[1]-2))


            return places_knight_can_move

    class Pawn:

        def __init__(self):
            self.value = 1 # Numerical value of piece
            self.notation = '' # Chess notation

        def movement(chess_game, current_player, current_position):

            '''
                Some things to think about with Pawn Movement:
                    - Pawns can only move forward when not attacking.
                    - Pawns can only capture diagonally.
                    - Pawn cannot leap over other pieces.
                    - (Special Case): If the Pawn is in its inital spot, it can move 2 squares or 1 square forward, assuming space exists.
                    - (Special Case): En Passant - A Pawn can capture another pawn if an enemy pawn moved 2 spaces forward and is currently adjacent to this pawn.
            '''
            
            places_pawn_can_move = []

            # Check to see if the pawn is on the initial rank or not, if it is, it can move 2 squares, if not, it can move 1.
            current_rank = current_position[1]
            if (current_rank == 6 and current_player == 1) or (current_rank == 1 and current_player == -1):
                squares_pawn_can_move = 2
            else:
                squares_pawn_can_move = 1


            for squares in range(1,squares_pawn_can_move+1):
                if (current_player == 1):
                    # If the current player is white, check the squares you can move forward and break if there is a piece in the way.
                    if current_position[1] - squares >= 0 and chess_game.board[current_position[1]-squares][current_position[0]] == 0:
                        places_pawn_can_move.append((current_position[0], current_position[1] - squares))
                    else:
                        break

                elif (current_player == -1):
                    # If the current player is white, check the squares you can move forward and break if there is a piece in the way.
                    if current_position[1] + squares <= 7 and chess_game.board[current_position[1]+squares][current_position[0]] == 0:
                        places_pawn_can_move.append((current_position[0], current_position[1] + squares))
                    else:
                        break

            if (current_player == 1):
                    # Capture Left-forward
                    if current_position[0] < 7 and current_position[1] > 0 and chess_game.board[current_position[1]-1][current_position[0]+1] < 0:
                        places_pawn_can_move.append((current_position[0]+1,current_position[1]-1))

                    # Capture Right-forward
                    if current_position[0] > 0 and current_position[1] > 0 and chess_game.board[current_position[1]-1][current_position[0]-1] < 0:
                        places_pawn_can_move.append((current_position[0]-1,current_position[1]-1))

            elif (current_player == -1):
                    # Capture Left-forward
                    if current_position[0] < 7 and current_position[1] < 7 and chess_game.board[current_position[1]+1][current_position[0]+1] > 0:
                        places_pawn_can_move.append((current_position[0]+1,current_position[1]+1))

                    # Capture Right-forward
                    if current_position[0] > 0 and current_position[1] < 7 and chess_game.board[current_position[1]+1][current_position[0]-1] > 0:
                        places_pawn_can_move.append((current_position[0]-1,current_position[1]+1))

            return places_pawn_can_move