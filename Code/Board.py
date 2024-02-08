from enum import Enum
from copy import deepcopy

class direction(Enum):
    ROW = 1
    COL = 2
    DIAG_TOP_BOTTOM = 3
    DIAG_BOTTOM_TOP = 4

class Board:
    """
    Players:
        1 = player X
        -1 = player O

    Game State:
        0 and 9 moves played: draw
        -1: player O wins the game
        1: player X wins the game
    """

    def __init__(self):
        """
        Initializes a new Tic-Tac-Toe board with an empty grid, list of moves, game state, winning move, and available moves.
        """
        
        self.grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.moves = []
        self.gameState = 0
        self.winningMove = None
        self.available_moves = set([(i, j) for i in range(3) for j in range(3)])
        
    def copy(self):
        """
        Creates a deep copy of the current board state, including the grid, moves, game state, winning move, and available moves.

        Returns:
            Board: A new Board instance with the copied state.
        """
        
        board_copy = Board()
        board_copy.grid = deepcopy(self.grid)
        board_copy.moves = deepcopy(self.moves)
        board_copy.gameState = self.gameState    
        board_copy.winningMove = self.winningMove 
        board_copy.available_moves = self.available_moves.copy()   
        return board_copy

    def display_cell(self, i, j):
        """
        Prints the content of a specified cell on the board. Displays 'X', 'O', or an empty space accordingly.

        Parameters:
            i (int): The row index of the cell.
            j (int): The column index of the cell.
        """
        
        if self.grid[i][j] == 0:
            print('   ', end = '')
        elif self.grid[i][j] == 1:
            print(' X ', end = '')
        else:
            print(' O ', end = '')

    def display(self, addSpace=False):
        """
        Displays the entire board state in the console, with optional spacing after the board.

        Parameters:
            addSpace (bool): If True, adds an extra newline after displaying the board. Default is False.
        """
        
        for i in range(3):
            for j in range(3):
                self.display_cell(i, j)
                if j < 2:
                    print('|', end='')
                else:
                    print()
            if i < 2:
                print('-----------')
        if addSpace:
            print()

    def display_player_name(self, player):
        """
        Returns the display name of the player ('X' or 'O') based on the player's identifier.

        Parameters:
            player (int): The player identifier (1 for 'X', -1 for 'O').

        Returns:
            str: The display name of the player.
            """
            
        if player == 1:
            return "X"
        return "O"

    def updateGameState(self, i, j, player):
        """
        Updates the game state after a move. Checks if the move leads to a win or continues the game.

        Parameters:
            i (int): The row index of the last move.
            j (int): The column index of the last move.
            player (int): The identifier of the player who made the last move.
        """
        
        if len(self.moves) > 9 or self.gameState != 0:
            pass
        else:
            #check if the player has won on the row
            if self.playerWins_row(i, j, player):
                self.gameState = player
                self.winningMove = ((i, j), direction.ROW) 
                return
            if self.playerWins_column(i, j, player):
                self.gameState = player
                self.winningMove = ((i, j), direction.COL) 
                return
            
            won_on_diagonal = self.playerWins_diag(player)
            if won_on_diagonal[0]:
                self.gameState = player
                if won_on_diagonal[1] == 1:
                    dir = direction.DIAG_TOP_BOTTOM
                else:
                    dir = direction.DIAG_BOTTOM_TOP
                self.winningMove = ((i, j), dir)

    def playerWins_row(self, i, j, player):
        """
        Checks if a player wins by completing a row.

        Parameters:
            i (int): The row index of the last move.
            j (int): The column index of the last move.
            player (int): The identifier of the player who made the last move.

        Returns:
            bool: True if the player wins by completing a row, False otherwise.
        """
        
        if j == 0:
            return self.grid[i][j+1] == self.grid[i][j+2] == player
        if j == 1:
            return self.grid[i][j-1] == self.grid[i][j+1] == player
        return self.grid[i][j-2] == self.grid[i][j-1] == player

    def playerWins_column(self, i, j, player):
        """
        Checks if a player wins by completing a column.

        Parameters:
            i (int): The row index of the last move.
            j (int): The column index of the last move.
            player (int): The identifier of the player who made the last move.

        Returns:
            bool: True if the player wins by completing a column, False otherwise.
        """
        
        if i == 0:
            return self.grid[i+1][j] == self.grid[i+2][j] == player
        if i == 1:
            return self.grid[i-1][j] == self.grid[i+1][j] == player
        return self.grid[i-1][j] == self.grid[i-2][j] == player

    def playerWins_diag(self, player):
        """
        Checks if a player wins by completing a diagonal.

        Parameters:
            player (int): The identifier of the player.

        Returns:
            tuple: A tuple containing a boolean indicating if a player wins and an integer indicating which diagonal (1 for top-bottom, 2 for bottom-top).
        """
        
        if self.grid[0][0] == self.grid[1][1] == self.grid[2][2] == player:
            #diagonal from top right corner to bottom left corner
            return (True, 1)
        return (self.grid[0][2] == self.grid[1][1] == self.grid[2][0] == player, 2)

    def play(self, i, j, player):
        """
        Plays a move on the board, updating the grid, moves, and game state.

        Parameters:
            i (int): The row index for the move.
            j (int): The column index for the move.
            player (int): The identifier of the player making the move.

        Raises:
            Exception: If the game is over or the cell is not empty.
        """
        
        if self.gameState != 0 or len(self.moves) >= 9:
            text = "The game is a draw." if self.gameState == 0 else f"Player {self.display_player_name(self.gameState)} has won."
            raise Exception(text)
        elif self.grid[i][j] == 0:
            if len(self.moves) != 0 and self.moves[-1][2] == player:
                players_turn = 1 if player == -1 else -1
                raise Exception(f"It's player {self.display_player_name(players_turn)}'s turn to play.")
            else:
                self.grid[i][j] = player
                self.moves.append((i, j, player))
                self.updateGameState(i, j, player)
                self.available_moves.remove((i, j))
        else:
            raise Exception(f"Cell [{i}, {j}] is not empty.")
        
    def undo_last_move(self, return_move=False):
        """
        Undoes the last move made on the board, reverting the game state accordingly.

        Parameters:
            return_move (bool): If True, returns the last move made. Default is False.

        Returns:
            tuple: The last move made (i, j, player) if return_move is True. Otherwise, nothing is returned.
        """
        
        if len(self.moves) == 0:
            return
        
        (i, j, player) = self.moves.pop()
        self.grid[i][j] = 0
        self.gameState = 0  # undoing the last move necessarily makes it so that the game cannot be over
        self.winningMove = None
        self.available_moves.add((i, j))
        
        if return_move:
            return (i, j, player)
        
    def get_square_representation(self, i, j):
        """
        Returns a string representation of a cell's content.

        Parameters:
            i (int): The row index of the cell.
            (int): The column index of the cell.

        Returns:
            str: The content of the cell represented as 'X', 'O', or '*' for an empty cell.
        """
        
        if self.grid[i][j] == 0:
            return '*'
        if self.grid[i][j] == 1:
            return 'X'
        return 'O'
        
    def get_representation(self):
        """
        Generates a string representation of the entire board state, useful for debugging or logging.

        Returns:
            str: A string representing the board's current state, with 'X', 'O', and '*' for empty spaces.
        """

        representation = ''
        for i in range(3):
            for j in range(3):
                representation += self.get_square_representation(i, j)
        return representation
    
    def isGameOver(self):
        """
        Checks if the game is over, either because a player has won or all cells are filled (draw).

        Returns:
            bool: True if the game is over, False otherwise.
        """
        
        return self.gameState != 0 or (self.gameState == 0 and len(self.moves) >= 9)