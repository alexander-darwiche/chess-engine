

import math
import random
from chess import Chess
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt



import random_ai
random_agent = random_ai.random_ai()

class MCTS_ai:

    def __init__(self, game, parent=None, parent_move = None, possible_moves = None):
        self.game = game
        self.state = self.game.board
        self.parent = parent
        self.parent_move = parent_move
        self.child = []
        self.player = self.game.current_player
        self.possible_moves = self.game.get_all_moves_dict(for_player=self.game.current_player)
        self.results = {}
        self.T = 0
        self.N = 0
        self.done = False
    
    def getUCBscore(self):

        # Unexplored nodes have maximum values so we favour exploration
        if self.N == 0:
            return float('inf')

        # We need the parent node of the current node 
        top_node = self
        if top_node.parent:
            top_node = top_node.parent
            
        # We use one of the possible MCTS formula for calculating the node value
        return (self.T / self.N) + 1 * math.sqrt(math.log(top_node.N) / self.N) 
    
    def create_child(self):
        '''
        '''
    
        actions = []
        games = []
        
        # Loop through all possible moves and create lists of actions and the games
        for current_position in self.possible_moves:
            for j in self.possible_moves[current_position][1]:
                next_position = self.game.x_notation[j[0]] + self.game.y_notation[j[1]]
                actions.append([current_position,next_position])
                new_game = deepcopy(self.game)
                games.append(new_game)
                
                    
        child = {} 
        # Add each child with the action as the key, and the item being the new game resulting from the action
        for action, game in zip(actions, games):
            game.move_piece(action[0],action[1])
            action_key = action[0] + " to " + action[1]
            child[action_key] = MCTS_ai(game = game, parent = self, parent_move=action_key, possible_moves = self.game.get_all_moves_dict(for_player=self.game.current_player))                        
        
        # Set the children of the current game    
        self.child = child

    def explore(self):
        '''
        '''
        
        # Current will hold the current game state that we are looking at.
        current = self

        # If we've already built out the children for the current game
        while current.child:
                    
            child = current.child
            # Get the max value UCB of all the children nodes
            max_UCB = max(child_node.getUCBscore() for child_node in child.values())

            # Get the specific children that have this max UCB values
            moves = [ move for move,child_node in child.items() if child_node.getUCBscore() == max_UCB ]

            # Randomly select one of the children that has the highest UCB of the current children
            move = random.choice(moves)

            # Set current to 
            current = child[move]
            # After this, we loop back to the top and see if this child node has children.
            # If it does have children, again pick the one with the highest UCB.
            # If it does not have children, go deeper into the tree and create children for it.

        # play a random game, or expand if needed          
        if current.N < 1:
            # Update the win/lose/draw values
            current.T = current.T + current.rollout()
        else:
            # If the node has been visited, create children node for it. This is all possible moves from the current posisiton.
            current.create_child()

            # If the current node has children, randomly select one of them.
            if current.child:
                current_key = random.choice([move for move in current.child.keys()])
                current = current.child[current_key]

            # Perform a rollout for the random child
            current.T = current.T + current.rollout()
        # Make sure visits are updated appopriately
        current.N += 1      
                
        # update statistics and backpropagate
        parent = current
            
        while parent.parent:
            
            parent = parent.parent
            parent.N += 1
            parent.T = parent.T + current.T

    def rollout(self):
        '''
        '''
        
        new_game = deepcopy(self.game)     
        
        result = 0
        keep_playing = True
        while keep_playing:

            # Check if stalemate
            if new_game.is_stalemate():
                keep_playing = False
                result = 0

            loser_king, checked = new_game.is_check()
            if (checked):
                if new_game.is_checkmate():
                    keep_playing = False
                    result = 1 if loser_king == -6 else -1

            if new_game.is_king_bishop_draw():
                    keep_playing = False
                    result = 0

            if keep_playing:    
                if new_game.current_player == 1:
                    random_agent.choose_move(new_game)
                else:
                    random_agent.choose_move(new_game)

                new_game.promotable_pawns()  

        return result
    
    def next(self):

        # Find the node that's been visited the most
        max_N = max(node.N for node in self.child.values())

        # Find the children that have been visited the most times
        max_children = [ c for a,c in self.child.items() if c.N == max_N ]
        
        # Return a random child that's been visited the most times
        max_child = random.choice(max_children)
        
        # Return this new child and the value that led to this child
        return max_child, max_child.parent_move

    def play(self, iterations):

        for i in range(iterations):
            self.explore()

        child, move = self.next()
        return child, move



# chess = Chess()
# mcts_ai = MCTS_ai(game = chess)
# mcts_ai.game.display_game()



# while not mcts_ai.done:
    
#     # Check if stalemate
#     if mcts_ai.game.is_stalemate():
#         mcts_ai.done = True
#         break

#     loser_king, checked = mcts_ai.game.is_check()
#     if (checked):
#         if mcts_ai.game.is_checkmate():
#             mcts_ai.done = True
#             break

#     if mcts_ai.game.is_king_bishop_draw():
#             mcts_ai.done = True
#             break

#     mcts_ai.game.promotable_pawns()  
    
#     if mcts_ai.game.current_player == 1:
#         print('White\'s Turn')

#         for i in range(25):
#             mcts_ai.explore()
                
#         mcts_ai, action = mcts_ai.next()
#         chess = deepcopy(mcts_ai.game)
#         print(action)
        
#         mcts_ai.game.display_game()
#     else:
#         print('Black\'s Turn')
#         location_current_piece = input("What piece?")
#         location_move = input("Where to?")
#         mcts_ai.game.move_piece(location_current_piece,location_move)

#         print(action)
#         mcts_ai.game.display_game()






# import pdb;pdb.set_trace()

