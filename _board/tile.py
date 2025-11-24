"""
Contains the Tile class representing individual squares on chess board
"""
from dataclasses import dataclass
from typing import Optional
from _pieces.piece import Piece
from _enums.color import Color

@dataclass()
class Tile:
    """
    A single tile/square on the chess board

    Attributes:
        file: The file (column) position (0-7)
        rank: The rank (row) position (0-7)
        is_light_square: Whether this tile is a light or dark square
        piece_here: The piece currently on this tile, if any
        highlighted: Whether this tile is currently highlighted for a legal move
    """
    file: int
    rank: int
    is_light_square: bool
    piece_here: Optional[Piece] = None
    highlighted: bool = False
    prev: bool = False
    clicked: bool = False

    def has_piece(self) -> bool:
        """
        Check if there is a piece on this tile

        Returns:
            True if a piece is present, False otherwise
        """
        return self.piece_here is not None

    def is_same_color(self, color: Color) -> bool:
        """
        Check if the piece on this tile matches the given color

        Args:
            color: The color to check against
        Returns:
            True if there is a piece and it matches the color, False otherwise
        """
        return self.piece_here is not None and self.piece_here.color == color

    def is_other_color(self, color: Color) -> bool:
        """
        Check if the piece on this tile is a different color than given.

        Args:
            color: The color to check against
        Returns:
            True if there is a piece and it's a different color, False otherwise
        """
        return self.piece_here is not None and self.piece_here.color != color

    def highlight_move(self):
        """Highlight this tile to indicate it's a legal move"""
        self.highlighted = True

    def clear_highlight(self):
        """Remove highlight from this tile"""
        self.highlighted = False

    def prev_move(self):
        """ Highlight this tile to indicate that it was the last move made"""
        self.prev = True

    def clear_prev(self):
        """ Remove previous move highlight from this tile"""
        self.prev = False

    def click(self):
        """Mark this tile as clicked for user interface"""
        self.clicked = True

    def clear_click(self):
        """Remove clicked marking from this tile"""
        self.clicked = False

    def get_piece_here(self):
        """
        Get the piece currently on this tile

        Returns:
            The Piece object on this tile, None if empty
        """
        return self.piece_here