"""
This class is responsible for storing all the information about the current state of a chess game.
It will also be responsible for determining the valid moves at the current state.
It will also keep a move log.
"""


class GameState:
    def __init__(self):
        # The board is a 8x8 2D list, each element of the list has 2 characters.
        # The first character represents the color of the piece, 'b' or 'w'.
        # The second character represents the type of the piece, 'K', 'Q', 'R', 'B', 'N' or 'P'.
        # "--" represents an empty space with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.white_to_move = True
        self.move_log = []

    """
    Takes a move as a parameter and executes it.
    """

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)  # Log the move so we can undo it later.
        self.white_to_move = not self.white_to_move  # Swap players.

    """
    Undo the last move made.
    """

    def undo_move(self):
        if len(self.move_log) != 0:  # Make sure that there is a move to undo.
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move  # Swap players.

    """
    All moves considering checks.
    """

    def get_valid_moves(self):
        return self.get_all_possible_moves()

    """
    All moves without considering checks.
    """

    def get_all_possible_moves(self):
        moves = [Move((6, 4), (4, 4), self.board)]
        for r in range(len(self.board)):  # Number of rows.
            for c in range(len(self.board[r])):  # Number of columns in given row.
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_to_move) and (turn == "b" and not self.white_to_move):
                    piece = self.board[r][c][1]
                    if piece == "p":
                        self.get_pawn_moves(r, c, moves)
                    elif piece == "R":
                        self.get_rook_moves(r, c, moves)
        return moves

    """
    Get all the pawn moves for the pawn located at row and column and add these moves to the list.
    """

    def get_pawn_moves(self, r, c, moves):
        pass

    """
    Get all the rook moves for the rook located at row and column and add these moves to the list.
    """

    def get_rook_moves(self, r, c, moves):
        pass


class Move:
    # Maps keys to values
    # key : value
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board):
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        print(self.move_ID)

    """
    Overriding the equals method.
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False


    def get_chess_notation(self):
        #  It makes real chess notation.
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
