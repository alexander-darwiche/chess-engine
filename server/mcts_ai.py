

import math
import random
from copy import deepcopy



import random_ai
random_agent = random_ai.random_ai()

class MCTS_ai:

    def __init__(self, game, parent=None, parent_move = None, possible_moves = None):
        self.game = game
        self.parent = parent
        self.parent_move = parent_move
        self.child = []
        self.player = self.game.current_player
        self.possible_moves = self.game.get_all_moves_dict(for_player=self.game.current_player)
        self.T = 0
        self.N = 0
    
    def getUCBscore(self):
        '''
            This function returns the Upper Confidence Bound for a specific node

            @param self - current node, this node includes the number of times visited (N) and the total value (T) for the Node

            @return - The UCB given the N and T of the node
        '''

        if self.N == 0:
            return float('inf')

        top_node = self
        if top_node.parent:
            top_node = top_node.parent
        
        # Calculate the UCB for the node
        return (self.T / self.N) + 1 * math.sqrt(math.log(top_node.N) / self.N) 
    
    def create_child(self):
        '''
            This function creates the children nodes for a parent node. These children 
            are all the possible moves that can be made from the current game state.

            @param self - Current/parent node.
        '''
    
        moves = []
        games = []
        
        # Loop through all possible moves and create lists of actions and the games
        for current_position in self.possible_moves:
            for j in self.possible_moves[current_position][1]:
                next_position = self.game.x_notation[j[0]] + self.game.y_notation[j[1]]
                moves.append([current_position,next_position])
                new_game = deepcopy(self.game)
                games.append(new_game)
                
                    
        child = {} 
        # Add each child with the action as the key, and the item being the new game resulting from the action
        for move, game in zip(moves, games):
            game.move_piece(move[0],move[1])
            move_key = move[0] + " to " + move[1]
            child[move_key] = MCTS_ai(game = game, parent = self, parent_move=move_key, possible_moves = self.game.get_all_moves_dict(for_player=self.game.current_player))                        
        
        # Set the children of the current game    
        self.child = child

    def explore(self):
        '''
            This is the main function of the Monte-Carlo Tree Search. Essentially you start with 
            a Node. If that nodes has children, then you pick the node with the highest UCB and you
            "explore" that node. If that node then has no children and has not been visited before,
            then you do a random playout simulation (rollout). If that node has been visited before,
            then you instead create all that nodes children. Each time running through this function 
            is a "simulation". Ideally this could be run thousands of times at each decision point.

            @param self - Current/parent node.
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
            This a random playout of a game. From a given game state, this function continues 
            running 2 random agents until the game reaches a complete state.

            @param self - Current/parent node.

            @return result - The result of the game. If White or Black wins it is a 1 (depending on the node's player) and if its a draw, then its a .5
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
        '''
            This function returns the action that is taken by the MCTS algorithm
            after the simulations have been run. This navigates through the tree
            and takes us down the path that has been explored the most by the algorithm
            to that date. The reason it goes down the most populated path, is because 
            we want to explore the path that is most well understood first, and second
            we have down selected the highest UCB's to explore this path most often anyways.

            @param self - Current/parent node.

            @return max_child - Child with the most visits.
            @return max_child.parent_move - The move that led to this game state.
        '''

        # Find the node that's been visited the most
        max_N = max(node.N for node in self.child.values())

        # Find the children that have been visited the most times
        max_children = [ c for a,c in self.child.items() if c.N == max_N ]
        
        # Return a random child that's been visited the most times
        max_child = random.choice(max_children)
        
        # Return this new child and the value that led to this child
        return max_child, max_child.parent_move

    def play(self, iterations):
        '''
            This is called to run Monte-Carlo Tree Search on the a given game state. This
            will run as many iterations as are specified by the user, and then return the 
            recommended move to take.

            @param self - Current/parent node.

            @return child - Child with the most visits.
            @return move - The move that led to this game state.
        
        '''

        for i in range(iterations):
            self.explore()

        child, move = self.next()
        
        # self.mcts_viz_helper()
                
        return child, move
    
    def mcts_viz_helper(self):
        stack = [self]
        while stack:
            for i in stack:
                key = i.parent_move if i.parent_move is not None else "Root"
                stack.remove(i)
                print("Move: " + key + " -- wins:" + str(i.T) + " total: " + str(i.N))
                if i.child != []:
                    for key,item in i.child.items():
                        stack.append(item)