"""
This is our main driver file.
It will be responsible for handling user input and displaying the current GameState object.
"""

import pygame as p
from Chess import ChessEngine

WIDTH = HEIGHT = 512  # 400 is another option
DIMENSION = 8  # Dimensions of a chess board
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # For animations later on
IMAGES = {}

"""
Initialize a global dictionary of images. This will be called exactly once in the main.
"""


def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK",
              "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))
        # Note: we can access an image by saying 'IMAGES['wp']'


"""
The main driver for our code. This will handle the user input and updating the graphics.
"""


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    game_state = ChessEngine.GameState()
    valid_moves = game_state.get_valid_moves()
    move_made = False  # When a move is made.

    load_images()  # Only do this once, before the while loop
    running = True
    square_selected = ()  # No square is selected initially, keep track of the last click of the user (tuple: row, col).
    player_clicks = []  # Keep track of player clicks (2 tuples: [(6, 4), (4, 4)])

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse handler.
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x, y) location of the mouse.
                col = location[0] // SQUARE_SIZE
                row = location[1] // SQUARE_SIZE

                if square_selected == (row, col):  # It means the user clicked the same square twice.
                    square_selected = ()  # Deselects the square.
                    player_clicks = []  # Clean player clicks.
                else:
                    square_selected = (row, col)
                    player_clicks.append(square_selected)  # Append for both 1st and 2nd clicks.

                if len(player_clicks) == 2:  # After 2nd click.
                    move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                    if move in valid_moves:
                        game_state.make_move(move)
                        move_made = True
                    square_selected = ()  # Reset user clicks.
                    player_clicks = []
            # Key handlers.
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo when 'z' is pressed
                    game_state.undo_move()
                    move_made = True

        if move_made:
            valid_moves = game_state.get_valid_moves()
            move_made = False

        draw_game_state(screen, game_state)
        clock.tick(MAX_FPS)
        p.display.flip()


"""
Responsible for all the graphics within a current game state.
"""


def draw_game_state(screen, game_state):
    draw_board(screen)  # Draw squares on the board
    # Add in piece highlighting or move suggestions (later)
    draw_pieces(screen, game_state.board)  # Draw pieces on top of those squares


"""
Draw the squares on the board. The top left square is always light.
"""


def draw_board(screen):
    colors = [p.Color("#F0D9B5"), p.Color("#B58863")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


"""
Draw the pieces on the board using the current GameState.board.
"""


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # Not empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


if __name__ == "__main__":
    main()
