import copy
from random import choice
import pygame
import numpy as np
from collections import deque
from cell import Cell
from tile_set import TileSet


class Grid:
    def __init__(self, screen_size: tuple[int, int], grid_resolution: tuple[int, int], tile_set: TileSet, scaling: int=1, wrap: bool=False):
        self.screen_size = screen_size
        self.tile_set = tile_set
        self.width_in_cells = grid_resolution[0]
        self.height_in_cells = grid_resolution[1]
        self.cell_size = min(self.screen_size[0] // self.width_in_cells, self.screen_size[1] // self.height_in_cells)
        self.num_tiles = len(self.tile_set.tiles)
        self.scaling = scaling
        self.draw_size = (self.tile_set.kernel_size, self.tile_set.kernel_size)
        self.wrap = wrap
        self.cells = np.array([[Cell(x * self.cell_size, y * self.cell_size, self.cell_size, self.num_tiles) for x in range(self.width_in_cells)] for y in range(self.height_in_cells)])
        self.neighbours = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # N, S, W, E
        # Cache for backtracking - maybe a queue would be more efficient?
        self.grid_copy = []

    def step(self):
        next_cell = self.get_lowest_entropy_cell()

        if next_cell is None or next_cell.is_collapsed:     # should never be collapsed, just being defensive
            return

        # choose a tile to collapse to
        next_cell_tile = choice(np.nonzero(next_cell.possible)[0])

        # collapse the cell
        success = self.collapse_cell(next_cell, next_cell_tile)

        while not success:
            # Need to backtrack the last step on the stack
            if len(self.grid_copy) == 0:
                print("No more states to backtrack to. Puzzle failed.")
                break

            # restore grid to pre-collapsed state
            old_cells, old_cell, old_cell_tile = self.grid_copy.pop()

            old_possible = np.nonzero(old_cell.possible)[0]
            choices = old_possible[old_possible != old_cell_tile]

            if len(choices) == 0:
                print(
                    f"Backtracked using snapshots. Snapshot stack length = {len(self.grid_copy)}"
                )
                success = False
                continue

            # restore last good grid
            self.cells = old_cells.copy()

            # choose a new tile to collapse to
            new_choice = choice(choices)

            # try it out
            success = self.collapse_cell(old_cell, new_choice)

    def collapse_cell(self, next_cell, next_cell_tile):
        # Save state in case we need to backtrack
        self.grid_copy.append(
            [copy.deepcopy(self.cells), next_cell.copy(), next_cell_tile]
        )

        next_cell.tile = self.tile_set.tiles[next_cell_tile]
        next_cell.possible[:] = False
        next_cell.possible[next_cell_tile] = True
        next_cell.is_collapsed = True
        return self.propagate(next_cell.x_pos // next_cell.width, next_cell.y_pos // next_cell.height, next_cell_tile)

    def propagate(self, x_index: int, y_index: int, tile_id: int) -> bool:
        # Queue of cells to process (y, x)
        cell_tuple = [(y_index, x_index)]
        queue = deque(cell_tuple)

        # Track processed cells to avoid duplicates
        processed = set()

        while queue:
            current_y, current_x = queue.popleft()

            if (current_y, current_x) in processed:
                continue

            processed.add((current_y, current_x))

            # Remember: adjacencies are in the order North, South, West, East
            for idx, direction in enumerate(self.neighbours):
                ny = current_y + direction[0]
                nx = current_x + direction[1]

                if ny < 0 or ny >= self.height_in_cells or nx < 0 or nx >= self.width_in_cells:
                    continue

                if self.cells[ny, nx].is_collapsed:
                    continue

                # Always get all possibilities for the source cell
                current_possible_tiles = np.nonzero(
                    self.cells[current_y, current_x].possible
                )[0]

                valid_tiles = np.zeros(self.num_tiles, dtype=bool)
                for t_id in current_possible_tiles:
                    valid_tiles |= self.tile_set.adjacencies[t_id][idx]

                # Remove illegal neighbour options
                remaining_copy = np.copy(self.cells[ny, nx].possible)
                self.cells[ny, nx].possible &= valid_tiles
                remaining = np.nonzero(self.cells[ny, nx].possible)[0]

                if np.all(np.equal(self.cells[ny, nx].possible, remaining_copy)):
                    # No changes made to neighbour, so move on to next cell
                    continue

                if len(remaining) == 0:
                    # contradiction - need to backtrack, so return a failure
                    return False

                elif len(remaining) == 1:
                    # only 1 possibility, so collapse the cell without snapshotting
                    self.cells[ny, nx].tile = self.tile_set.tiles[remaining[0]]
                    self.cells[ny, nx].possible[:] = False
                    self.cells[ny, nx].possible[remaining[0]] = True
                    self.cells[ny, nx].is_collapsed = True
                    queue.append((ny, nx))

                else:
                    # Add neighbour to queue
                    if (ny, nx) not in processed:
                        queue.append((ny, nx))

        # if you get here, everything went well, so return a success
        return True

    def get_lowest_entropy_cell(self) -> Cell | None:
        u_cells = self.get_uncollapsed_cells()
        if len(u_cells) == 0:
            return None     # we're done

        lowest_entropy_cell = sorted(u_cells, key=lambda obj: obj.possible.sum())[0]
        lowest_entropy_value = len(np.nonzero(lowest_entropy_cell.possible)[0])
        lowest_entropy_cells = u_cells[
            np.nonzero(np.vectorize(lambda c: len(np.nonzero(c.possible)[0]) == lowest_entropy_value)(u_cells))
        ]
        return choice(lowest_entropy_cells)

    def get_uncollapsed_cells(self):
        return self.cells[np.nonzero(np.vectorize(lambda c: c.is_collapsed is False)(self.cells))]

    def draw(self, surface: pygame.Surface) -> None:
        for row in self.cells:
            for cell in row:
                cell.draw(surface)
