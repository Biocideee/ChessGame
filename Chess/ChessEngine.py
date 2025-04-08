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
        self.move_functions = {
            "p": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves,
            "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves
        }
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
        moves = []
        for r in range(len(self.board)):  # Number of rows.
            for c in range(len(self.board[r])):  # Number of columns in given row.
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)  # Calls the appropriate move function based on piece type.
        return moves

    """
    Get all the pawn moves for the pawn located at row and column and add these moves to the list.
    """

    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:  # White pawn moves.
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))

            # Captures for white
            if c - 1 >= 0:  # Captures to the left.
                if self.board[r - 1][c - 1][0] == "b":  # Enemy piece to capture.
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))

            if c + 1 <= 7:  # Captures to the right.
                if self.board[r - 1][c + 1][0] == "b":  # Enemy piece to capture.
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

        else:  # Black pawn moves.
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))

            # Captures for black
            if c - 1 >= 0:  # Captures to the left.
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))

            if c + 1 <= 7:  # Captures to the right.
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    """
    Get all the rook moves for the rook located at row and column and add these moves to the list.
    """

    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right.
        enemy_color = "b" if self.white_to_move else "w"

        for direction in directions:
            for i in range(1, 8):
                end_row = r + direction[0] * i
                end_col = c + direction[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # On board.
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # Empty space valid.
                        moves.append(Move((r, c), (end_row, end_col), self.board))

                    elif end_piece[0] == enemy_color:  # Enemy piece valid.
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:  # friendly piece invalid.
                        break
                else:  # Off board.
                    break

    """
    Get all the knight moves for the knight located at row and column and add these moves to the list.
    """

    def get_knight_moves(self, r, c, moves):
        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = "w" if self.white_to_move else "b"

        for direction in directions:
            end_row = r + direction[0]
            end_col = c + direction[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # Enemy piece valid.
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    """
    Get all the bishop moves for the bishop located at row and column and add these moves to the list.
    """

    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 diagonals.
        enemy_color = "b" if self.white_to_move else "w"

        for direction in directions:
            for i in range(1, 8):  # Bishop can move 7 squares max.
                end_row = r + direction[0] * i
                end_col = c + direction[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # On board.
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # Empty space valid.
                        moves.append(Move((r, c), (end_row, end_col), self.board))

                    elif end_piece[0] == enemy_color:  # Enemy piece valid.
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:  # friendly piece invalid.
                        break
                else:  # Off board.
                    break

    """
    Get all the queen moves for the queen located at row and column and add these moves to the list.
    """

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    """
    Get all the king moves for the king located at row and column and add these moves to the list.
    """

    def get_king_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        ally_color = "w" if self.white_to_move else "b"

        for i in range(8):
            end_row = r + directions[i][0]
            end_col = c + directions[i][1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))


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
