import heapq
import numpy as np
from collections import deque
from cell import Cell
from tile_set import TileSet


class Grid:
    def __init__(self, screen_size: tuple[int, int], size_in_cells: tuple[int, int], tile_set: TileSet, scaling: int=1, wrap: bool=False) -> None:
        self.screen_size = screen_size
        self.tile_set = tile_set
        self.size_in_cells = size_in_cells
        self.cell_size = min(self.screen_size[0] // self.size_in_cells[0], self.screen_size[1] // self.size_in_cells[1])
        self.num_cells = len(self.tile_set.tiles)
        self.num_uncollapsed_cells = len(self.tile_set.tiles)
        self.scaling = scaling
        self.wrap = wrap
        self.entropy_heap = []            # entries in here need to be of the form (entropy, y-coord, x-coord)
        heapq.heapify(self.entropy_heap)
        self.tile_removals = deque()      # entries in here need to be of the form (tile_index, y-coord, x-coord)
        self.cells = [[Cell(x, y, self.cell_size, self.cell_size, self.tile_set.adjacencies, self.tile_set.frequencies) for x in range(self.size_in_cells[0])] for y in range(self.size_in_cells[1])]

    def choose_next_cell(self) -> tuple[int, int]:
        while len(self.entropy_heap) > 0:
            entropy_coord = heapq.heappop(self.entropy_heap)
            cell = self.cells[entropy_coord[2]][entropy_coord[1]]
            if not cell.is_collapsed:
                return entropy_coord

        raise IndexError("Entropy_heap is empty but there are still uncollapsed cells")

    def collapse_cell_at(self, cell_coord: tuple[int, int]) -> None:
        cell = self.cells[cell_coord[1]][cell_coord[0]]
        tile_index = cell.choose_tile_index()
        cell.is_collapsed = True
        cell.possible[:] = False
        cell.possible[tile_index] = True
        self.tile_removals.extend(np.flatnonzero(~cell.possible))   # add indices of all False values to deque

    def propagate(self) -> None:
        pass
        # while self.tile_removals:
        #     removal_update = heapq.heappop(self.entropy_heap)
        #
        #     for direction in range(4):  # N, S, W, E
        #         neighbour_coord = removal_update.

    def step(self) -> None:
        if self.num_uncollapsed_cells > 0:
            next_cell = self.choose_next_cell()
            self.collapse_cell_at(next_cell)
            self.propagate()
            self.num_uncollapsed_cells -= 1
