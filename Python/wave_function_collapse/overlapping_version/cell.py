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

    def set_tile(self, tile: np.ndarray) -> None:
        self.tile = tile

    def get_tile(self) -> np.ndarray:
        return self.tile

    def draw(self, screen: pygame.Surface, average_colour=None) -> None:
        if self.tile is None:
            # Average colour of top-left pixel of all possible tiles
            pygame.draw.rect(
                screen, average_colour, (self.x_pos, self.y_pos, self.width, self.height)
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
        return f"Cell(pos=({self.x_pos // self.width}, {self.y_pos // self.height}), collapsed={self.is_collapsed}, tile={self.tile}, possibilities={np.nonzero(self.possible)[0]})"
