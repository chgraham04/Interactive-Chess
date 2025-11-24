"""
Board class which manages chess _board state and piece movements.
"""
from typing import List
from _pieces.piece import Piece, PieceType, Color
from _pieces.bishop import Bishop
from _pieces.king import King
from _pieces.knight import Knight
from _pieces.pawn import Pawn
from _pieces.queen import Queen
from _pieces.rook import Rook
from _board.tile import Tile

class Board:
    """
    Represents a chess _board with an 8x8 grid of tiles.
    Manages piece placement, movement, and check detection
    """

    def __init__(self) -> None:
        """Initialize the chess board with tiles and pieces in starting
        positions."""
        # nested list format
        # creates 8 lists for each row, each with 8 tile objects
        # initialized to none, replaced by Tile objects later
        self.grid: List[List[Tile]] = [[None for _ in range(8)]
                                       for _ in range(8)]
        self.selected_piece = None
        self.checking_for_checks = False
        self.en_passant_target = None
        self.move_history = []
        self.current_index = -1
        self.material_differential = 0
        self.checkmate = False
        self.stalemate = False
        self.mate_color = None
        self.resigned = False

        # assign tile objects to None lists
        for rank in range(8):
            for file in range(8):
                # determine if tile is light or dark square
                is_light = (file + rank) % 2 == 1
                # assign Tile object to list
                # use grid structure to format 2d matrix
                self.grid[rank][file] = Tile(file, rank, is_light)
        self.initialize_pieces()

    def initialize_pieces(self):
        """Initialize and populate all pieces to starting locations on the
        board"""
        # Pawns
        for file in range(8):
            self.grid[1][file].piece_here = Pawn(Color.WHITE, (file, 1))
            self.grid[6][file].piece_here = Pawn(Color.BLACK, (file, 6))

        # Kings
        self.grid[0][4].piece_here = King(Color.WHITE, (4, 0))
        self.grid[7][4].piece_here = King(Color.BLACK, (4, 7))

        # Queens
        self.grid[0][3].piece_here = Queen(Color.WHITE, (3, 0))
        self.grid[7][3].piece_here = Queen(Color.BLACK, (3, 7))

        # Rooks
        self.grid[0][0].piece_here = Rook(Color.WHITE, (0, 0))
        self.grid[0][7].piece_here = Rook(Color.WHITE, (7, 0))
        self.grid[7][0].piece_here = Rook(Color.BLACK, (0, 7))
        self.grid[7][7].piece_here = Rook(Color.BLACK, (7, 7))

        # Knights
        self.grid[0][1].piece_here = Knight(Color.WHITE, (1, 0))
        self.grid[0][6].piece_here = Knight(Color.WHITE, (6, 0))
        self.grid[7][1].piece_here = Knight(Color.BLACK, (1, 7))
        self.grid[7][6].piece_here = Knight(Color.BLACK, (6, 7))

        # Bishops
        self.grid[0][2].piece_here = Bishop(Color.WHITE, (2, 0))
        self.grid[0][5].piece_here = Bishop(Color.WHITE, (5, 0))
        self.grid[7][2].piece_here = Bishop(Color.BLACK, (2, 7))
        self.grid[7][5].piece_here = Bishop(Color.BLACK, (5, 7))

        #Sets initial board layout in previous move shower
        self.move_history.append({
            "Piece": None,
            "From": None,
            "To": None,
            "Captured": None,
            "FEN": self.board_state()
        })
        self.current_index = len(self.move_history) - 1

    def move_piece(self, file, rank):
        """
        Move the selected piece to the specified file and rank.
        Handles special moves like castling and updates _board state.
        """

        if not self.is_curr_pos():
            return

        before_move = self.selected_piece.get_position()
        before_move_rank = before_move[1]
        before_move_file = before_move[0]

        captured_piece = self.grid[rank][file].piece_here
        if captured_piece:
            # very piece_value is enum, need the integer .value
            piece_val = captured_piece.piece_value.value
            # print(f"DEBUG: Captured {captured_piece.color}
            # {captured_piece.piece_type} worth {piece_val}")
            # print(f"DEBUG: Material Differential Before:
            # {self.material_differential}")
            if captured_piece.color == Color.WHITE:
                self.material_differential -= piece_val
                print("WHITE captured")
            if captured_piece.color == Color.BLACK:
                self.material_differential += piece_val
                print("BLACK captured")

            # print(f"DEBUG: Material Differential After:
            # {self.material_differential}")
            # Actually call the delete method
            captured_piece.delete()

        self.selected_piece.move((file, rank), self)

        self.grid[rank][file].piece_here = self.selected_piece
        self.grid[before_move_rank][before_move_file].piece_here = None

        self.material_differential = self.calculate_material()
        piece = self.selected_piece
        # CASTLING
        if piece.piece_type == PieceType.KING and before_move_file == 4:
            if piece.color == Color.WHITE and rank == 0 and file == 6:
                rook = self.grid[0][7].get_piece_here()
                if rook:
                    self.grid[0][5].piece_here = rook
                    self.grid[0][7].piece_here = None
                    rook.current_pos = (5, 0)
                    print("White short castle")

            elif piece.color == Color.WHITE and rank == 0 and file == 2:
                rook = self.grid[0][0].get_piece_here()
                if rook:
                    self.grid[0][3].piece_here = rook
                    self.grid[0][0].piece_here = None
                    rook.current_pos = (3, 0)
                    print("White long castle")

            elif piece.color == Color.BLACK and rank == 7 and file == 6:
                rook = self.grid[7][7].get_piece_here()
                if rook:
                    self.grid[7][5].piece_here = rook
                    self.grid[7][7].piece_here = None
                    rook.current_pos = (5, 7)
                    print("Black short castle")

            elif piece.color == Color.BLACK and rank == 7 and file == 2:
                rook = self.grid[7][0].get_piece_here()
                if rook:
                    self.grid[7][3].piece_here = rook
                    self.grid[7][0].piece_here = None
                    rook.current_pos = (3, 7)
                    print("Black long castle")

        # Check if enemy is in check after move
        piece = self.selected_piece
        enemy_color = (Color.BLACK if piece.color == Color.WHITE
                      else Color.WHITE)

        # Clear all check indicators first
        self.remove_check_indicators()

        # Check and highlight if either king is in check
        if self.check_for_checks(enemy_color):
            print(f"{enemy_color.name} is in check!")
            self.highlight_king_in_check(enemy_color)

        # Also check if the current player's king is somehow in check
        # (shouldn't happen with legal moves, but good for debugging)
        if self.check_for_checks(piece.color):
            self.highlight_king_in_check(piece.color)

        print(f"{piece.color} {piece.piece_type} moved from "
              f"{before_move} to {(file, rank)}")

        #Add move to the move history list
        self.move_history.append({
            "Piece": piece,
            "From": before_move,
            "To": (file, rank),
            "Captured": captured_piece,
            "FEN": self.board_state()
        })

        #Store the current position in move history
        self.current_index = len(self.move_history) - 1
        self.selected_piece = None

    def get_piece(self, piece: Piece):
        """Set the currently selected piece"""
        self.selected_piece = piece

    def set_checkmate(self):
        """ Set the checkmate condition to true """
        self.checkmate = True

    def set_stalemate(self):
        """ Set the stalemate condition to true """
        self.stalemate = True

    def set_mate_color(self, color: Color):
        """Set the color of the player who won by checkmate"""
        self.mate_color = color

    def highlight_moves(self):
        """Highlight all legal moves for the currently selected piece"""
        # ensure a piece is selected
        if self.selected_piece:
            legal_moves = self.get_all_legal(self.selected_piece)
            for move in legal_moves:
                self.grid[move[1]][move[0]].highlight_move()

    def remove_highlights(self):
        """Remove all highlighted legal moves from the board"""
        for rank in range(8):
            for file in range(8):
                self.grid[rank][file].clear_highlight()

    def remove_prev(self):
        """Removes all highlighted tiles from the previously made move on
        the grid"""
        for rank in range(8):
            for file in range(8):
                self.grid[rank][file].clear_prev()

    def remove_check_indicators(self):
        """Remove all check indicators from the board"""
        for rank in range(8):
            for file in range(8):
                self.grid[rank][file].clear_check()

    def highlight_king_in_check(self, color: Color):
        """
        Highlight the king of the specified color if it's in check

        Args:
            color: The color of the king to check and highlight
        """
        if self.check_for_checks(color):
            king_pos = self.find_king(color)
            if king_pos:
                self.grid[king_pos[1]][king_pos[0]].set_check()

    def get_all_moves(self, color: Color):
        """
        Get all possible moves for pieces of the player color.

        Args:
            color: The color of the player
        Returns:
            List of all possible player move positions
        """
        all_moves = []

        #Get moves for each piece
        for rank in range(8):
            for file in range(8):
                piece = self.grid[rank][file].piece_here
                if (piece and piece.color == color):
                    curr = self.get_all_legal(piece)

                    for move in curr:
                        if move not in all_moves:
                            all_moves.append(move)

        return all_moves

    def get_all_enemy_moves(self, color: Color):
        """
        Get all possible moves for pieces of the opposite color.

        Args:
            color: The color of the player whose opponent moves to get
        Returns:
            List of all possible enemy move positions
        """
        all_moves = []

        # Get moves for each piece
        for rank in range(8):
            for file in range(8):
                piece = self.grid[rank][file].piece_here
                if (piece and piece.color != color):
                    curr = self.get_all_legal(piece)

                    for move in curr:
                        if move not in all_moves:
                            all_moves.append(move)

        return all_moves

    def find_king(self, color: Color):
        """
        Find the position of the king for the specified color

        Args:
            color: The color of the king to find
        Returns:
            Tuple of (file, rank) or None if king not found
        """
        for rank in range(8):
            for file in range(8):
                piece = self.grid[rank][file].piece_here
                if (piece and piece.color == color
                        and piece.piece_type.name == "KING"):
                    return (file, rank)

        return None

    def check_for_checks(self, color: Color):
        """
        Check whether the king of the specified color is currently in check

        Args:
            color: The color of the king to check
        Returns:
            True if king is in check, False otherwise
        """
        # prevent infinite recursion
        if self.checking_for_checks:
            return False

        self.checking_for_checks = True

        try:
            king_pos = self.find_king(color)
            if not king_pos:
                return False

            enemy_moves = self.get_all_enemy_moves(color)
            return king_pos in enemy_moves

        finally:
            self.checking_for_checks = False

    def check_if_move_into_check(self, piece: Piece,
                                 new_pos: tuple[int, int]):
        """
        Check if moving a piece to a new position would put the king in check

        Args:
            piece: The piece to move
            new_pos: The target position (file, rank)
        Returns:
            True if move would result in check, False otherwise
        """
        current_pos = piece.current_pos
        next_pos = self.grid[new_pos[1]][new_pos[0]]

        # Store piece on target tile
        captured_piece = next_pos.piece_here

        # Simulate move
        self.grid[current_pos[1]][current_pos[0]].piece_here = None
        next_pos.piece_here = piece
        piece.current_pos = new_pos

        # See if moves into check
        check = self.check_for_checks(piece.color)

        # Undo move
        self.grid[current_pos[1]][current_pos[0]].piece_here = piece
        next_pos.piece_here = captured_piece
        piece.current_pos = current_pos

        return check

    def get_all_legal(self, piece: Piece):
        """
        Get all legal moves for a piece that don't put king in check

        Args:
            piece: The piece to get legal moves for
        Returns:
            List of legal move positions
        """
        check_moves = piece.get_moves(self)
        legal_moves = []

        for move in check_moves:
            if not self.check_if_move_into_check(piece, move):
                legal_moves.append(move)

        return legal_moves

    def check_if_danger(self, square: tuple[int, int], enemy_moves: list,
                        visited_squares=None):
        """
        Check if a certain tile is under threat of enemy pieces

        Args:
            square: The position to check (file, rank)
            enemy_moves: List of all enemy move positions
            visited_squares: Set of already visited squares to prevent
                           recursion
        Returns:
            True if square is under attack, False otherwise
        """
        if visited_squares is None:
            visited_squares = set()

        # Prevent recursion
        if square in visited_squares:
            return False

        visited_squares.add(square)

        if square in enemy_moves:
            return True

        return False

    def en_passant(self, piece: Pawn, new_pos: tuple[int, int]):
        """
        Handle en passant checking and capturing

        Args:
            piece: The pawn performing en passant
            new_pos: The target position (file, rank)
        """
        prev_pos = piece.current_pos

        if self.en_passant_target and new_pos == self.en_passant_target:

            if piece.color == Color.WHITE:
                check_square = (new_pos[0], new_pos[1] - 1)
            else:
                check_square = (new_pos[0], new_pos[1] + 1)

            self.grid[check_square[1]][check_square[0]].piece_here = None

        self.grid[prev_pos[1]][prev_pos[0]].piece_here = None
        self.grid[new_pos[1]][new_pos[0]].piece_here = piece
        piece.current_pos = new_pos
        piece.has_moved = True

        self.en_passant_target = None

    def resign(self, resigning_color: Color):
        """
        Handle player resignation

        Args:
            resigning_color: The color of the player who is resigning
        """
        self.resigned = True
        self.checkmate = True
        # Winner is the opposite color
        self.mate_color = resigning_color.opposite()
        print(f"{resigning_color.name} resigned. {self.mate_color.name} "
              "wins!")

    def reset_board(self):
        """
        Reset the board to the initial starting position
        """
        # Clear all tiles
        for rank in range(8):
            for file in range(8):
                is_light = (file + rank) % 2 == 1
                self.grid[rank][file] = Tile(file, rank, is_light)

        # Reset board state
        self.selected_piece = None
        self.checking_for_checks = False
        self.en_passant_target = None
        self.move_history = []
        self.current_index = -1
        self.material_differential = 0
        self.checkmate = False
        self.stalemate = False
        self.mate_color = None
        self.resigned = False

        # Clear all visual indicators
        self.remove_check_indicators()

        # reinitialize pieces to starting positions
        self.initialize_pieces()
        print("Board reset to starting position")

    def print_board(self):
        """Print a text representation of the _board to console (testing)"""
        for rank in range(7, -1, -1):  # print rank 8 down to 1
            row_str = ""
            for file in range(8):  # left to right
                piece = self.grid[rank][file].piece_here
                if piece is None:
                    row_str += ". "
                else:
                    symbol = piece.piece_type.value
                    # uppercase for White, lowercase for Black
                    if piece.color == Color.WHITE:
                        row_str += symbol.upper() + " "
                    else:
                        row_str += symbol.lower() + " "
            print(row_str)
        print()

    def board_state(self, active_color: Color = None):
        """
        Generate FEN (Forsyth-Edwards Notation) string of current _board state

        Modified board_state to accept optional active_color parameter.
        Returns full FEN string including turn indicator, castling rights,
        en passant, etc. If no active_color provided, returns just piece
        positions (backward compatible).

        Args:
            active_color: Optional - Whose turn it is (Color.WHITE or
                         Color.BLACK). If provided, returns full FEN. If None,
                         returns only positions.
        Returns:
            FEN string representing the _board position
        """
        fen_string = ""
        for rank in range(7, -1, -1):  # print rank 8 down to 1
            fen_row = ""
            empty_count = 0
            for file in range(8):
                piece = self.grid[rank][file].piece_here
                if piece is None:
                    empty_count += 1
                    if file == 7:
                        fen_row = fen_row + str(empty_count)
                else:
                    symbol = piece.piece_type.value
                    if empty_count > 0:
                        fen_row = fen_row + str(empty_count)
                        empty_count = 0
                        if piece.color == Color.WHITE:
                            fen_row += symbol.upper()
                        else:
                            fen_row += symbol.lower()
                    else:
                        if piece.color == Color.WHITE:
                            fen_row += symbol.upper()
                        else:
                            fen_row += symbol.lower()
            fen_string += (fen_row + "/")
        fen_string = fen_string[:-1]

        # If active_color provided, return full FEN
        if active_color is not None:
            # Add turn indicator
            turn_char = 'w' if active_color == Color.WHITE else 'b'

            # Add castling rights (simplified for now - could be improved)
            castling = '-'

            # Add en passant target
            if self.en_passant_target:
                file_letter = chr(ord('a') + self.en_passant_target[0])
                rank_number = str(self.en_passant_target[1] + 1)
                en_passant = f"{file_letter}{rank_number}"
            else:
                en_passant = '-'

            # Add halfmove and fullmove counters (simplified)
            halfmove = 0
            fullmove = 1

            fen_string = (f"{fen_string} {turn_char} {castling} "
                         f"{en_passant} {halfmove} {fullmove}")

        return fen_string

    def calculate_material(self):
        '''
        Calculates the total material balance of the board

        Returns:
            Difference in total white material vs total black material
        '''
        white_total = 0
        black_total = 0

        for rank in range(8):
            for file in range(8):
                piece = self.grid[rank][file].piece_here

                if not piece:
                    continue

                value = (piece.piece_value.value
                        if hasattr(piece.piece_value, "value")
                        else piece.piece_value)

                if piece.color == Color.WHITE:
                    white_total += value
                else:
                    black_total += value

        return white_total - black_total

    def load_fen(self, fen):
        '''
        Reset the board to the position described by a FEN string

        Args:
            fen: fen representation of board layout
        '''

        for file in range(8):
            for rank in range(8):

                #Check if tile is light
                is_light = (rank + file) % 2 == 1

                #Recreate the tiles
                self.grid[rank][file] = Tile(file, rank, is_light)

        #Split fen string apart per row
        rank_rows = fen.split('/')

        #Iterate through ranks and files
        for rank_index, row in enumerate(reversed(rank_rows)):
            file_index = 0

            #Find empty squares
            for char in row:
                if char.isdigit():
                    file_index += int(char)

                #If not digit, there is a piece here
                else:
                    color = Color.WHITE if char.isupper() else Color.BLACK
                    piece_type_char = char.lower()

                    #Place piece
                    piece_class = {
                        'p': Pawn,
                        'r': Rook,
                        'n': Knight,
                        'b': Bishop,
                        'q': Queen,
                        'k': King
                    }[piece_type_char]

                    piece = piece_class(color, (file_index, rank_index))

                    #Handle has_moved for pawn
                    if isinstance(piece, Pawn):
                        if ((piece.color == Color.WHITE
                                and rank_index != 1)
                                or (piece.color == Color.BLACK
                                    and rank_index != 6)):
                            piece.has_moved = True

                    #TODO - implement has_moved for rook and king as well

                    self.grid[rank_index][file_index].piece_here = piece
                    file_index += 1

        #Calculate previous material difference
        self.material_differential = self.calculate_material()

        # Clear check indicators when loading a position
        self.remove_check_indicators()

    def on_mouse_release(self, x: float, y: float, button: int,
                        modifiers: int):
        """Handle mouse release events (placeholder for future
        implementation)"""

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """Handle mouse motion events (placeholder for future
        implementation)"""

    def is_curr_pos(self):
        """ Check if board displays current move """
        return self.current_index == len(self.move_history) - 1

    def promote(self, color, file, rank):
        """
        Create a new instance of a queen wherever a pawn is promoted

        Args:
            color: The color of the piece
            file: The file of the pawn/queen
            rank: The rank of the pawn/queen
        """
        self.grid[rank][file].piece_here = Queen(color, (file, rank))

    def check_draw(self):
        """
        Check to see if enough pieces are left on the board to complete a
        checkmate; if not, sets draw to true.

        Returns:
            1 if draw condition met, 0 otherwise
        """
        piece_count = 0

        #If more than four pieces on the board, checkmate is possible
        # (bishop/knight and king in each color invalidate checkmate)
        for rank in range(8):
            for file in range(8):
                piece = self.grid[rank][file].piece_here
                if piece:

                    piece_count += 1

                    if piece.piece_type in (PieceType.ROOK,
                                           PieceType.QUEEN,
                                           PieceType.PAWN):
                        return 0

        if piece_count <= 4:
            return 1

        return 0
