from Board import Board
from Minimax_AlphaBeta import back_to_start_state
from math import log
#from numba import njit

class Node:
    
    def __init__(self, board):
        self.board = board
        self.wins = 0
        self.draws = 0
        self.visits = 0
        self.parents = set()
        
    def add_parent(self, parent):
        if isinstance(parent, Board):
            parent_representation = parent.get_representation()
            self.parents.add(parent_representation)
        else:
            self.parents.add(parent)
            
    def update(self, player, winner):
        if player == winner:
            self.wins += 1
        elif winner == 0:
            self.draws += 1
        
        self.visits += 1
            
    def calculate_parents_visits(self):
        total_parents_visits = 1
        for parent in self.parents:
            total_parents_visits += parent.visits
        return total_parents_visits
    
    def calculate_winrate(self):
        if self.visits == 0:
            return 0
        
        return (self.wins + 0.75*self.draws) / self.visits #we count the draws in the winrate because, under best play, a draw is the best result one can get
                                                          #however, we give less weight to the draw because we want our engine to favor positions where it wins
            
    def calculate_uct(self, c):
        if self.visits == 0:
            return float('inf')
        
        winrate = self.calculate_winrate()
        
        parents_visits = self.calculate_parents_visits()
        exploration = c * (log(parents_visits) / self.visits)**(1/2)
        
        return winrate + exploration

#@njit
def choose_node_uct(board, player, dic_nodes_visited, c):
    #dic has the board representation as key and the node as value
    
    if board.isGameOver():
        return None
    
    nb_moves_beginning = len(board.moves)
    best_uct = -float('inf')
    best_move = None
    for i in range(3):
        for j in range(3):
            try:
                board.play(i, j, player)
                
                if dic_nodes_visited.get(board.get_representation()) != None: #the node has already been visited and exists in the dictionary
                    node = dic_nodes_visited.get(board.get_representation())
                    uct = node.calculate_uct(c)
                else:
                    node = Node(board.copy())
                    dic_nodes_visited[node.board.get_representation()] = node
                    uct = node.calculate_uct(c)
                    
                if uct >= best_uct:
                    best_uct = uct
                    best_move = (i, j, node)
                
                back_to_start_state(board, nb_moves_beginning)
            except:
                back_to_start_state(board, nb_moves_beginning)
    
    back_to_start_state(board, nb_moves_beginning)      
    return best_move

def choose_node_winrate(board, player, dic_nodes_visited):    
    if board.isGameOver():
        return None
    
    nb_moves_beginning = len(board.moves)
    best_winrate = -1
    best_move = None
    for i in range(3):
        for j in range(3):
            try:
                board.play(i, j, player)
                
                if dic_nodes_visited.get(board.get_representation()) != None: #the node has already been visited and exists in the dictionary
                    node = dic_nodes_visited.get(board.get_representation())
                    winrate = node.calculate_winrate()
                else:
                    winrate = 0
                    
                if winrate >= best_winrate:
                    best_winrate = winrate
                    best_move = (i, j, node)
                
                back_to_start_state(board, nb_moves_beginning)
            except:
                back_to_start_state(board, nb_moves_beginning)
    
    back_to_start_state(board, nb_moves_beginning)      
    return best_move

def play_move_in_simulation(board, player, dic_nodes_visited, path, c):
    
    try:
        parent = dic_nodes_visited[board.get_representation()]
    except:
        parent = Node(board.copy())
    
    try:
        (i, j, best_node) = choose_node_uct(board, player, dic_nodes_visited, c)
        try:
            board.play(i, j, player)
            path.append((best_node, player))
                
            best_node.add_parent(parent)
            
        except:
            pass
    except:
        pass
    

def backpropagation(path, winner):
    for i in range(len(path)-1, -1, -1):
        node, player = path[i]
        node.update(player, winner)
            
    
def make_complete_simulation(board, player, dic_nodes_visited, c):
    path = []
    
    while not board.isGameOver():
        play_move_in_simulation(board, player, dic_nodes_visited, path, c)
        if player == -1:
            player = 1
        else:
            player = -1
    
    winner = board.gameState
    backpropagation(path, winner)
 
def play_mcts(board, player, nb_simulations, c = 2**(1/2)):
    dic_nodes_visited = {}
    
    for i in range(nb_simulations):
        copy_board = board.copy()
        make_complete_simulation(copy_board, player, dic_nodes_visited, c)
    
    (i, j, node) = choose_node_winrate(board, player, dic_nodes_visited)
    board.play(i, j, player)
    return dic_nodes_visited