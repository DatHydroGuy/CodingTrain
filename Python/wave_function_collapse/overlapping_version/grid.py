from random import choice
import pygame
import numpy as np
from collections import deque


class Grid:
    def __init__(self, screen_size, tile_set, width_in_cells, height_in_cells, scaling=1, wrap=False):
        self.screen_size = screen_size
        self.tile_set = tile_set
        self.width_in_cells = width_in_cells
        self.height_in_cells = height_in_cells
        self.cell_size = min(self.screen_size[0] // self.width_in_cells, self.screen_size[1] // self.height_in_cells)
        self.num_tiles = len(self.tile_set.tiles)
        self.tile_size = tile_set.tile_size
        self.scaling = scaling
        self.draw_size = (self.tile_size[0], self.tile_size[1])
        self.wrap = wrap

        # Optimise grid structure with numpy arrays
        # -1 indicates not collapsed (no tile assigned)
        self.tiles = np.full((self.height_in_cells, self.width_in_cells), -1, dtype=np.int32)

        # Use boolean array for entropy - faster than lists
        # Shape: [height, width, num_tiles]
        self.entropy = np.ones((self.height_in_cells, self.width_in_cells, self.num_tiles), dtype=bool)

        # Cache for backtracking - maybe a queue would be more efficient?
        self.grid_copy = []

        # Precompute neighbour co-ordinates for faster access
        self.directions = [
            (-1, 0),  # North
            (0, 1),   # East
            (1, 0),   # South
            (0, -1),  # West
        ]

        # Precompute direction to illegal_list mapping
        self.direction_to_illegals = [
            lambda tile: self.tile_set.tiles[tile].north_illegals,  # North
            lambda tile: self.tile_set.tiles[tile].east_illegals,   # East
            lambda tile: self.tile_set.tiles[tile].south_illegals,  # South
            lambda tile: self.tile_set.tiles[tile].west_illegals,   # West
        ]

    def collapse(self, x_index, y_index, tile_id, remaining_choices):
        success = self.collapse_tile(x_index, y_index, tile_id, remaining_choices)
        while not success:
            # Need to backtrack the last step on the stack
            # restore grid to pre-collapsed state
            old_tiles, old_entropy, last_x, last_y, choices = self.grid_copy.pop()

            if len(choices) == 0:
                print(f"Backtracked using snapshots. Snapshot stack length = {len(self.grid_copy)}")
                success = False
                continue

            # restore last good grid
            self.tiles = old_tiles.copy()
            self.entropy = old_entropy.copy()

            # choose a new tile to collapse to
            new_choice = choice(choices)

            # try it out
            success = self.collapse_tile(x_index, y_index, new_choice, [n for n in choices if n != new_choice])

    def collapse_tile(self, x_index, y_index, tile_id, remaining_choices):
        # Save state in case we need to backtrack
        self.grid_copy.append([self.tiles.copy(), self.entropy.copy(), x_index, y_index, remaining_choices])

        # Collapse the current cell
        self.tiles[y_index, x_index] = tile_id
        self.entropy[y_index, x_index][:] = False
        self.entropy[y_index, x_index][tile_id] = True

        # Propagate the collapse across the grid
        return self.propagate(x_index, y_index, tile_id)

    def propagate(self, x_index, y_index, tile_id):
        # Queue of cells to process (y, x)
        cell_tuple = [(y_index, x_index)]
        queue = deque(cell_tuple)

        # Track processed cells to avoid duplicates
        processed = set()

        # Changed propagation method from Manhattan distance to a queue of cells within the grid
        while queue:
            current_y, current_x = queue.popleft()

            if (current_y, current_x) in processed:
                continue

            processed.add((current_y, current_x))

            current_tile = self.tiles[current_y, current_x]

            # For each neighbour direction
            for direction_number, (y_diff, x_diff) in enumerate(self.directions):
                neighbour_y, neighbour_x = current_y + y_diff, current_x + x_diff

                if self.wrap:
                    if neighbour_x == self.width_in_cells:
                        neighbour_x = 0

                    if neighbour_y >= self.height_in_cells:
                        neighbour_y = 0
                else:
                    # Skip if outside bounds
                    if not (0 <= neighbour_y < self.height_in_cells and 0 <= neighbour_x < self.width_in_cells):
                        continue

                # If current cell is collapsed, remove incompatible neighbours
                if current_tile != -1:
                    # Get illegal tiles in this direction
                    illegals = self.direction_to_illegals[direction_number](current_tile)

                    # If neighbour isn't collapsed yet
                    if self.tiles[neighbour_y, neighbour_x] == -1:
                        # Remove illegal options
                        if not self.apply_constraints(neighbour_x, neighbour_y, illegals, queue, processed):
                            return False

                else:
                    # Current cell not collapsed, constrain based on possible valid tiles
                    possible_tiles = np.where(self.entropy[current_y, current_x])[0]

                    # If neighbour not collapsed, constrain based on all possible tiles
                    if self.tiles[neighbour_y, neighbour_x] == -1:
                        # Get all illegals for this direction from all possible tiles
                        all_illegals = []
                        for tile in possible_tiles:
                            all_illegals.append(
                                set(self.direction_to_illegals[direction_number](tile))
                            )

                        # Find common illegals (tiles illegal for ALL possible configurations)
                        if all_illegals:
                            common_illegals = set.intersection(*all_illegals)

                            # Apply constraints
                            if not self.apply_constraints(neighbour_x, neighbour_y, common_illegals, queue, processed):
                                return False

        return True  # No contradictions found

    def apply_constraints(self, neighbour_x, neighbour_y, illegals, queue, processed):
        changed = False

        # Remove illegal neighbour options
        for illegal in illegals:
            if self.entropy[neighbour_y, neighbour_x, illegal]:
                self.entropy[neighbour_y, neighbour_x, illegal] = False
                changed = True

        # If changes were made, check for contradictions and add to queue
        if changed:
            # Check if this cell still has valid options
            if not np.any(self.entropy[neighbour_y, neighbour_x]):
                return False  # Contradiction

            # If only one option left, collapse it
            if np.sum(self.entropy[neighbour_y, neighbour_x]) == 1:
                tile_id = np.where(self.entropy[neighbour_y, neighbour_x])[0][0]
                self.tiles[neighbour_y, neighbour_x] = tile_id

            # Add neighbour to queue
            if (neighbour_y, neighbour_x) not in processed:
                queue.append((neighbour_y, neighbour_x))

        return True

    def get_lowest_entropy_cell(self):

        # Get all uncollapsed cells
        uncollapsed = np.where(self.tiles == -1)
        if len(uncollapsed[0]) == 0:
            return None, None

        # Count entropy (number of possibilities) for each uncollapsed cell
        entropy_counts = np.sum(self.entropy[uncollapsed], axis=1)

        # Find the minimum entropy value
        min_entropy = np.min(entropy_counts)

        # Get all cells with minimum entropy
        min_indices = np.where(entropy_counts == min_entropy)[0]

        # Choose randomly from cells with minimum entropy
        if len(min_indices) == 0:
            return None, None

        choice_index = choice(min_indices)
        y, x = uncollapsed[0][choice_index], uncollapsed[1][choice_index]

        return y, x

    def draw(self, surface):
        for y in range(self.height_in_cells):
            for x in range(self.width_in_cells):
                pygame.draw.rect(
                    surface,
                    (100, 100, 100),
                    (
                        x * self.draw_size[1],
                        y * self.draw_size[0],
                        self.draw_size[1],
                        self.draw_size[0],
                    ),
                    1,
                )
                if self.tiles[y, x] != -1:
                    self.tile_set.tiles[self.tiles[y, x]].draw(
                        surface,
                        x * self.draw_size[1],
                        y * self.draw_size[0],
                    )
