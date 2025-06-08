import heapq
from collections import deque
from random import randint

import numpy as np

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
        self.cells = [[Cell(x, y, self.size_in_cells, self.cell_size, self.tile_set.adjacencies, self.tile_set.frequencies) for x in range(self.size_in_cells[0])] for y in range(self.size_in_cells[1])]

    def choose_next_cell(self) -> tuple[int, int]:
        while len(self.entropy_heap) > 0:
            entropy_coord = heapq.heappop(self.entropy_heap)
            cell = self.cells[entropy_coord[2]][entropy_coord[1]]
            if not cell.is_collapsed:
                return entropy_coord

        raise IndexError("Entropy_heap is empty but there are still uncollapsed cells")

    def collapse_cell_at(self, cell_coord: tuple[int, int]) -> None:
        cell = self.cells[cell_coord[0]][cell_coord[1]]
        tile_index = cell.choose_tile_index()
        cell.is_collapsed = True
        cell.possible[:] = False
        cell.possible[tile_index] = True
        # self.tile_removals.extend(np.flatnonzero(~cell.possible))   # add indices of all False values to deque
        self.tile_removals.append((tile_index, cell_coord))

    def propagate(self) -> None:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # N, S, W, E
        opposites = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # S, N, E, W
        last_enabler = np.array([1, 1, 1, 1])

        while self.tile_removals:
            # at some point in the recent past, removal_update.tile_index was removed as a candidate for the tile in
            # the cell at removal_update.coord
            removal_update = self.tile_removals.popleft()

            for dir_index, direction in enumerate(directions):
                # propagate the effect to the neighbour in each direction
                neighbour_coord = (removal_update[1][0] + direction[0], removal_update[1][1] + direction[1])
                if neighbour_coord[0] < 0 or neighbour_coord[0] >= self.size_in_cells[0] or neighbour_coord[1] < 0 or neighbour_coord[1] >= self.size_in_cells[1]:
                    continue

                neighbour_cell = self.cells[neighbour_coord[0]][neighbour_coord[1]]

                compatible_tiles = np.nonzero(
                    self.tile_set.adjacencies[removal_update[0], dir_index]
                )[0]

                # iterate over all the tiles which may appear in the cell one space in `direction` from a
                # cell containing removal_update.tile_index
                for compatible_tile in compatible_tiles:
                    # check if we're about to decrement any enablers to zero
                    enabler_counts = neighbour_cell.tile_enabler_counts.enablers[
                                neighbour_coord[0],
                                neighbour_coord[1],
                                :,
                                compatible_tile,
                            ]

                    if enabler_counts[dir_index] == 1:
                        # if there is a zero count in another direction, the potential tile has already been removed,
                        # and we want to avoid removing it again
                        if not np.any(np.equal(enabler_counts, np.zeros_like(enabler_counts))):
                            # remove the possibility
                            neighbour_cell.remove_tile(compatible_tile)

                            # check for contradictions
                            if len(neighbour_cell.possible[neighbour_cell.possible]) == 0:
                                # contradiction
                                raise LookupError(f"No possible tiles exist for cell ({removal_update[0]},{removal_update[1]})")

                            # this probably changed the cell's entropy
                            heapq.heappush(self.entropy_heap, (neighbour_cell.entropy(), neighbour_coord))

                            # add the update to the stack
                            self.tile_removals.append((compatible_tile, neighbour_coord))

                    neighbour_cell.tile_enabler_counts.enablers[
                        neighbour_coord[0],
                        neighbour_coord[1],
                        dir_index,
                        compatible_tile,
                    ] -= 1


    def step(self) -> None:
        if self.num_uncollapsed_cells > 0:
            if self.num_uncollapsed_cells == self.num_cells:
                next_cell = (randint(0, self.size_in_cells[0] - 1), randint(0, self.size_in_cells[1] - 1))
            else:
                next_cell = self.choose_next_cell()
            self.collapse_cell_at(next_cell)
            self.propagate()
            self.num_uncollapsed_cells -= 1
