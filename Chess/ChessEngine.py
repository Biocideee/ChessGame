from tkinter import messagebox


class GameState:
    """
    This class is responsible for storing all the information about the current state of a chess game.
    It's also responsible for determining the valid moves at the current state.
    It's also keeping a move log.
    """

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
        self.redo_log = []
        self.white_king_location = (7, 4)  # Initial coordinates of the white king.
        self.black_king_location = (0, 4)  # Initial coordinates of the black king.
        self.checkmate = False
        self.stalemate = False
        self.draw = False
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
        self.pawn_promotion = False
        self.promotion_square = ()
        self.promotion_piece_color = None

    def make_move(self, move):
        """
        Takes a move as a parameter and executes it.
        """
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
            if move.promotion_piece:  # If promotion_piece is provided, it's a normal promotion.
                promoted_piece = move.piece_moved[0] + move.promotion_piece
                self.board[move.end_row][move.end_col] = promoted_piece
                move.piece_promoted = promoted_piece
            else:
                self.pawn_promotion = True
                self.promotion_square = (move.end_row, move.end_col)
                self.promotion_piece_color = move.piece_moved[0]
            return  # End the move function after handling promotion

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

        # Update castling rights when it's a rook or a king moves.
        self.update_castling(move)
        self.castling_log.append(
            Castling(
                self.castling_rights.white_king_side,
                self.castling_rights.black_king_side,
                self.castling_rights.white_queen_side,
                self.castling_rights.black_queen_side,
            )
        )

    def undo_move(self, add_to_redo=True):
        """
        Undo the last move made.
        """
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
            if self.castling_log:
                self.castling_log.pop()  # Removing the last undoing element.

                # Set the current castling rights to the last castling rights before the move was made.
                if self.castling_log:
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

            #  Add the move to the redo log so you can move forward.
            if add_to_redo:
                self.redo_log.append(move)

            #  Reset the pawn promotion.
            if move.is_pawn_promotion:
                self.pawn_promotion = False
                self.promotion_square = ()

    def redo_move(self):
        """
        Redo the last undo move.
        """
        if len(self.redo_log) != 0:
            self.make_move(self.redo_log.pop())

    def update_castling(self, move):
        """
        Update castling rights based on the current position of the pieces.
        """
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

    def get_valid_moves(self):
        """
        All moves considering checks.
        """
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
            self.undo_move(add_to_redo=False)

        if len(moves) == 0:  # Either checkmate or stalemate.
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        if self.check_for_draw():
            self.draw = True
        else:
            self.draw = False

        self.en_passant_possible = temp_en_passant_possible
        self.castling_rights = temp_castling_rights
        return moves

    def in_check(self):
        """
        Determine if the current player is in check.
        """
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, r, c):
        """
        Determine if the enemy can attack the square r, c.
        """
        self.white_to_move = not self.white_to_move  # Switch to an opponent's turn.
        opponent_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move  # Switch to turn back.
        for move in opponent_moves:
            if move.end_row == r and move.end_col == c:  # Square is under attack.
                return True
        return False

    def get_all_possible_moves(self):
        """
        All moves without considering checks.
        """
        moves = []
        for r in range(len(self.board)):  # Number of rows.
            for c in range(len(self.board[r])):  # Number of columns in a given row.
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c,
                                               moves)  # Calls the appropriate move function based on a piece type.
        return moves

    def get_pawn_moves(self, r, c, moves):
        """
        Get all the pawn moves for the pawn located at row and column and add these moves to the list.
        """
        if self.white_to_move:  # White pawn moves.
            if r - 1 >= 0:
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
            if r + 1 <= 7:
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

    def get_rook_moves(self, r, c, moves):
        """
        Get all the rook moves for the rook located at row and column and add these moves to the list.
        """
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

    def get_knight_moves(self, r, c, moves):
        """
        Get all the knight moves for the knight located at row and column and add these moves to the list.
        """
        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = "w" if self.white_to_move else "b"

        for direction in directions:
            end_row = r + direction[0]
            end_col = c + direction[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # Enemy piece valid.
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        """
        Get all the bishop moves for the bishop located at row and column and add these moves to the list.
        """
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

    def get_queen_moves(self, r, c, moves):
        """
        Get all the queen moves for the queen located at row and column and add these moves to the list.
        """
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        """
        Get all the king moves for the king located at row and column and add these moves to the list.
        """
        directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        ally_color = "w" if self.white_to_move else "b"

        for i in range(8):
            end_row = r + directions[i][0]
            end_col = c + directions[i][1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_castling_moves(self, r, c, moves):
        """
        Generate all valid castling moves for the king at (r, c) and add them to the list.).
        """
        if self.square_under_attack(r, c):
            return  # Castling is illegal.
        if ((self.white_to_move and self.castling_rights.white_king_side) or
                (not self.white_to_move and self.castling_rights.black_king_side)):
            self.get_king_side_castling_moves(r, c, moves)
        if ((self.white_to_move and self.castling_rights.white_queen_side) or
                (not self.white_to_move and self.castling_rights.black_queen_side)):
            self.get_queen_side_castling_moves(r, c, moves)

    def get_king_side_castling_moves(self, r, c, moves):
        """
        Additional function for get_castling_moves that generates king-side castling moves and checks if they are legal.
        """
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.square_under_attack(r, c + 1) and not self.square_under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, is_castling_move=True))

    def get_queen_side_castling_moves(self, r, c, moves):
        """
        Additional function for get_castling_moves
        that generates queen-side castling moves and checks if they are legal.
        """
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.square_under_attack(r, c - 1) and not self.square_under_attack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castling_move=True))

    def check_for_draw(self):
        """
        Checks for insufficient material for a draw.
        Simplified version: K vs K, K vs KN, K vs KB.
        More complex rules exist but are omitted for simplicity.
        """
        pieces_on_board = []

        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                if piece != "--":
                    pieces_on_board.append(piece)

        if len(pieces_on_board) == 2:
            return True  # Only Kings left.

        if len(pieces_on_board) == 3:
            # Find the non-king piece.
            non_king_piece = ""
            for piece in pieces_on_board:
                if piece[1] != "K":
                    non_king_piece = piece[1]
                    break
            if non_king_piece == "N" or non_king_piece == "B":
                return True  # King vs King and Knight or King vs King and Bishop.

        if len(pieces_on_board) == 4:
            white_bishops = []
            black_bishops = []
            for r in range(len(self.board)):
                for c in range(len(self.board[r])):
                    piece = self.board[r][c]
                    if piece == "wB":
                        white_bishops.append((r, c))
                    elif piece == "bB":
                        black_bishops.append((r, c))
                    if len(white_bishops) == 1 or len(black_bishops) == 1:
                        # Check if bishops are on the same colored squares
                        white_bishop_color = (white_bishops[0][0] + white_bishops[0][1]) % 2
                        black_bishop_color = (black_bishops[0][0] + black_bishops[0][1]) % 2
                        if white_bishop_color == black_bishop_color:
                            return True  # King and Bishop vs King and Bishop on the same colored squares.

        return False

    def save_game_state(self, filename="saved_game.txt"):
        """
        A function that saves the game state (move log, en passant, castling rights, promotion) to a file.
        """
        with open(filename, "w") as file:
            file.write("# Chess Game Save File\n")
            for move in self.move_log:
                notation = move.get_chess_notation()
                if move.is_en_passant_move:
                    notation += " ep"
                elif move.is_castling_move:
                    notation += " castle"

                # Detect pawn promotion.
                if move.piece_moved[1] == "p" and (move.end_row == 0 or move.end_row == 7):
                    promoted_to = move.promotion_piece
                    notation += f" promotion={promoted_to}"

                file.write(f"{notation}\n")

    @staticmethod
    def load_game_state(filename="saved_game.txt"):
        """
        A function that loads the game state from a file by replaying the move log.
        """
        with open(filename, "r") as file:
            lines = [line.strip() for line in file.readlines() if line.strip() and not line.startswith('#')]

        game_state = GameState()
        redo_log = []

        for notation_with_flags in lines:
            notation_parts = notation_with_flags.split()
            notation = notation_parts[0]
            promotion_piece = None

            for part in notation_parts[1:]:
                if part.startswith("promotion="):
                    promotion_piece = part.split("=")[1]

            if len(notation) == 4:
                start_sq, end_sq = Move.get_row_col_from_notation(notation)
                possible_moves = game_state.get_valid_moves()

                for move in possible_moves:
                    if (move.start_row == start_sq[0] and move.start_col == start_sq[1] and
                            move.end_row == end_sq[0] and move.end_col == end_sq[1]):

                        if promotion_piece:
                            move.promotion_piece = promotion_piece
                            move.piece_moved = move.piece_moved[0] + "p"
                            move.piece_captured = game_state.board[move.end_row][
                                move.end_col]
                            move.piece_promoted = move.piece_moved[0] + promotion_piece

                        game_state.make_move(move)
                        break
                else:
                    messagebox.showerror("Invalid move", f"Invalid move found in save file: {notation_with_flags}")

            elif notation_with_flags:
                messagebox.showerror("Invalid notation format",
                                     f"Warning: Invalid notation format in save file: {notation_with_flags}")
        return game_state


class Move:
    """
    This class represents a move.
    """
    # Match keys to values
    # key : value
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board, is_en_passant_move=False,
                 is_castling_move=False, promotion_piece=None):
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        # Pawn promotion.
        self.is_pawn_promotion = (self.piece_moved == "wp" and self.end_row == 0) or (
                self.piece_moved == "bp" and self.end_row == 7)
        self.promotion_piece = promotion_piece

        # En passant.
        self.is_en_passant_move = is_en_passant_move
        if self.is_en_passant_move:
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"

        # Castling.
        self.is_castling_move = is_castling_move

        self.is_capture = self.piece_captured != "--"
        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

        # Pawn promotion.

    def __eq__(self, other):
        """
        Overriding the equals' method.
        """
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False

    def __str__(self):
        """
        Overriding the str's method.
        """
        # Castling.
        if self.is_castling_move:
            return "O-O" if self.end_col == 6 else "O-O-O"
        end_square = self.get_rank_file(self.end_row, self.end_col)
        # Pawn moves.
        if self.piece_moved[1] == "p":
            if self.is_capture:
                return self.cols_to_files[self.start_col] + "x" + end_square
            else:
                return end_square
        # Pawn promotions.
        if self.is_pawn_promotion:
            if self.is_capture:
                return self.piece_moved[1] + "q" + end_square
            else:
                return self.piece_moved[1] + end_square
        # Piece moves.
        move_str = self.piece_moved[1]
        if self.is_capture:
            move_str += "x"
        return move_str + end_square

    def get_chess_notation(self):
        """
        A function that makes real chess notation.
        """
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        """
        A function that converts row and column to a rank file notation.
        """
        return self.cols_to_files[c] + self.rows_to_ranks[r]

    @staticmethod
    def get_row_col_from_notation(notation):
        """
        Helper function to get (row, col) from chess notation (e.g., 'e2e4').
        """
        start_file, start_rank, end_file, end_rank = notation
        start_row = Move.ranks_to_rows[start_rank]
        start_col = Move.files_to_cols[start_file]
        end_row = Move.ranks_to_rows[end_rank]
        end_col = Move.files_to_cols[end_file]
        return (start_row, start_col), (end_row, end_col)


class Castling:
    """
    A function that stores the castling rights of a player.
    """

    def __init__(self, white_king_side, black_king_side, white_queen_side, black_queen_side):
        self.white_king_side = white_king_side
        self.black_king_side = black_king_side
        self.white_queen_side = white_queen_side
        self.black_queen_side = black_queen_side
