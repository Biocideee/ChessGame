"""
This is our main driver file.
It will be responsible for handling user input and displaying the current GameState object.
"""

import pygame as p
from Chess import ChessEngine
from tkinter import messagebox

# Size constants.
WIDTH = HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = HEIGHT / 2
DIMENSION = 8  # Dimensions of a chess board.
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60  # For animations.

# Color constants.
LIGHT_SQUARE_COLOR = p.Color("#edd6b0")
DARK_SQUARE_COLOR = p.Color("#b88762")
HIGHLIGHT_COLOR = p.Color("#fae623")
MOVE_HIGHLIGHT_COLOR = p.Color("#f6ea70")
MOVE_LOG_BACKGROUND_COLOR = p.Color("#2f2e2b")
GAME_INFO_BACKGROUND_COLOR = p.Color("#2f2e2b")
TEXT_COLOR = p.Color("white")
BORDER_COLOR = p.Color("#252422")
BUTTON_HOVER_COLOR = p.Color("#444340")

IMAGES = {}


def load_images():
    """
    Initialize a global dictionary of images. This will be called exactly once in the main.
    """
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK",
              "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.smoothscale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))
        # Note: we can access an image by saying 'IMAGES['wp'].


def draw_board(screen):
    """
    Draw the squares on the board. The top left square is always light.
    """
    global colors
    colors = [LIGHT_SQUARE_COLOR, DARK_SQUARE_COLOR]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def highlight_moves(screen, game_state, valid_moves, square_selected):
    """
    Highlighting moves for the current piece selected.
    """
    if square_selected != ():
        r, c = square_selected
        if game_state.board[r][c][0] == ("w" if game_state.white_to_move else "b"):  # Square_selected is a valid piece.

            # Highlight a selected square.
            surface = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            surface.set_alpha(100)  # 0 is transparent, 255 is no transparent.
            surface.fill(HIGHLIGHT_COLOR)
            screen.blit(surface, (c * SQUARE_SIZE, r * SQUARE_SIZE))

            # Highlight moves of a selected square.
            surface.fill(MOVE_HIGHLIGHT_COLOR)
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(surface, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))

    if game_state.in_check():
        king_location = game_state.get_king_location()
        if king_location:
            # Highlight the king if in check.
            surface = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            surface.set_alpha(100)
            kr, kc = king_location
            surface.fill("red")
            screen.blit(surface, (kc * SQUARE_SIZE, kr * SQUARE_SIZE))


def draw_pieces(screen, board):
    """
    Draw the pieces on the board using the current GameState.board.
    """
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # Not an empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_move_log_panel(screen, game_state, font, offset):
    """
    Draws the move log panel.
    """
    move_log_rect = p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, MOVE_LOG_BACKGROUND_COLOR, move_log_rect)
    move_log = game_state.move_log
    move_text_list = []
    for i in range(0, len(move_log), 2):
        move_str = str(i // 2 + 1) + ". " + str(move_log[i]) + "    "
        if i + 1 < len(move_log):  # Make sure black made a move.
            move_str += str(move_log[i + 1]) + " "
        move_text_list.append(move_str)

    padding = 10
    line_spacing = 2
    text_y = padding - offset
    for i in range(len(move_text_list)):
        text = move_text_list[i]
        text_surface = font.render(text, True, TEXT_COLOR)
        text_location = move_log_rect.move(padding, text_y + 25)
        screen.blit(text_surface, text_location)
        text_y += text_surface.get_height() + line_spacing

    # Rectangle that closes the gap from the top of the move log background so the text will not appear.
    draw_rects(screen, WIDTH + 5, 0, MOVE_LOG_PANEL_WIDTH - 10, 25, MOVE_LOG_BACKGROUND_COLOR)

    # Draw rectangles and texts on top of them.
    draw_rects(screen, WIDTH + 5, 5, MOVE_LOG_PANEL_WIDTH - 10, 25, BORDER_COLOR)
    draw_texts(screen, WIDTH + 85, 6, 0, 0, "Move log")


def draw_game_menu_panel(screen, game_state):
    """
    Draws the game info panel.
    """
    game_info_rect = p.Rect(WIDTH, MOVE_LOG_PANEL_HEIGHT, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, GAME_INFO_BACKGROUND_COLOR, game_info_rect)

    # Draw rectangles and texts on top of them.
    draw_rects(screen, WIDTH + 5, MOVE_LOG_PANEL_HEIGHT, MOVE_LOG_PANEL_WIDTH - 10, 25, BORDER_COLOR)
    draw_texts(screen, WIDTH + 80, MOVE_LOG_PANEL_HEIGHT, 0, 0, "Game menu")

    # Draw the save button rectangle.
    draw_rects(screen, WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 30, MOVE_LOG_PANEL_WIDTH - 20, 25, BORDER_COLOR)
    draw_texts(screen, WIDTH + 15, MOVE_LOG_PANEL_HEIGHT + 33, 0, 0, "Save game", 15)

    # Draw the load button rectangle.
    draw_rects(screen, WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 60, MOVE_LOG_PANEL_WIDTH - 20, 25, BORDER_COLOR)
    draw_texts(screen, WIDTH + 15, MOVE_LOG_PANEL_HEIGHT + 63, 0, 0, "Load game", 15)

    # Draw the move back button rectangle.
    draw_rects(screen, WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 90, (MOVE_LOG_PANEL_WIDTH / 2) - 10, 25, BORDER_COLOR)
    draw_texts(screen, WIDTH + 15, MOVE_LOG_PANEL_HEIGHT + 93, 0, 0, "Move back", 15)

    # Draw the move forward button rectangle.
    draw_rects(screen, WIDTH + (MOVE_LOG_PANEL_WIDTH / 2) + 5, MOVE_LOG_PANEL_HEIGHT + 90,
               (MOVE_LOG_PANEL_WIDTH / 2) - 15, 25, BORDER_COLOR)
    draw_texts(screen, WIDTH + (MOVE_LOG_PANEL_WIDTH / 2) + 8, MOVE_LOG_PANEL_HEIGHT + 93, 0, 0,
               "Move forward", 15)

    # Draw the reset button rectangle.
    draw_rects(screen, WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 120, MOVE_LOG_PANEL_WIDTH - 20, 25, BORDER_COLOR)
    draw_texts(screen, WIDTH + 15, MOVE_LOG_PANEL_HEIGHT + 123, 0, 0, "Reset game", 15)

    # Draw the exit the game button.
    draw_rects(screen, WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 150, MOVE_LOG_PANEL_WIDTH - 20, 25, BORDER_COLOR)
    draw_texts(screen, WIDTH + 15, MOVE_LOG_PANEL_HEIGHT + 153, 0, 0, "Exit game", 15)


def draw_texts(screen, left, top, width, height, text, size=18):
    """
    Draws the text and on the panels.
    """
    font = p.font.SysFont("Times New Roman", size, True, False)
    text_surface = font.render(text, False, TEXT_COLOR)
    text_location = p.Rect(left, top, width, height)
    p.draw.rect(screen, GAME_INFO_BACKGROUND_COLOR, text_location)
    screen.blit(text_surface, text_location)


def draw_rects(screen, left, top, width, height, color):
    """
    Draws the rectangles on the panels.
    """
    move_log_panel_rect = p.Rect(left, top, width, height)
    p.draw.rect(screen, color, move_log_panel_rect)


def draw_end_game_text(screen, text):
    """
    Draws the text so you can see the game is over.
    """
    font = p.font.SysFont("Broadway", 30, True, False)
    text_surface = font.render(text, False, TEXT_COLOR)
    text_location = (p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH / 2 - text_surface.get_width() / 2,
        HEIGHT / 2 - text_surface.get_height() / 2)
    )
    screen.blit(text_surface, text_location)
    text_surface = font.render(text, False, BORDER_COLOR)
    screen.blit(text_surface, text_location.move(1, 1))


def draw_game_state(screen, game_state, valid_moves, square_selected, move_log_font, move_log_offset):
    """
    Responsible for all the graphics within a current game state.
    """
    draw_board(screen)  # Draw squares on the board
    highlight_moves(screen,
                    game_state,
                    valid_moves,
                    square_selected)  # Draw highlighting on valid squares before pieces drawn.
    draw_pieces(screen, game_state.board)  # Draw pieces on top of those squares
    draw_move_log_panel(screen, game_state, move_log_font, move_log_offset)  # Draw move log panel.
    draw_game_menu_panel(screen, game_state)  # Draw the game info panel.


def animate_move(move, screen, board, clock):
    """
    Animating a move.
    """
    global colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 5  # Frames to move per square.
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        r, c = (move.start_row + d_row * frame / frame_count, move.start_col + d_col * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        # Erase the piece moved from its previous location.
        color = colors[((move.end_row + move.end_col) % 2)]
        end_square = p.Rect(move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)

        # Draw the captured piece onto the rectangle.
        if move.piece_captured != "--":
            screen.blit(IMAGES[move.piece_captured], end_square)

        # Draw the moving piece onto the rectangle.
        screen.blit(IMAGES[move.piece_moved], p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)  # 60 fps.


def save_game_state(game_state, filename="saved_game.txt"):
    """
    A function that saves the game state (move log, en passant, castling rights) to a file.
    """
    with open(filename, "w") as file:
        file.write("# Chess Game Save File\n")
        for move in game_state.move_log:
            notation = move.get_chess_notation()
            if move.is_en_passant_move:
                notation += " ep"
            elif move.is_castling_move:
                notation += " castle"
            file.write(f"{notation}\n")


def load_game_state(screen, clock, filename="saved_game.txt"):
    """
    A function that loads the game state from a file by replaying the move log.
    """
    with open(filename, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]

    game_state = ChessEngine.GameState()
    game_state.redo_log = []

    for notation_with_flags in lines:
        notation_parts = notation_with_flags.split()
        notation = notation_parts[0]
        if len(notation) == 4:
            start_sq, end_sq = ChessEngine.Move.get_row_col_from_notation(notation)
            possible_moves = game_state.get_valid_moves()

            for move in possible_moves:
                if move.start_row == start_sq[0] and move.start_col == start_sq[1] and \
                        move.end_row == end_sq[0] and move.end_col == end_sq[1]:
                    is_ep_flag = "ep" in notation_parts
                    is_castle_flag = "castle" in notation_parts
                    if move.is_en_passant_move == is_ep_flag and move.is_castling_move == is_castle_flag:
                        game_state.make_move(move)
                        # animate_move(game_state.move_log[-1], screen, game_state.board, clock)
                        break
            else:
                messagebox.showerror("Invalid move", f"Invalid move found in save file: {notation_with_flags}")
        elif notation_with_flags:
            messagebox.showerror("Invalid notation format",
                                 f"Warning: Invalid notation format in save file: {notation_with_flags}")
    return game_state


def main():
    """
    The main driver for our code. This will handle the user input and update the graphics.
    """
    p.init()
    p.display.set_caption(f"Pygame chess: White's turn")
    screen = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(TEXT_COLOR)
    move_log_font = p.font.SysFont("Times New Roman", 17, False, False)
    game_state = ChessEngine.GameState()
    valid_moves = game_state.get_valid_moves()
    move_made = False  # When a move is made.
    animate = False  # When we want to show the animation of a move.
    game_over = False  # When the game is over.
    load_images()  # Only do this once, before the while loop
    run = True

    # No square is selected initially, keep track of the last click of the user (tuple: row, col) 2.
    square_selected = ()
    player_clicks = []  # Keep track of player clicks (2 tuples: [(6, 4), (4, 4)])

    # Rectangles that create fields of press on buttons.
    save_button_rect = p.Rect(WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 30, MOVE_LOG_PANEL_WIDTH - 20, 25)
    load_button_rect = p.Rect(WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 60, MOVE_LOG_PANEL_WIDTH - 20, 25)
    move_back_button_rect = p.Rect(WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 90, (MOVE_LOG_PANEL_WIDTH / 2) - 10, 25)
    move_forward_button_rect = p.Rect(WIDTH + (MOVE_LOG_PANEL_WIDTH / 2) + 5, MOVE_LOG_PANEL_HEIGHT + 90,
                                      (MOVE_LOG_PANEL_WIDTH / 2) - 15, 25)
    reset_button_rect = p.Rect(WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 120, MOVE_LOG_PANEL_WIDTH - 20, 25)
    exit_button_rect = p.Rect(WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 150, MOVE_LOG_PANEL_WIDTH - 20, 25)

    # Constants for scrolling the move log panel.
    move_log_offset = 0
    scroll_speed = 20

    while run:
        for e in p.event.get():
            if e.type == p.QUIT:
                run = False
            # Mouse button handler.
            elif e.type == p.MOUSEBUTTONDOWN and e.button == 1:
                if not game_over:
                    location = p.mouse.get_pos()  # (x, y) location of the mouse.
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE

                    if square_selected == (row,
                                           col) or col >= 8:  # It means the user clicked the same square twice or the user clicked the mouse log.
                        square_selected = ()  # Deselects the square.
                        player_clicks = []  # Clean player clicks.
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)  # Append for both 1st and 2nd clicks.

                    if len(player_clicks) == 2:  # After 2nd click.
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.make_move(valid_moves[i])
                                game_state.redo_log = []
                                move_made = True
                                animate = True
                                square_selected = ()  # Reset user clicks.
                                player_clicks = []
                        if not move_made:
                            player_clicks = [square_selected]

                    if save_button_rect.collidepoint(location):
                        save_game_state(game_state)
                        draw_rects(screen, WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 30, MOVE_LOG_PANEL_WIDTH - 20, 25,
                                   TEXT_COLOR)
                        p.display.flip()
                        # p.time.delay(200)

                    if load_button_rect.collidepoint(location):
                        loaded_game_state = load_game_state(screen, clock)
                        if loaded_game_state:
                            game_state = loaded_game_state
                            valid_moves = game_state.get_valid_moves()  # Update valid moves after loading
                            move_made = True  # Force redraw
                            animate = False
                            square_selected = ()
                            player_clicks = []
                            move_log_offset = 0  # Reset move log scroll
                            draw_rects(screen, WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 60, MOVE_LOG_PANEL_WIDTH - 20, 25,
                                       TEXT_COLOR)
                            p.display.flip()

                    if move_back_button_rect.collidepoint(location):
                        if game_state.move_log:
                            game_state.undo_move()
                            move_made = True
                            animate = False
                            game_over = False
                        draw_rects(screen, WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 90, (MOVE_LOG_PANEL_WIDTH / 2) - 10, 25,
                                   TEXT_COLOR)
                        p.display.flip()

                    if move_forward_button_rect.collidepoint(location):
                        if game_state.redo_log:
                            game_state.redo_move()
                            move_made = True
                            animate = True
                            game_over = False
                            draw_rects(screen, WIDTH + (MOVE_LOG_PANEL_WIDTH / 2) + 5, MOVE_LOG_PANEL_HEIGHT + 90,
                                       (MOVE_LOG_PANEL_WIDTH / 2) - 15, 25, TEXT_COLOR)
                            p.display.flip()

                    if reset_button_rect.collidepoint(location):
                        game_state = ChessEngine.GameState()
                        valid_moves = game_state.get_valid_moves()
                        square_selected = ()
                        player_clicks = []
                        move_made = False
                        animate = False
                        p.display.set_caption(f"Pygame chess: White's turn")
                        draw_rects(screen, WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 120, MOVE_LOG_PANEL_WIDTH - 20, 25,
                                   TEXT_COLOR)
                        p.display.flip()

                    if exit_button_rect.collidepoint(location):
                        draw_rects(screen, WIDTH + 10, MOVE_LOG_PANEL_HEIGHT + 150, MOVE_LOG_PANEL_WIDTH - 20, 25,
                                   TEXT_COLOR)
                        p.display.flip()
                        run = False

            # Mouse scroll handler.
            elif e.type == p.MOUSEWHEEL:
                location = p.mouse.get_pos()
                col = location[0] // SQUARE_SIZE
                row = location[1] // SQUARE_SIZE
                if col >= 8 and row <= 3:
                    move_log_offset -= scroll_speed * e.y
                    text_height = (len(game_state.move_log) // 2 + (1 if len(game_state.move_log) % 2 != 0 else 0)) * (
                            move_log_font.get_linesize() + 2) + 2 * 15
                    move_log_offset = max(0, min(move_log_offset,
                                                 text_height - MOVE_LOG_PANEL_HEIGHT if text_height > MOVE_LOG_PANEL_HEIGHT else 0))

        if move_made:
            if animate:
                animate_move(game_state.move_log[-1], screen, game_state.board, clock)

            turn = "White's turn" if game_state.white_to_move else "Black's turn"
            p.display.set_caption(f"Pygame chess: {turn}")

            valid_moves = game_state.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, game_state, valid_moves, square_selected, move_log_font, move_log_offset)

        if game_state.checkmate or game_state.stalemate:
            game_over = True
            draw_end_game_text(screen,
                               "Stalemate" if game_state.stalemate else "Black wins by checkmate" if game_state.white_to_move else "White wins by checkmate")

        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == "__main__":
    main()
