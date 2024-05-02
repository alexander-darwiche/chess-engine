

import math
import random
from chess import Chess
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt



import random_ai
random_agent = random_ai.random_ai()

class MCTS_ai:

    def __init__(self, game, parent=None, parent_move = None):
        self.game = game
        self.state = self.game.board
        self.parent = parent
        self.parent_move = parent_move
        self.child = []
        self.player = self.game.current_player
        self.possible_moves = self.game.get_all_moves_dict(for_player=self.player)
        self.results = {}
        self.T = 0
        self.N = 0
        self.done = False


    def choose_move(self):
        max_val = max(self.results.values())
        result = [key for key in self.results if self.results[key] == max_val]
        key = random.choice(result)
        return key
    
    
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
        We create one children for each possible action of the game, 
        then we apply such action to a copy of the current node enviroment 
        and create such child node with proper information returned from the action executed
        '''
    
        actions = []
        games = []

        for current_position in self.possible_moves:
            for j in self.possible_moves[current_position][1]:
                next_position = self.game.x_notation[j[0]] + self.game.y_notation[j[1]]
                actions.append([current_position,next_position])
                new_game = deepcopy(self.game)
                games.append(new_game)
                
                    
        child = {} 
        for action, game in zip(actions, games):
            game.move_piece(action[0],action[1])
            action_key = action[0] + " to " + action[1]
            child[action_key] = MCTS_ai(game = game, parent_move=action_key)                        
            
        self.child = child

    def explore(self):
        
        '''
        The search along the tree is as follows:
        - from the current node, recursively pick the children which maximizes the value according to the MCTS formula
        - when a leaf is reached:
            - if it has never been explored before, do a rollout and update its current value
            - otherwise, expand the node creating its children, pick one child at random, do a rollout and update its value
        - backpropagate the updated statistics up the tree until the root: update both value and visit counts
        '''
        
        # find a leaf node by choosing nodes with max U.
        
        current = self

        while current.child:

            child = current.child
            max_U = max(c.getUCBscore() for c in child.values())
            actions = [ a for a,c in child.items() if c.getUCBscore() == max_U ]
            if len(actions) == 0:
                print("error zero length ", max_U)                      
            action = random.choice(actions)
            current = child[action]
            
        # play a random game, or expand if needed          
        if current.N < 1:
            current.T = current.T + current.rollout()
        else:
            current.create_child()
            if current.child:
                try:
                    current_key = random.choice([a for a in current.child.keys()])
                    current = current.child[current_key]
                                            
                except:
                    import pdb;pdb.set_trace()
            current.T = current.T + current.rollout()

        current.N += 1      
                
        # update statistics and backpropagate
        parent = current
            
        while parent.parent:
            
            parent = parent.parent
            parent.N += 1
            parent.T = parent.T + current.T

    def rollout(self):
        
        '''
        The rollout is a random play from a copy of the environment of the current node using random moves.
        This will give us a value for the current node.
        Taken alone, this value is quite random, but, the more rollouts we will do for such node,
        the more accurate the average of the value for such node will be. This is at the core of the MCTS algorithm.
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
                    result = 1 if loser_king*self.player < 0 else 0

            if new_game.is_king_bishop_draw():
                    keep_playing = False
                    result = .5

            if keep_playing:    
                if new_game.current_player == 1:
                    random_agent.choose_move(new_game)
                else:
                    random_agent.choose_move(new_game)

                new_game.promotable_pawns()  
        #print(result)  
        return result
    
    def next(self):
        
        ''' 
        Once we have done enough search in the tree, the values contained in it should be statistically accurate.
        We will at some point then ask for the next action to play from the current node, and this is what this function does.
        There may be different ways on how to choose such action, in this implementation the strategy is as follows:
        - pick at random one of the node which has the maximum visit count, as this means that it will have a good value anyway.
        '''

        if self.done:
            raise ValueError("game has ended")

        if not self.child:
            raise ValueError('no children found and game hasn\'t ended')
        
        child = self.child
        
        max_N = max(node.N for node in child.values())
       
        max_children = [ c for a,c in child.items() if c.N == max_N ]
        
        if len(max_children) == 0:
            print("error zero length ", max_N) 
            
        max_child = random.choice(max_children)
        
        return max_child, max_child.parent_move


chess = Chess()
mcts_ai = MCTS_ai(game = chess)
mcts_ai.game.display_game()

while not mcts_ai.done:

    print('White\'s Turn')
    
    for i in range(25):
        mcts_ai.explore()
    
    mcts_ai, action = mcts_ai.next()
    print(action)
    # import pdb;pdb.set_trace()
    
    # mcts_ai.game.move_piece(action.split()[0],action.split()[2])
    mcts_ai.game.display_game()

    # print('Black\'s Turn')
    # location_current_piece = input("What piece?")
    # location_move = input("Where to?")
    # mcts_ai.game.move_piece(location_current_piece,location_move)
    # #mcts_ai, action = mcts_ai.next()
    # print(action)
    # mcts_ai.game.display_game()

    if mcts_ai.game.is_checkmate():
        mcts_ai.done = True
        import pdb;pdb.set_trace()




import pdb;pdb.set_trace()

