from Board_script import Board
import numpy as np

def back_to_start_state(board, nb_moves_beginning):
    """
    Reverts the board to a specified state by undoing moves until it reaches the number of moves at the beginning.

    Parameters
    ----------
    board : Board
        The board to revert.
    nb_moves_beginning : int
        The number of moves to revert to.
    """
    
    while len(board.moves) > nb_moves_beginning:
        board.undo_last_move()

class Node:
    """
    Represents a node in the MCTS tree.

    Parameters
    ----------
    board : Board
        The state of the game at this node.
    parents : set, optional
        A set of parent nodes. Defaults to an empty set.

    Attributes
    ----------
    board : Board
        The state of the game at this node.
    wins : int
        The number of wins observed from this node.
    draws : int
        The number of draws observed from this node.
    visits : int
        The number of visits to this node.
    parents : set
        A set of parent nodes.
    """
    
    def __init__(self, board, parents=set()):
        """
        Initializes a Node with a board state and optionally parent nodes.
        
        Parameters
        ----------
        board : Board 
            The current state of the game.
        parents : set, optional
            Parent nodes. Defaults to an empty set.
        """
        self.board = board
        self.wins = 0
        self.draws = 0
        self.visits = 0
        self.parents = parents
        
    def add_parent(self, parent):
        """
        Adds a parent node to the current node.

        Parameters
        ----------
        parent : Node or Board
            The parent node to add. If a Board instance is passed, its representation is used as the parent identifier. Otherwise, the parent node itself is added to the parents set.
        """
    
        if isinstance(parent, Board):
            parent_representation = parent.get_representation()
            self.parents.add(parent_representation)
        else:
            self.parents.add(parent)
            
    def update(self, player, winner):
        """
        Updates the node's statistics based on the outcome of a simulation.

        Parameters
        ----------
        player : int
            The identifier of the player (1 for player X, -1 for player O) who made the move leading to this node.
        winner : int
            The outcome of the game from this node's perspective (-1 for O wins, 1 for X wins, 0 for draw).
        """
        
        if player == winner:
            self.wins += 1
        elif winner == 0:
            self.draws += 1
        
        self.visits += 1
            
    def calculate_parents_visits(self):
        """
        Calculates the total number of visits to all parent nodes.
        This is used in the UCT calculation to adjust the exploration term based on the total number of simulations that have passed through the parent nodes.

        Returns
        -------
        int
            The total number of visits to this node's parent nodes.
        """
        
        total_parents_visits = 1
        for parent in self.parents:
            total_parents_visits += parent.visits
        return total_parents_visits
    
    def calculate_winrate(self):
        """
        Calculates the win rate for this node, considering both wins and draws. Draws are counted as half a win to indicate a partially positive outcome.

        Returns
        -------
        float
            The win rate of this node, calculated as (wins + 0.5 * draws) / visits.
        """
        if self.visits == 0:
            return 0
        
        return (self.wins + 0.5*self.draws) / self.visits #we count the draws in the winrate because, under best play, a draw is the best result one can get
                                                          #however, we give less weight to the draw because we want our engine to favor positions where it wins
            
    def calculate_uct(self, c):
        """
        Calculates the Upper Confidence Bound (UCT) for this node, used for selecting nodes during the tree search. 
        The UCT value balances exploration and exploitation by considering both the win rate and the exploration term, 
        which is influenced by the total number of parent visits and the number of visits to this node.

        Parameters
        ----------
        c : float
            The exploration parameter used in the UCT calculation.

        Returns
        -------
        float
            The UCT value for this node. Returns infinity (`float('inf')`) if the node has not been visited, to ensure unvisited nodes are prioritized.
        """
        
        if self.visits == 0:
            return float('inf')
        
        winrate = self.calculate_winrate()
        
        parents_visits = self.calculate_parents_visits()
        exploration = c * (np.log2(parents_visits) / self.visits)**(1/2)
        
        return winrate + exploration

def choose_node_uct(board, player, dic_nodes_visited, c):
    """
    Chooses the next move based on the Upper Confidence Bound applied to trees (UCT) metric.

    Parameters
    ----------
    board : Board
        The current state of the board.
    player : int
        The current player (-1 for O, 1 for X).
    dic_nodes_visited : dict
        A dictionary of visited nodes with their board representation as keys.
    c : float
        The exploration parameter for UCT.

    Returns
    -------
    tuple
        The best move (i, j) and its corresponding node, or None if the game is over.
    """
    
    if board.isGameOver():
        return None
    
    nb_moves_beginning = len(board.moves)
    best_uct = -float('inf')
    best_move = None
    for i, j in board.available_moves:
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
      
    return best_move

def choose_node_winrate(board, player, dic_nodes_visited):    
    """
    Chooses the next move based on the highest win rate from the visited nodes.

    Parameters
    ----------
    board : Board
        The current state of the board.
    player : int
        The current player (-1 for O, 1 for X).
    dic_nodes_visited : dict
        A dictionary of visited nodes with their board representation as keys.

    Returns
    -------
    tuple
        The best move (i, j) and its corresponding node, or None if the game is over.
    """
    
    if board.isGameOver():
        return None
    
    nb_moves_beginning = len(board.moves)
    best_winrate = -1
    best_move = None
    for i, j in board.available_moves:
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
    return best_move

def play_move_in_simulation(board, player, dic_nodes_visited, path, c):
    """
    Simulates playing a move on the board for the current player using the UCT algorithm.

    Parameters
    ----------
    board : Board
        The current state of the board on which the move will be simulated.
    player : int
        The identifier of the current player (1 for player X, -1 for player O) making the move.
    dic_nodes_visited : dict
        A dictionary mapping board representations to corresponding Node objects.
    path : list
        A list tracking the sequence of (Node, player) tuples visited during the current simulation.
    c : float
        The exploration parameter for the UCT formula.

    Note
    ----
    This function attempts to choose and play a move based on the UCT strategy. If no move can be played (e.g., the game is over), the function has no effect. It handles exceptions gracefully, ensuring the simulation can continue even if an unexpected state is encountered.
    """
    
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
    """
    Backpropagates the result of a simulation up the tree.

    Parameters
    ----------
    path : list
        The path of nodes visited in the simulation.
    winner : int
        The outcome of the game (-1 for O wins, 1 for X wins, 0 for draw).
    """
    
    for i in range(len(path)-1, -1, -1):
        node, player = path[i]
        node.update(player, winner)
            
    
def make_complete_simulation(board, player, dic_nodes_visited, c):
    """
    Completes a single simulation from the current state until the game ends.

    Parameters
    ----------
    board : Board
        A copy of the board to simulate the game on.
    player : int
        The player who is currently to move.
    dic_nodes_visited : dict
        A dictionary of nodes visited during simulations.
    c : float
        The exploration parameter for UCT.
    """
    
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
    """
    Performs Monte Carlo Tree Search to determine and play the best move.

    Parameters
    ----------
    board : Board
        The current game board.
    player : int
        The current player making the move.
    nb_simulations : int
        The number of simulations to run for the MCTS.
    c : float, optional
        The exploration parameter for UCT. Defaults to the square root of 2.

    Returns
    -------
    dict
        A dictionary of visited nodes after the simulations.

    Side effects
    -------------
    Updates the board with the best move determined by the MCTS.
    """
    
    dic_nodes_visited = {}
    
    for i in range(nb_simulations):
        copy_board = board.copy()
        make_complete_simulation(copy_board, player, dic_nodes_visited, c)
    
    (i, j, node) = choose_node_winrate(board, player, dic_nodes_visited)
    board.play(i, j, player)
    return dic_nodes_visited