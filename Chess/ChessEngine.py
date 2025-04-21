"""
This class is responsible for storing all the information about the current state of a chess game.
It will also be responsible for determining the valid moves at the current state.
It will also keep a move log.
"""


class GameState:
    def __init__(self):
        # The board is an 8x8 2D list, each element of the list has 2 characters.
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
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.en_passant_possible = ()  # Coordinates for the square en passant capture are possible.
        self.castling_rights = Castling(True, True, True, True)
        self.castling_log = [
            Castling(
                self.castling_rights.white_king_side,
                self.castling_rights.black_king_side,
                self.castling_rights.white_queen_side,
                self.castling_rights.black_queen_side,
            )
        ]

    """
    Takes a move as a parameter and executes it.
    """

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)  # Log the move so we can undo it.
        self.white_to_move = not self.white_to_move  # Swap players.

        # Update the king's location if it's moved.
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)

        # Pawn promotion.
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

        # En passant move.
        if move.is_en_passant_move:
            self.board[move.start_row][move.end_col] = "--"  # Capturing the pawn.

        #  Update en_passant_possible variable.
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:  # Only on 2 square pawn advances.
            self.en_passant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.en_passant_possible = ()

        # Castling.
        if move.is_castling_move:
            if move.end_col - move.start_col == 2:  # Kingside castling.
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = "--"  # Erase the old rook.
            else:  # Queenside castling.
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = "--"  # Erase the old rook.

        # Update castling rights when it's rook or a king moves.
        self.update_castling(move)
        self.castling_log.append(
            Castling(
                self.castling_rights.white_king_side,
                self.castling_rights.black_king_side,
                self.castling_rights.white_queen_side,
                self.castling_rights.black_queen_side,
            )
        )

    """
    Undo the last move made.
    """

    def undo_move(self):
        if len(self.move_log) != 0:  # Make sure that there is a move to undo.
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move  # Swap players.

            # Update the king's location if it's moved.
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)

            # Undo en passant move.
            if move.is_en_passant_move:
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.en_passant_possible = (move.end_row, move.end_col)

            # Undo a 2 square pawn advance.
            if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
                self.en_passant_possible = ()

            # Undo castling rights.
            self.castling_log.pop()  # Removing the last undoing element.

            # Set the current castling rights to the last castling rights before the move was made.
            new_castling_right = self.castling_log[-1]
            self.castling_rights = Castling(
                new_castling_right.white_king_side,
                new_castling_right.black_king_side,
                new_castling_right.white_queen_side,
                new_castling_right.black_queen_side,
            )

            #  Undo castling.
            if move.is_castling_move:
                if move.end_col - move.start_col == 2:  # Kingside castling.
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = "--"
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = "--"

    """
    Update castling rights based on the current position of the pieces.
    """

    def update_castling(self, move):
        if move.piece_moved == "wK":
            self.castling_rights.white_king_side = False
            self.castling_rights.white_queen_side = False
        elif move.piece_moved == "bK":
            self.castling_rights.black_king_side = False
            self.castling_rights.black_queen_side = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:  # Where the white pieces start.
                if move.start_col == 0:  # Left rook.
                    self.castling_rights.white_queen_side = False
                elif move.start_col == 7:  # Right rook.
                    self.castling_rights.white_king_side = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:  # Where the black pieces start.
                if move.start_col == 0:  # Left rook.
                    self.castling_rights.black_queen_side = False
                elif move.start_col == 7:  # Right rook.
                    self.castling_rights.black_king_side = False

    """
    All moves considering checks.
    """

    def get_valid_moves(self):
        temp_en_passant_possible = self.en_passant_possible
        temp_castling_rights = Castling(
            self.castling_rights.white_king_side,
            self.castling_rights.black_king_side,
            self.castling_rights.white_queen_side,
            self.castling_rights.black_queen_side,
        )
        # 1) Generate all possible moves.
        moves = self.get_all_possible_moves()
        if self.white_to_move:
            self.get_castling_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castling_moves(self.black_king_location[0], self.black_king_location[1], moves)

        # 2) For each move, make the move.
        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])
            # 3) Generate all opponent's moves.
            # 4) For each of your opponent's moves, see if they attack your king.
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i])  # 5) If they do attack your king, not a valid move.
            self.white_to_move = not self.white_to_move
            self.undo_move()

        if len(moves) == 0:  # Either checkmate or stalemate.
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.en_passant_possible = temp_en_passant_possible
        self.castling_rights = temp_castling_rights
        return moves

    """
    Determine if the current player is in check.
    """

    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    """
    Determine if the enemy can attack the square r, c.
    """

    def square_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move  # Switch to an opponent's turn.
        opponent_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move  # Switch to turn back.
        for move in opponent_moves:
            if move.end_row == r and move.end_col == c:  # Square is under attack.
                return True
        return False

    """
    All moves without considering checks.
    """

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):  # Number of rows.
            for c in range(len(self.board[r])):  # Number of columns in a given row.
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c,
                                               moves)  # Calls the appropriate move function based on a piece type.
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
                elif (r - 1, c - 1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, is_en_passant_move=True))
            if c + 1 <= 7:  # Captures to the right.
                if self.board[r - 1][c + 1][0] == "b":  # Enemy piece to capture.
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, is_en_passant_move=True))

        else:  # Black pawn moves.
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            # Captures for black
            if c - 1 >= 0:  # Captures to the left.
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, is_en_passant_move=True))
            if c + 1 <= 7:  # Captures to the right.
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, is_en_passant_move=True))

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

    """
    Generate all valid castling moves for the king at (r, c) and add them to the list.).
    """

    def get_castling_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return  # Castling is illegal.
        if ((self.white_to_move and self.castling_rights.white_king_side) or
                (not self.white_to_move and self.castling_rights.black_king_side)):
            self.get_king_side_castling_moves(r, c, moves)
        if ((self.white_to_move and self.castling_rights.white_queen_side) or
                (not self.white_to_move and self.castling_rights.black_queen_side)):
            self.get_queen_side_castling_moves(r, c, moves)

    """
    Additional function for get_castling_moves that generates king-side castling moves and checks if they are legal.
    """

    def get_king_side_castling_moves(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.square_under_attack(r, c + 1) and not self.square_under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, is_castling_move=True))

    """
    Additional function for get_castling_moves that generates queen-side castling moves and checks if they are legal.
    """

    def get_queen_side_castling_moves(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.square_under_attack(r, c - 1) and not self.square_under_attack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castling_move=True))


class Move:
    # Maps keys to values
    # key : value
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board, is_en_passant_move=False,
                 is_castling_move=False):
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = (self.piece_moved == "wp" and self.end_row == 0) or (
                self.piece_moved == "bp" and self.end_row == 7)
        # En passant.
        self.is_en_passant_move = is_en_passant_move
        if self.is_en_passant_move:
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"

        # Castling.
        self.is_castling_move = is_castling_move

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


class Castling:
    def __init__(self, white_king_side, black_king_side, white_queen_side, black_queen_side):
        self.white_king_side = white_king_side
        self.black_king_side = black_king_side
        self.white_queen_side = white_queen_side
        self.black_queen_side = black_queen_side
