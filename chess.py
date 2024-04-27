# Chess Class 
# This includes the rules and moves generation for a chess game.

import math

class Chess():
    

    # Initalize Chess Game 
    def __init__(self):
        '''
            This is the initialization of the Chess Game. Will hold all base assumptions for a chess match.
        '''
        self.x_notation = ['a','b','c','d','e','f','g','h'] # the chess board is 8x8, this is the x-axis Notation/Coordinate
        self.y_notation = ['8','7','6','5','4','3','2','1'] # the chess board is 8x8, this is the x-axis Notation/Coordinate

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
                print('This is a vaild Move!\n\n\n\n')
                self.board[next_position_y][next_position_x] = self.board[current_position_y][current_position_x]
                self.board[current_position_y][current_position_x] = 0
                self.current_player = self.current_player * -1 
            else:
                print("Invalid Move!\n\n\n\n")

            


    def check_valid_move(self,current_position,next_position):

        # Ensure white player is moving white pieces, and black player is moving black pieces
        if self.current_player == 1 and self.board[current_position[1]][current_position[0]] < 0:
            return False
        elif self.current_player == -1 and self.board[current_position[1]][current_position[0]] > 0:
            return False

        # Determine what type of piece is being moved
        import pdb;pdb.set_trace()
        type_of_piece = self.chess_pieces_name[abs(self.board[current_position[1]][current_position[0]])]

        # Check the places the Chess Piece can move.
        places = getattr(Chess,type_of_piece).movement(self, self.current_player, current_position)

        if tuple(next_position) in places:
            return True
        else:
            return False
        

    class King:
        print('hi')


    class Queen:
        print('hi')

    class Rook:
        print('hi')

    class Bishop:
        def __init__(self):
            self.value = 3 #Numerical value of piece
            self.notation = '' #Chess notation

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
                elif continue_searching[0] and current_position[1] + squares <= 7 and current_position[0] + squares <= 7 and chess_game.board[current_position[1]+squares][current_position[0]+squares] < 0:
                    places_bishop_can_move.append((current_position[0]+squares, current_position[1]+squares))
                    continue_searching[0] = False
                elif continue_searching[0]:
                    continue_searching[0] = False
                
                # Direction 2 (-,-)
                if continue_searching[1] and current_position[1] - squares >= 0 and current_position[0] - squares >= 0 and chess_game.board[current_position[1]-squares][current_position[0]-squares] == 0:
                    places_bishop_can_move.append((current_position[0]-squares, current_position[1]-squares))
                elif continue_searching[1] and current_position[1] - squares >= 0 and current_position[0] - squares >= 0 and chess_game.board[current_position[1]-squares][current_position[0]-squares] < 0:
                    places_bishop_can_move.append((current_position[0]-squares, current_position[1]-squares))
                    continue_searching[1] = False
                elif continue_searching[1]:
                    continue_searching[1] = False
                
                # Direction 3 (+,-)
                if continue_searching[2] and current_position[1] + squares <= 7 and current_position[0] - squares >= 0 and chess_game.board[current_position[1]+squares][current_position[0]-squares] == 0:
                    places_bishop_can_move.append((current_position[0]-squares, current_position[1]+squares))
                elif continue_searching[2] and current_position[1] + squares <= 7 and current_position[0] - squares >= 0 and chess_game.board[current_position[1]+squares][current_position[0]-squares] < 0:
                    places_bishop_can_move.append((current_position[0]-squares, current_position[1]+squares))
                    continue_searching[2] = False
                elif continue_searching[2]:
                    continue_searching[2] = False
                
                # Direction 4 (-,+)
                if continue_searching[3] and current_position[1] - squares >= 0 and current_position[0] + squares <= 7 and chess_game.board[current_position[1]-squares][current_position[0]+squares] == 0:
                    places_bishop_can_move.append((current_position[0]+squares, current_position[1]-squares))
                elif continue_searching[3] and current_position[1] - squares >= 0 and current_position[0] + squares <= 7 and chess_game.board[current_position[1]-squares][current_position[0]+squares] < 0:
                    places_bishop_can_move.append((current_position[0]+squares, current_position[1]-squares))
                    continue_searching[3] = False
                elif continue_searching[3]:
                    continue_searching[3] = False



            return places_bishop_can_move

    class Knight:
        print('hi')

    class Pawn:

        def __init__(self):
            self.value = 1 #Numerical value of piece
            self.notation = '' #Chess notation

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
                    if current_position[1] + squares <= 7 and chess_game.board[current_position[1]-squares][current_position[0]] == 0:
                        places_pawn_can_move.append((current_position[0], current_position[1] - squares))
                    else:
                        break

                elif (current_player == -1):
                    # If the current player is white, check the squares you can move forward and break if there is a piece in the way.
                    if current_position[1] - squares >= 0 and chess_game.board[current_position[1]+squares][current_position[0]] == 0:
                        places_pawn_can_move.append((current_position[0], current_position[1] + squares))
                    else:
                        break

            if (current_player == 1):
                    # Capture Left-forward
                    if current_position[0] < 7 and chess_game.board[current_position[1]-1][current_position[0]+1] < 0:
                        places_pawn_can_move.append((current_position[0]+1,current_position[1]-1))

                    # Capture Right-forwad
                    if current_position[0] > 0 and chess_game.board[current_position[1]-1][current_position[0]-1] < 0:
                        places_pawn_can_move.append((current_position[0]-1,current_position[1]-1))

            elif (current_player == -1):
                    # Capture Left-forward
                    if current_position[0] < 7 and chess_game.board[current_position[1]+1][current_position[0]+1] > 0:
                        places_pawn_can_move.append((current_position[0]+1,current_position[1]+1))

                    # Capture Right-forwad
                    if current_position[0] > 0 and chess_game.board[current_position[1]+1][current_position[0]-1] > 0:
                        places_pawn_can_move.append((current_position[0]-1,current_position[1]+1))

            return places_pawn_can_move




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