import numpy as np
import pygame


class Cell:
    def __init__(
        self, x_pos: int, y_pos: int, cell_size: int, total_number_of_tiles: int
    ) -> None:
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = cell_size
        self.height = cell_size
        self.possible = np.full(total_number_of_tiles, True, dtype=np.bool_)
        self.tile = None
        self.is_collapsed = False
        self.recursion_checked = False

    def copy(self):
        """Create a fast copy of this cell"""
        # Create new cell with same position and size
        new_cell = Cell.__new__(Cell)  # Create instance without calling __init__

        # Copy all attributes efficiently
        new_cell.x_pos = self.x_pos
        new_cell.y_pos = self.y_pos
        new_cell.width = self.width
        new_cell.height = self.height
        new_cell.is_collapsed = self.is_collapsed
        new_cell.recursion_checked = self.recursion_checked

        # Copy numpy array efficiently
        new_cell.possible = self.possible.copy()

        # Handle tile reference (shallow copy is usually sufficient for tiles)
        new_cell.tile = self.tile  # Shallow copy - tiles are typically immutable

        return new_cell

    def deep_copy(self):
        """Create a deep copy of this cell (slower but safer)"""
        # Create new cell with same position and size
        new_cell = Cell.__new__(Cell)  # Create instance without calling __init__

        # Copy all attributes
        new_cell.x_pos = self.x_pos
        new_cell.y_pos = self.y_pos
        new_cell.width = self.width
        new_cell.height = self.height
        new_cell.is_collapsed = self.is_collapsed
        new_cell.recursion_checked = self.recursion_checked

        # Deep copy numpy arrays
        new_cell.possible = self.possible.copy()

        # Deep copy tile if it exists
        if self.tile is not None:
            new_cell.tile = self.tile.copy()
        else:
            new_cell.tile = None

        return new_cell

    def copy_state_from(self, other_cell):
        """Copy state from another cell (in-place, very fast)"""
        if not isinstance(other_cell, Cell):
            raise TypeError("Can only copy from another Cell object")

        # Copy state attributes (position stays the same)
        self.is_collapsed = other_cell.is_collapsed
        self.recursion_checked = other_cell.recursion_checked

        # Copy numpy array efficiently
        np.copyto(self.possible, other_cell.possible)

        # Copy tile reference
        self.tile = other_cell.tile

    def set_tile(self, tile: np.ndarray) -> None:
        self.tile = tile

    def get_tile(self) -> np.ndarray:
        return self.tile

    def draw(self, screen: pygame.Surface):
        colour = (120, 120, 120)
        if self.tile is None:
            pygame.draw.rect(
                screen, colour, (self.x_pos, self.y_pos, self.width, self.height), 1
            )
        else:
            blit_array = np.transpose(self.tile, (1, 0, 2))
            # Top-left pixel of 3x3 tile
            pygame.draw.rect(
                screen,
                blit_array[0, 0],
                (self.x_pos, self.y_pos, self.width, self.height),
            )

    def reset(self):
        """Reset cell to initial uncollapsed state"""
        self.possible.fill(True)
        self.tile = None
        self.is_collapsed = False
        self.recursion_checked = False

    def __repr__(self):
        return f"Cell(pos=({self.x_pos}, {self.y_pos}), collapsed={self.is_collapsed}, possibilities={np.sum(self.possible)})"
