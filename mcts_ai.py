

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
                
        # update statistics and back propagate
        parent = current
        
        # This can be tricky, update the parent nodes based on their current_player.
        while parent.parent:
            parent = parent.parent
            parent.N += 1

            # This achieves the 2 player game back propogation
            if current.T == 1:
                back_prop_value = 0
            elif current.T == 0:
                back_prop_value = 1
            else:
                back_prop_value = .5

            parent.T = parent.T + back_prop_value

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
                result = .5

            loser_king, checked = new_game.is_check()
            if (checked):
                if new_game.is_checkmate():
                    keep_playing = False
                    result = 1 if loser_king*self.game.current_player == -6 else 0

            if new_game.is_king_bishop_draw():
                    keep_playing = False
                    result = .5

            if keep_playing:    
                if new_game.current_player == 1:
                    random_agent.choose_move(new_game)
                else:
                    random_agent.choose_move(new_game)

                new_game.promotable_pawns()  
        
        # This achieves the 2 player game back propogation
        if result == 1 and self.game.current_player == -1:
            result = 0
        elif result == 0 and self.game.current_player == -1:
            result = 1

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
        
        # stack = [self]
        # while stack:
        #     for i in stack:
        #         key = i.parent_move if i.parent_move is not None else "Root"
        #         stack.remove(i)
        #         print("Move: " + key + " -- wins:" + str(i.T) + " total: " + str(i.N))
        #         if i.child != []:
        #             for key,item in i.child.items():
        #                 stack.append(item)

                
        return child, move