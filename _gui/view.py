"""
GUI view module
Contains the GameView class which handles rendering and user interaction
"""
import arcade
import time
from arcade import color as C
from _board.board import Board
from _enums.color import Color
from _enums.piece_type import PieceType
from _assets.spritesheet import Spritesheet, ChessSprites
from _game.game import Game
from _bot.bot import Bot
from pyglet.math import Vec2
from arcade.experimental.crt_filter import CRTFilter
import arcade.gui
import arcade.gui.widgets.layout
import arcade.gui.widgets.buttons
from arcade.gui import UIManager, UIFlatButton

#LIGHT_SQ = (240, 217, 181)
#DARK_SQ = (181, 136, 99)
LIGHT_SQ = (230, 225, 210)  
DARK_SQ = (200, 190, 170)
HIGHLIGHT_SQ = (118, 150, 86)
PREV_SQ = (125, 135, 150)
SIDEPANEL_BG = (50, 50, 50)
CLICK_SQ = (255, 165, 0)


def draw_board(board: Board, origin_x: int, origin_y: int, square: int, user_color: Color):
    """
    Draw the chess board with all tiles

    Args:
        board: The Board object to draw
        origin_x: X coordinate of board origin
        origin_y: Y coordinate of board origin
        square: Size of each square in pixels
        user_color: The color the user is playing (affects board orientation)
    """

    BORDER_1 = 0.07
    BORDER_2 = 0.14

    for rank in range(8):
        for file in range(8):
            # Transform coordinates based on user color
            if user_color == Color.BLACK:
                visual_file = 7 - file
                visual_rank = 7 - rank
            else:
                visual_file = file
                visual_rank = rank

            x = origin_x + visual_file * square
            y = origin_y + visual_rank * square
            fill = LIGHT_SQ if board.grid[rank][file].is_light_square else DARK_SQ
            alt = DARK_SQ if fill == LIGHT_SQ else LIGHT_SQ

            inner_1 = square * BORDER_1
            inner_2 = square * BORDER_2

            if board.grid[rank][file].prev:
                #arcade.draw_lbwh_rectangle_filled(x, y, square, square, PREV_SQ)
                alt = PREV_SQ

            if board.grid[rank][file].highlighted:
                #arcade.draw_lbwh_rectangle_filled(x, y, square, square, HIGHLIGHT_SQ)
                alt = HIGHLIGHT_SQ

            if board.grid[rank][file].clicked:
                #arcade.draw_lbwh_rectangle_filled(x, y, square, square, CLICK_SQ)
                alt = CLICK_SQ
            
            arcade.draw_lbwh_rectangle_filled(x, y, square, square, fill)

            #MIDDLE SQUARE
            arcade.draw_lbwh_rectangle_filled(
                x + inner_1, y + inner_1,
                square - 2 * inner_1, square - 2 * inner_1, 
                alt
            )

            #INNER SQUARE
            arcade.draw_lbwh_rectangle_filled(
                x + inner_2, y + inner_2,
                square - 2 * inner_2, square - 2 * inner_2,
                fill
            )


def draw_sidepanel(x: int, y: int, width: int, height: int, game: Game, board: Board, settings_mode: bool):
    """
    Draw the side panel with game information

    Args:
        x: X coordinate of panel
        y: Y coordinate of panel
        width: Width of panel
        height: Height of panel
        game: The Game object containing game state
        board: The Board object containing board state
        settings_mode: Whether to show settings panel or game panel
    """
    # Background
    arcade.draw_lbwh_rectangle_filled(x, y, width, height, SIDEPANEL_BG)

    # Settings button (always visible, top right) - always blue
    settings_button_size = 35
    settings_button_x = x + width - settings_button_size - 10
    settings_button_y = y + height - settings_button_size - 10

    settings_color = C.ROYAL_BLUE
    arcade.draw_lbwh_rectangle_filled(settings_button_x, settings_button_y,
                                      settings_button_size, settings_button_size,
                                      settings_color)
    arcade.draw_lbwh_rectangle_outline(settings_button_x, settings_button_y,
                                       settings_button_size, settings_button_size,
                                       C.WHITE, 2)
    arcade.draw_text("⚙", x + width - settings_button_size // 2 - 10,
                     y + height - settings_button_size // 2 - 10,
                     C.WHITE, 20, anchor_x="center", anchor_y="center")

    if not settings_mode:
        # Current turn / game status
        if board.stalemate == False and board.checkmate == False:
            turn_text = "White's Turn" if game.turn == Color.WHITE else "Black's Turn"
        elif board.stalemate == True:
            turn_text = "Stalemate!"
        elif board.resigned:
            turn_text = "Resignation!"
        else:
            turn_text = "Checkmate!"

        arcade.draw_text(turn_text, x + width // 2, y + height - 100,
                         C.WHITE, 16, anchor_x="center")

        # Material differential / game result
        material_diff = board.material_differential
        if board.checkmate == False and board.stalemate == False:
            if material_diff > 0:
                material_msg = f"White + {material_diff}"
            elif material_diff < 0:
                material_msg = f"Black + {abs(material_diff)}"
            else:
                material_msg = f"Even Material"
        elif board.checkmate == True:
            if board.mate_color == Color.WHITE:
                material_msg = f"White Wins!"
            else:
                material_msg = f"Black Wins!"
        else:
            material_msg = f"Draw :/"

        arcade.draw_text(material_msg, x + width // 2, y + height - 140,
                         C.WHITE, 14, anchor_x="center")

        # Resign button OR New Game button (same position)
        button_width = 100
        button_height = 40
        button_x = x + width // 2 - button_width // 2
        button_y = 200

        if board.checkmate or board.stalemate or board.resigned:
            # NEW GAME BUTTON
            arcade.draw_lbwh_rectangle_filled(button_x, button_y,
                                              button_width, button_height,
                                              C.DARK_GREEN)
            arcade.draw_lbwh_rectangle_outline(button_x, button_y,
                                               button_width, button_height,
                                               C.WHITE, 2)
            arcade.draw_text("NEW GAME", x + width // 2, button_y + button_height // 2,
                            C.WHITE, 11, anchor_x="center", anchor_y="center", bold=True)
        else:
            # RESIGN BUTTON
            arcade.draw_lbwh_rectangle_filled(button_x, button_y,
                                              button_width, button_height,
                                              C.DARK_RED)
            arcade.draw_lbwh_rectangle_outline(button_x, button_y,
                                               button_width, button_height,
                                               C.WHITE, 2)
            arcade.draw_text("RESIGN", x + width // 2, button_y + button_height // 2,
                            C.WHITE, 12, anchor_x="center", anchor_y="center", bold=True)

        # Color selection label (button is managed by UIManager)
        arcade.draw_text("User plays as:", x + width // 2, y + 80,
                         C.WHITE, 14, anchor_x="center")

    else:
        # settings panel
        arcade.draw_text("SETTINGS", x + width // 2, y + height - 100,
                         C.WHITE, 18, anchor_x="center", bold=True)


class GameView(arcade.View):
    """
    Main game view handling rendering and user interaction.
    Manages the chess board, pieces, and player/bot turns.
    """

    def __init__(self, width: int, height: int, title: str):
        """
        Initialize the game view.

        Args:
            width: Window width
            height: Window height
            title: Window title (unused but required by parent)
        """
        super().__init__()
        self.crt_filter = CRTFilter(self.window.width, self.window.height,
                                    resolution_down_scale=1.0,
                                    hard_scan=-2.0,
                                    hard_pix=-2.0,
                                    display_warp = Vec2(0.0, 0.0),
                                    mask_dark=0.5,
                                    mask_light=1.2)

        self.filter_on = False
        self.settings_mode = False  # Track if settings panel is open
        self.current_difficulty = "MEDIUM"  # Track selected difficulty

        arcade.set_background_color(C.CADET_BLUE)
        self.window.set_caption(title)

        self.board = Board()
        self.game = Game()
        self.bot = Bot()
        self.square = 850 // 8
        self.origin_x = 0
        self.origin_y = (height - self.square * 8) // 2
        self.sidepanel_x = 850
        self.sidepanel_width = width - 850

        cell_pixel_width = 256

        # Loader + sprites from _assets/spritesheet.py
        self.sheet = Spritesheet("_assets/_sprites")
        self.sprites = ChessSprites(self.sheet, cell_pixel_width)
        self.sprites.build_from_board(
            self.board, self.square, self.origin_x, self.origin_y
        )

        # TRACKERS FOR SPRITE DRAGGING
        self.dragging_sprite = None
        self.drag_start_pos = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        """
        Added game_started flag to track if first move has been made.
        This allows bot to make first move when user plays BLACK.
        """
        self.game_started = False

        self.manager = UIManager()
        self.manager.enable()

        # Difficulty Buttons
        easy_style = {
            "normal": UIFlatButton.UIStyle(
                bg=arcade.color.DARK_GRAY,
                font_color=(0, 150, 0),  # Darker green
                border=(60, 60, 60),
                border_width=2),
            "hover": UIFlatButton.UIStyle(
                font_color=(0, 150, 0),  # Darker green
                bg=arcade.color.GRAY,
                border=(60, 60, 60),
                border_width=2),
            "press": UIFlatButton.UIStyle(
                font_color=(0, 150, 0),  # Darker green
                bg=arcade.color.LIGHT_GRAY,
                border=(60, 60, 60),
                border_width=2),
        }
        medium_style = {
            "normal": UIFlatButton.UIStyle(
                bg=arcade.color.DARK_GRAY,
                font_color=(200, 100, 0),  # Darker orange
                border=(60, 60, 60),
                border_width=2),
            "hover": UIFlatButton.UIStyle(
                font_color=(200, 100, 0),  # Darker orange
                bg=arcade.color.GRAY,
                border=(60, 60, 60),
                border_width=2),
            "press": UIFlatButton.UIStyle(
                font_color=(200, 100, 0),  # Darker orange
                bg=arcade.color.LIGHT_GRAY,
                border=(60, 60, 60),
                border_width=2),
        }
        hard_style = {
            "normal": UIFlatButton.UIStyle(
                bg=arcade.color.DARK_GRAY,
                font_color=(180, 0, 0),  # Darker red
                border=(60, 60, 60),
                border_width=2),
            "hover": UIFlatButton.UIStyle(
                font_color=(180, 0, 0),  # Darker red
                bg=arcade.color.GRAY,
                border=(60, 60, 60),
                border_width=2),
            "press": UIFlatButton.UIStyle(
                font_color=(180, 0, 0),  # Darker red
                bg=arcade.color.LIGHT_GRAY,
                border=(60, 60, 60),
                border_width=2),
        }
        self.easy = UIFlatButton(text="EASY", width=120,style=easy_style)
        self.easy.center_x = 980
        self.easy.center_y = 670
        self.manager.add(self.easy)

        @self.easy.event("on_click")
        def on_click_settings(event):
            print("EASY")
            self.bot.set_elo(400)
            self.current_difficulty = "EASY"

        self.medium = UIFlatButton(text="MEDIUM", width=120, style = medium_style)
        self.medium.center_x = 980
        self.medium.center_y = 610
        self.manager.add(self.medium)

        @self.medium.event("on_click")
        def on_click_settings(event):
            print("MEDIUM")
            self.bot.set_elo(1000)
            self.current_difficulty = "MEDIUM"

        self.hard = UIFlatButton(text="HARD", width=120, style = hard_style)
        self.hard.center_x = 980
        self.hard.center_y = 550
        self.manager.add(self.hard)

        @self.hard.event("on_click")
        def on_click_settings(event):
            print("HARD")
            self.bot.set_elo(2000)
            self.current_difficulty = "HARD"

        # ================ THEME BUTTONS ======================
        theme_button_style = {
            "normal": UIFlatButton.UIStyle(
                bg=arcade.color.DARK_GRAY,
                font_color=arcade.color.BLACK,
                border=(60, 60, 60),
                border_width=2),
            "hover": UIFlatButton.UIStyle(
                bg=arcade.color.GRAY,
                font_color=arcade.color.BLACK,
                border=(60, 60, 60),
                border_width=2),
            "press": UIFlatButton.UIStyle(
                bg=arcade.color.LIGHT_GRAY,
                font_color=arcade.color.BLACK,
                border=(60, 60, 60),
                border_width=2),
        }

        # White theme button
        self.white_theme_button = UIFlatButton(text="Change WHITE Theme", width=180, style=theme_button_style)
        self.white_theme_button.center_x = 980
        self.white_theme_button.center_y = 460
        self.manager.add(self.white_theme_button)

        @self.white_theme_button.event("on_click")
        def _white_theme(event):
            print("Changing WHITE Theme")
            self.sheet.next_white_theme()
            self.sprites.build_from_board(self.board, self.square, self.origin_x, self.origin_y, self.game.user_color)

        # Black theme button
        self.black_theme_button = UIFlatButton(text="Change BLACK Theme", width=180, style=theme_button_style)
        self.black_theme_button.center_x = 980
        self.black_theme_button.center_y = 400
        self.manager.add(self.black_theme_button)

        @self.black_theme_button.event("on_click")
        def _black_theme(event):
            print("Changing BLACK Theme")
            self.sheet.next_black_theme()
            self.sprites.build_from_board(self.board, self.square, self.origin_x, self.origin_y, self.game.user_color)

        # ================ COLOR SELECTION BUTTON ======================
        self.color_button_style_white = {
            "normal": UIFlatButton.UIStyle(
                bg=arcade.color.WHITE,
                font_color=arcade.color.BLACK,
                border=(128, 128, 128),
                border_width=2),
            "hover": UIFlatButton.UIStyle(
                bg=arcade.color.LIGHT_GRAY,
                font_color=arcade.color.BLACK,
                border=(128, 128, 128),
                border_width=2),
            "press": UIFlatButton.UIStyle(
                bg=arcade.color.GRAY,
                font_color=arcade.color.BLACK,
                border=(128, 128, 128),
                border_width=2),
        }

        self.color_button_style_black = {
            "normal": UIFlatButton.UIStyle(
                bg=arcade.color.BLACK,
                font_color=arcade.color.WHITE,
                border=(128, 128, 128),
                border_width=2),
            "hover": UIFlatButton.UIStyle(
                bg=arcade.color.LIGHT_GRAY,
                font_color=arcade.color.WHITE,
                border=(128, 128, 128),
                border_width=2),
            "press": UIFlatButton.UIStyle(
                bg=arcade.color.GRAY,
                font_color=arcade.color.WHITE,
                border=(128, 128, 128),
                border_width=2),
        }

        # Color selection button
        self.color_button = UIFlatButton(text="WHITE", width=80, style=self.color_button_style_white)
        self.color_button.center_x = 980
        self.color_button.center_y = 50
        self.manager.add(self.color_button)

        @self.color_button.event("on_click")
        def _toggle_color(event):
            # Toggle user color
            self.game.user_color = Color.BLACK if self.game.user_color == Color.WHITE else Color.WHITE

            # Update button text and style
            if self.game.user_color == Color.WHITE:
                self.color_button.text = "WHITE"
                self.color_button.style = self.color_button_style_white
            else:
                self.color_button.text = "BLACK"
                self.color_button.style = self.color_button_style_black

            # Reset the game
            self.board.reset_board()
            self.game.turn = Color.WHITE
            self.game_started = False
            self.sprites.build_from_board(
                self.board, self.square, self.origin_x, self.origin_y, self.game.user_color
            )

            # If user chose black, bot makes first move
            if self.game.user_color == Color.BLACK:
                self.make_bot_move()
                self.game.turn = self.game.user_color
                self.game_started = True

        # Hide all settings buttons initially
        self.easy.visible = False
        self.medium.visible = False
        self.hard.visible = False
        self.white_theme_button.visible = False
        self.black_theme_button.visible = False


    def screen_to_board_coords(self, visual_file: int, visual_rank: int) -> tuple[int, int]:
        """
        Convert visual screen coordinates to actual board coordinates.

        Args:
            visual_file: File coordinate on screen (0-7)
            visual_rank: Rank coordinate on screen (0-7)
        Returns:
            Tuple of (actual_file, actual_rank) on the board
        """
        if self.game.user_color == Color.BLACK:
            return (7 - visual_file, 7 - visual_rank)
        return (visual_file, visual_rank)

    def board_to_screen_coords(self, board_file: int, board_rank: int) -> tuple[int, int]:
        """
        Convert actual board coordinates to visual screen coordinates.

        Args:
            board_file: File coordinate on board (0-7)
            board_rank: Rank coordinate on board (0-7)
        Returns:
            Tuple of (visual_file, visual_rank) for screen display
        """
        if self.game.user_color == Color.BLACK:
            return (7 - board_file, 7 - board_rank)
        return (board_file, board_rank)

    def on_show_view(self):
        """Called when this view is shown - ensures buttons are hidden on startup"""
        self.easy.visible = False
        self.medium.visible = False
        self.hard.visible = False
        self.white_theme_button.visible = False
        self.black_theme_button.visible = False

    def on_draw(self):
        if self.filter_on:
                # Draw our stuff into the CRT filter
                self.crt_filter.use()
                self.crt_filter.clear()
                # Switch back to our window and draw the CRT filter do
                # draw its stuff to the screen
                draw_board(self.board, self.origin_x, self.origin_y, self.square, self.game.user_color)
                self.sprites.draw()
                draw_sidepanel(self.sidepanel_x, 0, self.sidepanel_width,
                            self.window.height, self.game, self.board, self.settings_mode)
                self.manager.draw()

                self.window.use()
                self.clear()


                # draw stretched
                self.crt_filter.draw()

        else:
            self.clear()
            draw_board(self.board, self.origin_x, self.origin_y, self.square, self.game.user_color)
            self.sprites.draw()
            draw_sidepanel(self.sidepanel_x, 0, self.sidepanel_width, self.window.height, self.game, self.board, self.settings_mode)
            self.manager.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Handle mouse button press events

        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
            button: Which mouse button was pressed
            key_modifiers: Active keyboard modifiers
        """

        # Settings button
        settings_button_size = 35
        settings_button_x = self.sidepanel_x + self.sidepanel_width - settings_button_size - 10
        settings_button_y = self.window.height - settings_button_size - 10

        if (settings_button_x <= x <= settings_button_x + settings_button_size and
            settings_button_y <= y <= settings_button_y + settings_button_size):
            # Toggle settings mode
            self.settings_mode = not self.settings_mode

            # Show/hide settings buttons
            self.easy.visible = self.settings_mode
            self.medium.visible = self.settings_mode
            self.hard.visible = self.settings_mode
            self.white_theme_button.visible = self.settings_mode
            self.black_theme_button.visible = self.settings_mode

            return

        # Don't process game clicks if in settings mode
        if self.settings_mode:
            return

        # Resign button
        button_width = 100
        button_height = 40
        action_button_x = self.sidepanel_x + self.sidepanel_width // 2 - button_width // 2
        action_button_y = 200

        if (action_button_x <= x <= action_button_x + button_width and
            action_button_y <= y <= action_button_y + button_height):

            if self.board.checkmate or self.board.stalemate or self.board.resigned:
                # NEW GAME clicked
                self.board.reset_board()
                self.game.turn = Color.WHITE
                self.game_started = False

                self.sprites.build_from_board(
                    self.board, self.square, self.origin_x, self.origin_y, self.game.user_color
                )

                if self.game.user_color == Color.BLACK:
                    self.make_bot_move()
                    self.game.turn = self.game.user_color
                    self.game_started = True

                print("New game started!")
            else:
                # RESIGN clicked
                self.board.resign(self.game.user_color)
                print(f"{self.game.user_color.name} resigned. {self.board.mate_color.name} wins!")

            return

        if self.board.checkmate or self.board.stalemate or self.board.resigned:
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            # Required by python arcade, needed to pass pylint
            # no functionality currently
            if modifiers & arcade.key.MOD_SHIFT:
                pass

            visual_file = int((x - self.origin_x) // self.square)
            visual_rank = int((y - self.origin_y) // self.square)

            # Convert visual coordinates to actual board coordinates
            file, rank = self.screen_to_board_coords(visual_file, visual_rank)

            if 0 <= file <= 7 and 0 <= rank <= 7:
                tile = self.board.grid[rank][file]

                if tile.has_piece() and tile.piece_here.color == self.game.user_color:
                    self.board.remove_highlights()
                    self.board.get_piece(tile.piece_here)
                    self.board.highlight_moves()

                    #Check if checkmate or stalemate
                    piece = tile.get_piece_here()
                    if piece.piece_type == PieceType.KING:
                        king_moves = self.board.get_all_legal(piece)
                        if len(king_moves) == 0:

                            #Check if anyone has moves
                            all_moves = self.board.get_all_moves(self.game.user_color)
                            if len(all_moves) == 0:

                                #Checkmate or stalemate
                                enemy_moves = self.board.get_all_enemy_moves(self.game.user_color)

                                if piece.current_pos in enemy_moves: #Checkmate
                                    print(f"{self.game.user_color.name} is in CHECKMATE")
                                    self.board.set_checkmate()
                                    self.board.set_mate_color(self.game.user_color.opposite())
                                    return

                                else:
                                    #Stalemate
                                    print(f"{self.game.user_color.name} is in STALEMATE")
                                    self.board.set_stalemate()
                                    return

                    #Check for draws
                    if self.board.check_draw():
                        print(f"Stalemate")
                        self.board.set_stalemate()
                        return

                    # Start dragging the sprite
                    sprite = self.get_sprite_at_position(file, rank)
                    if sprite:
                        self.dragging_sprite = sprite
                        self.drag_start_pos = (file, rank)

                        # Calculate offset
                        self.drag_offset_x = x - sprite.center_x
                        self.drag_offset_y = y - sprite.center_y

                elif self.game.turn != self.game.user_color:
                    print("Not your turn")

                elif tile.highlighted:
                    self.board.remove_highlights()
                    self.board.remove_prev()
                    self.move_piece_and_update_sprites(file, rank)
                    self.board.print_board()

                    self.game.turn = self.game.user_color.opposite()
                    self.make_bot_move()
                    self.game.turn = self.game.user_color

                else:
                    self.board.selected_piece = None
                    self.board.remove_highlights()

        elif button == arcade.MOUSE_BUTTON_RIGHT:

            if modifiers & arcade.key.MOD_SHIFT:
                pass

            visual_file = int((x - self.origin_x) // self.square)
            visual_rank = int((y - self.origin_y) // self.square)
            file, rank = self.screen_to_board_coords(visual_file, visual_rank)

            if 0 <= file <= 7 and 0 <= rank <= 7:
                tile = self.board.grid[rank][file]

                if tile.clicked:
                    tile.clear_click()
                else:
                    tile.click()


    def make_bot_move(self):
        """Make the bot's move and update the display"""
        bot_color = self.game.user_color.opposite()
        # Check if we can make a move
        if not self.board.is_curr_pos() or self.board.checkmate or self.board.stalemate:
            return None

        # Get all legal moves
        move_list = self.board.get_all_moves(color=bot_color)

        # Check for checkmate or stalemate
        if len(move_list) == 0:
            all_moves = self.board.get_all_enemy_moves(color=bot_color)

            for rank in range(8):
                for file in range(8):
                    piece = self.board.grid[rank][file].piece_here

                    if (piece and piece.color == bot_color and
                            piece.piece_type == PieceType.KING):

                        if piece.current_pos in all_moves:
                            print(f"{bot_color.name} is in CHECKMATE")
                            self.board.set_checkmate()
                            self.board.set_mate_color(bot_color.opposite())
                            return None
                        else:
                            print(f"{bot_color.name} is in STALEMATE")
                            self.board.set_stalemate()
                            return None
        
        if self.board.check_draw():
            print(f"stalemate from not enough pieces!")
            self.board.set_stalemate()
            return None
        move = self.bot.make_move(self.board, bot_color)

        if move:
            from_pos, to_pos = move

            # Rebuild sprites to show new board state
            self.sprites.build_from_board(
                self.board, self.square, self.origin_x, self.origin_y, self.game.user_color
            )

            # Highlight the bot's move (from and to squares)
            self.board.grid[from_pos[0]][from_pos[1]].prev_move()
            self.board.grid[to_pos[0]][to_pos[1]].prev_move()

    def get_tile_from_mouse(self, x, y):
        """
        Convert mouse coordinates to board tile coordinates

        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
        Returns:
            Tuple of (file, rank) or (None, None) if outside board
        """
        visual_file = int((x - self.origin_x) // self.square)
        visual_rank = int((y - self.origin_y) // self.square)

        file, rank = self.screen_to_board_coords(visual_file, visual_rank)

        if 0 <= file <= 7 and 0 <= rank <= 7:
            return file, rank
        return None, None

    def get_sprite_at_position(self, file, rank):
        """
        Find the sprite at a given board position

        Args:
            file: Board file (0-7)
            rank: Board rank (0-7)
        Returns:
            The sprite at that position, or None if not found
        """
        # Convert board coordinates to visual coordinates for sprite positioning
        visual_file, visual_rank = self.board_to_screen_coords(file, rank)

        # Calculate the center of the square
        center_x = self.origin_x + visual_file * self.square + self.square // 2
        center_y = self.origin_y + visual_rank * self.square + self.square // 2

        # Find sprite near this position (within half a square)
        for sprite in self.sprites.sprite_list:
            if (abs(sprite.center_x - center_x) < self.square // 2 and
                    abs(sprite.center_y - center_y) < self.square // 2):
                return sprite
        return None

    def move_piece_and_update_sprites(self, file, rank):
        """
        Move a piece and update sprite positions.

        Args:
            file: Target file (0-7)
            rank: Target rank (0-7)
        """

        if self.board.checkmate or self.board.stalemate:
            return

        #Handle captures
        piece = self.board.grid[rank][file].piece_here
        if piece:
            captured_piece = piece
            self.sprites.remove_sprite_by_piece(captured_piece)
            self.board.grid[rank][file].piece_here = None

        # Move piece on board and update sprite positions
        self.board.move_piece(file, rank)

        # Pawn at end of board (promotion)
        piece = self.board.grid[rank][file].get_piece_here()
        if piece and piece.piece_type == PieceType.PAWN:
            if (rank == 7 and piece.color == Color.WHITE) or (rank == 0 and piece.color == Color.BLACK):
                print(f"{piece.color.name} PAWN PROMOTED!")
                piece.promote()
                self.board.promote(piece.color, file, rank)

        # Rebuild sprites to show new board state
        self.sprites.build_from_board(
            self.board, self.square, self.origin_x, self.origin_y, self.game.user_color
        )

        # Reset game state
        self.board.print_board()

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Handle mouse motion events

        Args:
            x: Current mouse x coordinate
            y: Current mouse y coordinate
            dx: Change in x position
            dy: Change in y position
        """
        # Handle dragging of pieces
        if self.dragging_sprite:
            # Update sprite position to follow mouse
            self.dragging_sprite.center_x = x - self.drag_offset_x
            self.dragging_sprite.center_y = y - self.drag_offset_y

    def on_mouse_release(self, x, y, button, modifiers):
        """
        Handle mouse button release events.

        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
            button: Which mouse button was released
            modifiers: Active keyboard modifiers
        """
        # Required by python arcade, needed to pass pylint
        # no functionality currently
        if modifiers & arcade.key.MOD_SHIFT:
            pass

        # Handle dropping of pieces
        if button == arcade.MOUSE_BUTTON_LEFT and self.dragging_sprite:
            file, rank = self.get_tile_from_mouse(x, y)

            # Check if dropped on valid highlighted square
            if file is not None and rank is not None:
                tile = self.board.grid[rank][file]

                if tile.highlighted:
                    # Valid move
                    self.board.remove_highlights()
                    self.move_piece_and_update_sprites(file, rank)
                    self.game.turn = self.game.user_color.opposite()
                    self.make_bot_move()
                    self.game.turn = self.game.user_color
                else:
                    # Invalid move - snap back to original position
                    orig_file, orig_rank = self.drag_start_pos
                    visual_file, visual_rank = self.board_to_screen_coords(orig_file, orig_rank)
                    center_x = self.origin_x + visual_file * self.square + self.square // 2
                    center_y = self.origin_y + visual_rank * self.square + self.square // 1.5
                    self.dragging_sprite.center_x = center_x
                    self.dragging_sprite.center_y = center_y
                    self.dragging_sprite = None
                    self.drag_start_pos = None
                    self.drag_offset_x = 0
                    self.drag_offset_y = 0
                    return

            else:
                # Dropped outside board - snap back
                orig_file, orig_rank = self.drag_start_pos
                visual_file, visual_rank = self.board_to_screen_coords(orig_file, orig_rank)
                center_x = self.origin_x + visual_file * self.square + self.square // 2
                center_y = self.origin_y + visual_rank * self.square + self.square // 2
                self.dragging_sprite.center_x = center_x
                self.dragging_sprite.center_y = center_y
                self.dragging_sprite = None
                self.drag_start_pos = None
                self.drag_offset_x = 0
                self.drag_offset_y = 0
                return

        self.dragging_sprite = None
        self.drag_start_pos = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def wait(self):
        """ Function waits a second prior to making bot move """
        counter = 1
        start = time.time()
        while time.time() < start + 2:
            pass

    def on_key_press(self, symbol, modifiers):
        '''
        Handles reactions to key press events

        Args:
            symbol: which key was pressed
            modifiers: active keyboard modifiers
        '''
        if symbol == arcade.key.DOWN:
            self.show_prev_move()
        if symbol == arcade.key.UP:
            self.show_next_move()

    def show_prev_move(self):
        ''' Goes backwards one move in history'''
        if self.board.current_index > 0:
            self.board.current_index -= 1
            move = self.board.move_history[self.board.current_index]
            self.board.load_fen(move["FEN"])
            self.sprites.build_from_board(self.board, self.square, self.origin_x, self.origin_y, self.game.user_color)

    def show_next_move(self):
        ''' Goes forward one move in history '''
        if self.board.current_index < len(self.board.move_history) - 1:
            self.board.current_index += 1
            move = self.board.move_history[self.board.current_index]
            self.board.load_fen(move["FEN"])
            self.sprites.build_from_board(self.board, self.square, self.origin_x, self.origin_y, self.game.user_color)