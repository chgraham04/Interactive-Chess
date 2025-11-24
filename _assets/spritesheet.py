''' This module creates the _sprites and draws the _board '''
from __future__ import annotations
import os
from typing import Dict, Tuple
import arcade

piece_names = ["king", "queen", "bishop", "knight", "rook", "pawn"]
color_names = ["white", "black"]

class Spritesheet:
    """
    Simplified spritesheet loader for 12 unique PNGs.
    Loads textures from _assets/_sprites/ and provides them via get_texture().
    """
    def __init__(self, sprites_dir: str = "_assets/_sprites", themes: int = 3):
        base_dir = os.path.dirname(__file__)
        self.dir = os.path.normpath(os.path.join(base_dir, "..", sprites_dir))

        self.themes = themes
        self.white_theme = 1
        self.black_theme = 1
        self.current_theme = 1

        self._textures: Dict[Tuple[str, str, int], arcade.Texture] = {}
        self._load_textures()

    def __repr__(self):
        return "_assets/_sprites"

    def _load_textures(self):
        """Load all piece textures from disk for all themes"""
        for theme in range(1, self.themes + 1):
            for color in color_names:
                for piece in piece_names:
                    filename = f"{color}_{piece}_{theme}.png"
                    full_path = os.path.join(self.dir, filename)
                    if not os.path.exists(full_path):
                        raise FileNotFoundError(
                            f"Missing sprite image: {full_path}")
                    tex = arcade.load_texture(full_path)
                    self._textures[(color.upper(), piece.upper(), theme)] = tex
        print(f"[Spritesheet] Loaded {len(self._textures)} piece textures "
              "successfully.")

    def next_white_theme(self):
        """Cycle to next white piece theme"""
        self.white_theme = (self.white_theme % self.themes) + 1

    def next_black_theme(self):
        """Cycle to next black piece theme"""
        self.black_theme = (self.black_theme % self.themes) + 1

    def set_theme(self, theme_number: int):
        """Switch active theme of pieces"""
        self.current_theme = theme_number

    def get_texture(self, color, piece_type) -> arcade.Texture:
        """
        Retrieve the correct texture for a piece.
        Accepts either Enum objects or strings for color/piece_type.
        """
        color_name = getattr(color, "name", str(color)).upper()
        piece_name = getattr(piece_type, "name", str(piece_type)).upper()
        theme = (self.white_theme if color_name == "WHITE"
                else self.black_theme)
        return self._textures[(color_name, piece_name, theme)]


class ChessSprites:
    """Manages an Arcade SpriteList for all _board _pieces."""
    def __init__(self, sheet: Spritesheet, cell_pixel_width: int):
        self.sheet = sheet
        self.sprite_list = arcade.SpriteList(use_spatial_hash=True)
        self.cell_pixel_width = cell_pixel_width
        self._by_piece_id: Dict[int, arcade.Sprite] = {}

    @staticmethod
    def _tile_center(origin_x: int, origin_y: int, square: int,
                      rank: int, file: int) -> tuple[float, float]:
        return (
            origin_x + file * square + square / 2,
            origin_y + rank * square + square / 1.5,
        )

    def build_from_board(self, board, square: int, origin_x: int,
                        origin_y: int, user_color=None):
        """
        Build sprite list from board state with optional user color
        for board orientation

        Args:
            board: Board object containing piece positions
            square: Size of each square in pixels
            origin_x: X coordinate of board origin
            origin_y: Y coordinate of board origin
            user_color: Color user is playing (affects board orientation)
        """
        pad: float = 0.88
        self.sprite_list = arcade.SpriteList(use_spatial_hash=True)
        self._by_piece_id.clear()

        board.remove_prev()

        desired_w = square * pad
        scale = desired_w / self.cell_pixel_width

        for rank in range(8):
            for file in range(8):
                tile = board.grid[rank][file]
                if not tile.has_piece():
                    continue

                piece = tile.piece_here

                # Convert board coordinates to visual coordinates based on
                # user color
                if (user_color and hasattr(user_color, 'name')
                        and user_color.name == 'BLACK'):
                    visual_file = 7 - file
                    visual_rank = 7 - rank
                else:
                    visual_file = file
                    visual_rank = rank

                #Checks if piece already has sprite
                if id(piece) in self._by_piece_id:
                    spr = self._by_piece_id[id(piece)]
                    spr.center_x, spr.center_y = self._tile_center(
                        origin_x, origin_y, square, visual_rank, visual_file)

                else:

                    tex = self.sheet.get_texture(piece.color,
                                                 piece.piece_type)

                    spr = arcade.Sprite(tex, scale=scale)
                    spr.center_x, spr.center_y = self._tile_center(
                        origin_x, origin_y, square, visual_rank, visual_file)
                    self.sprite_list.append(spr)
                    self._by_piece_id[id(piece)] = spr

    def sync_from_board(self, board, square: int, origin_x: int,
                       origin_y: int, user_color=None):
        """
        Sync sprite list with board state

        Args:
            board: Board object containing piece positions
            square: Size of each square in pixels
            origin_x: X coordinate of board origin
            origin_y: Y coordinate of board origin
            user_color: Color user is playing (affects board orientation)
        """
        pad: float = 0.88
        self.build_from_board(board, square, origin_x, origin_y, user_color)

        desired_w = square * pad
        scale = desired_w / self.cell_pixel_width

        for rank in range(8):
            for file in range(8):
                tile = board.grid[rank][file]
                if tile.has_piece():
                    piece = tile.piece_here

                    if id(piece) not in self._by_piece_id:
                        # Convert board coordinates to visual coordinates
                        # based on user color
                        if (user_color and hasattr(user_color, 'name')
                                and user_color.name == 'BLACK'):
                            visual_file = 7 - file
                            visual_rank = 7 - rank
                        else:
                            visual_file = file
                            visual_rank = rank

                        tex = self.sheet.get_texture(piece.color,
                                                     piece.piece_type)

                        spr = arcade.Sprite(tex, scale=scale)
                        spr.center_x, spr.center_y = self._tile_center(
                            origin_x, origin_y, square, visual_rank,
                            visual_file)
                        self.sprite_list.append(spr)
                        self._by_piece_id[id(piece)] = spr
                else:
                    self.remove_sprite_by_piece(tile.piece_here)

    def draw(self):
        """Draw all sprites in the sprite list"""
        self.sprite_list.draw()

    def remove_sprite_by_piece(self, piece: "Piece"):
        """Remove sprite for given piece from sprite list"""
        sprite = self._by_piece_id.get(id(piece))
        if sprite:
            self._by_piece_id.pop(id(piece))
            self.sprite_list.remove(sprite)

    def reload_theme(self, board, square, origin_x, origin_y,
                    user_color=None):
        """
        Rebuild all sprites when theme is changed

        Args:
            board: Board object containing piece positions
            square: Size of each square in pixels
            origin_x: X coordinate of board origin
            origin_y: Y coordinate of board origin
            user_color: Color user is playing (affects board orientation)
        """
        self.build_from_board(board, square, origin_x, origin_y, user_color)