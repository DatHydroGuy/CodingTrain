import copy
from random import choice
import pygame
import numpy as np
from collections import deque
from numpy import ndarray
from cell import Cell
from tile_set import TileSet


class Grid:
    def __init__(self, screen_size: tuple[int, int], grid_resolution: tuple[int, int], tile_set: TileSet, wrap: bool=False):
        self.screen_size = screen_size
        self.tile_set = tile_set
        self.width_in_cells = grid_resolution[0]
        self.height_in_cells = grid_resolution[1]
        self.cell_size = min(self.screen_size[0] // self.width_in_cells, self.screen_size[1] // self.height_in_cells)
        self.num_tiles = len(self.tile_set.tiles)
        self.draw_size = (self.tile_set.kernel_size, self.tile_set.kernel_size)
        self.wrap = wrap
        self.finished = False
        self.cells = np.array([[Cell(x * self.cell_size, y * self.cell_size, self.cell_size, self.num_tiles) for x in range(self.width_in_cells)] for y in range(self.height_in_cells)])
        self.neighbours = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # N, S, W, E
        # Cache for backtracking - maybe a queue would be more efficient?
        self.grid_copy = []

    def step(self):
        next_cell = self.get_lowest_entropy_cell()

        if next_cell is None or next_cell.is_collapsed:     # should never be collapsed, just being defensive
            return False

        # choose a tile to collapse to
        next_cell_tile = choice(np.nonzero(next_cell.possible)[0])

        # collapse the cell
        success = self.collapse_cell(next_cell, next_cell_tile)

        while not success:
            # Need to backtrack the last step on the stack
            if len(self.grid_copy) > 0:
                print(
                    f"Backtracked using snapshots. Snapshot stack length = {len(self.grid_copy)}"
                )
            else:
                print("No more states to backtrack to. Puzzle failed.")
                break

            # restore grid to pre-collapsed state
            old_cells, old_cell, old_cell_tile = self.grid_copy.pop()

            old_possible = np.nonzero(old_cell.possible)[0]
            choices = old_possible[old_possible != old_cell_tile]

            if len(choices) == 0:
                success = False
                continue

            # restore last good grid
            self.cells = copy.deepcopy(old_cells)

            # choose a new tile to collapse to
            new_choice = choice(choices)

            # try it out
            success = self.collapse_cell(old_cell, new_choice)

    def collapse_cell(self, next_cell, next_cell_tile):
        # Save state in case we need to backtrack
        self.grid_copy.append(
            [copy.deepcopy(self.cells), next_cell.copy(), next_cell_tile]       # TODO: append list of cell choices here, instead of next_cell_tile
        )

        next_cell.tile = self.tile_set.tiles[next_cell_tile]
        next_cell.possible[:] = False
        next_cell.possible[next_cell_tile] = True
        next_cell.is_collapsed = True
        return self.propagate(
            next_cell.x_pos // next_cell.width,
            next_cell.y_pos // next_cell.height,
            next_cell_tile,
        )

    def propagate(self, x_index: int, y_index: int, tile_id) -> bool:
        queue = deque([(y_index, x_index)])

        while queue:
            current_y, current_x = queue.popleft()
            source_cell = self.cells[current_y, current_x]
            source_possible = np.nonzero(source_cell.possible)[0]

            for idx, direction in enumerate(self.neighbours):
                neighbour_y = current_y + direction[0]
                neighbour_x = current_x + direction[1]

                if self.wrap:
                    if neighbour_x == self.width_in_cells:
                        neighbour_x = 0

                    if neighbour_y >= self.height_in_cells:
                        neighbour_y = 0
                else:
                    if (
                        neighbour_y < 0
                        or neighbour_y >= self.height_in_cells
                        or neighbour_x < 0
                        or neighbour_x >= self.width_in_cells
                    ):
                        continue

                neighbour = self.cells[neighbour_y, neighbour_x]
                if neighbour.is_collapsed:
                    continue

                valid_tiles = np.zeros(self.num_tiles, dtype=bool)
                for t_id in source_possible:
                    valid_tiles |= self.tile_set.adjacencies[t_id][idx]

                before = neighbour.possible.copy()
                neighbour.possible &= valid_tiles
                after = neighbour.possible

                if np.array_equal(before, after):
                    continue  # No change

                remaining = np.nonzero(after)[0]

                if len(remaining) == 0:
                    return False  # Contradiction

                elif len(remaining) == 1:
                    forced_tile = remaining[0]
                    neighbour.tile = self.tile_set.tiles[forced_tile]
                    neighbour.possible[:] = False
                    neighbour.possible[forced_tile] = True
                    neighbour.is_collapsed = True
                    queue.append((neighbour_y, neighbour_x))

                else:
                    queue.append((neighbour_y, neighbour_x))

        return True

    def get_lowest_entropy_cell(self) -> ndarray | None:
        u_cells = self.get_uncollapsed_cells()
        if len(u_cells) == 0:
            self.grid_copy = []
            self.finished = True
            print("Finished")
            return None     # we're done

        lowest_entropy_cell = sorted(u_cells, key=lambda obj: obj.possible.sum())[0]
        lowest_entropy_value = len(np.nonzero(lowest_entropy_cell.possible)[0])
        lowest_entropy_cells = u_cells[
            np.nonzero(np.vectorize(lambda c: len(np.nonzero(c.possible)[0]) == lowest_entropy_value)(u_cells))
        ]
        return choice(lowest_entropy_cells)

    def get_uncollapsed_cells(self) -> ndarray:
        return self.cells[np.nonzero(np.vectorize(lambda c: c.is_collapsed is False)(self.cells))]

    def draw(self, surface: pygame.Surface) -> None:
        for y in range(self.height_in_cells):
            for x in range(self.width_in_cells):
                average_colour = np.mean(np.array(self.tile_set.tiles)[self.cells[y, x].possible][:, 0, 0, :], axis=0)
                self.cells[y, x].draw(surface, average_colour)
