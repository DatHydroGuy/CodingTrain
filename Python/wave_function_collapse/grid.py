from copy import deepcopy
from random import choice
import pygame


class Grid:
    def __init__(self, screen_size, tile_set, width_in_cells, height_in_cells, scaling=1):
        self.screen_size = screen_size
        self.tile_set = tile_set
        self.width_in_cells = width_in_cells
        self.height_in_cells = height_in_cells
        self.cell_size = min(self.screen_size[0] // self.width_in_cells, self.screen_size[1] // self.height_in_cells)
        self.num_tiles = len(self.tile_set.tiles)
        self.tile_size = tile_set.tile_size()
        self.scaling = scaling
        self.draw_size = (self.tile_size[0] * self.scaling, self.tile_size[1] * self.scaling)
        self.max_manhattan = width_in_cells + height_in_cells - 1
        self.grid = [
            [
                {
                    'tile': None,
                    'entropy': [i for i in range(self.num_tiles)]
                 } for _ in range(self.width_in_cells)
            ]
            for _ in range(self.height_in_cells)
        ]
        self.grid_copy = []

    def collapse(self, x_index, y_index, tile_id, remaining_choices):
        success = self.collapse_tile(x_index, y_index, tile_id, remaining_choices)
        while not success:
            # Need to backtrack the last step on the stack
            # restore grid to pre-collapsed state
            old_grid, last_x, last_y, choices = self.grid_copy.pop()

            if len(choices) == 0:
                print(f"Backtracked using snapshots. Snapshot stack length = {len(self.grid_copy)}")
                success = False
                continue

            # ensure invalid tile value is not in the entropy list we're about to restore
            old_grid[y_index][x_index]['entropy'] = [n for n in old_grid[y_index][x_index]['entropy'] if n != tile_id]
            # restore last good grid
            self.grid = deepcopy(old_grid)
            # choose a new tile to collapse to
            new_choice = choice(choices)
            # try it out
            success = self.collapse_tile(x_index, y_index, new_choice, [n for n in choices if n != new_choice])

    def collapse_tile(self, x_index, y_index, tile_id, remaining_choices):
        self.grid_copy.append([deepcopy(self.grid), x_index, y_index, remaining_choices])
        self.grid[y_index][x_index]["tile"] = tile_id
        self.grid[y_index][x_index]['entropy'] = []
        return self.propagate(x_index, y_index, tile_id)

    def propagate(self, x_index, y_index, tile_id):
        for manhattan_dist in range(self.max_manhattan):

            for y in range(self.height_in_cells):
                y_diff = y - y_index
                if y_diff == 0:

                    for x in range(self.width_in_cells):
                        x_diff = x - x_index
                        if abs(y_diff) + abs(x_diff) != manhattan_dist:
                            continue

                        else:
                            if x_diff == 0:
                                # print(f"({x}, {y}) IS THE SAME CELL AS ({x_index}, {y_index})")
                                continue
                            elif x_diff > 0:
                                # print(f"({x}, {y}) is East of ({x_index}, {y_index})")
                                if manhattan_dist == 1:
                                    # remove illegal Eastern neighbours of grid[y_index][x_index] from grid[y][x]
                                    removals = self.tile_set.tiles[tile_id].east_illegals
                                    if type(self.grid[y][x]['tile']) is type(None):
                                        self.grid[y][x]["entropy"] = [x for x in self.grid[y][x]["entropy"] if x not in removals]
                                        if len(self.grid[y][x]['entropy']) == 0:
                                            return False
                                else:
                                    # remove all illegal Eastern neighbours of entropies in grid[y][x - 1] from grid[y][x]
                                    # if an entry is in ALL east illegals for all entropy values, then it's a valid removal.  If it's missing from even one, we keep it as a possible.
                                    illegals = [
                                        self.tile_set.tiles[entropy].east_illegals
                                        for entropy in self.grid[y][x - 1]["entropy"]
                                    ]
                                    removals = set.intersection(*[set(x) for x in illegals]) if len(illegals) > 0 else set()

                                    if type(self.grid[y][x]['tile']) is type(None):
                                        self.grid[y][x]["entropy"] = [x for x in self.grid[y][x]["entropy"] if x not in removals]
                                        if len(self.grid[y][x]['entropy']) == 0:
                                            return False
                            else:
                                # print(f"({x}, {y}) is West of ({x_index}, {y_index})")
                                if manhattan_dist == 1:
                                    # remove illegal Western neighbours of grid[y_index][x_index] from grid[y][x]
                                    removals = self.tile_set.tiles[tile_id].west_illegals
                                    if type(self.grid[y][x]['tile']) is type(None):
                                        self.grid[y][x]["entropy"] = [x for x in self.grid[y][x]["entropy"] if x not in removals]
                                        if len(self.grid[y][x]['entropy']) == 0:
                                            return False
                                else:
                                    # remove all illegal Western neighbours of entropies in grid[y][x + 1] from grid[y][x]
                                    # if an entry is in ALL west illegals for all entropy values, then it's a valid removal.  If it's missing from even one, we keep it as a possible.
                                    illegals = [
                                        self.tile_set.tiles[entropy].west_illegals
                                        for entropy in self.grid[y][x + 1]["entropy"]
                                    ]
                                    removals = set.intersection(*[set(x) for x in illegals]) if len(illegals) > 0 else set()

                                    if type(self.grid[y][x]['tile']) is type(None):
                                        self.grid[y][x]["entropy"] = [x for x in self.grid[y][x]["entropy"] if x not in removals]
                                        if len(self.grid[y][x]['entropy']) == 0:
                                            return False

                elif y_diff > 0:

                    for x in range(self.width_in_cells):
                        x_diff = x - x_index
                        if abs(y_diff) + abs(x_diff) != manhattan_dist:
                            continue

                        else:
                            if x_diff == 0:
                                # print(f"({x}, {y}) is South of ({x_index}, {y_index})")
                                if manhattan_dist == 1:
                                    # remove illegal Southern neighbours of grid[y_index][x_index] from grid[y][x]
                                    removals = self.tile_set.tiles[tile_id].south_illegals
                                    if type(self.grid[y][x]['tile']) is type(None):
                                        self.grid[y][x]["entropy"] = [x for x in self.grid[y][x]["entropy"] if x not in removals]
                                        if len(self.grid[y][x]['entropy']) == 0:
                                            return False
                                else:
                                    # remove all illegal Southern neighbours of entropies in grid[y - 1][x] from grid[y][x]
                                    # if an entry is in ALL south illegals for all entropy values, then it's a valid removal.  If it's missing from even one, we keep it as a possible.
                                    illegals = [
                                        self.tile_set.tiles[entropy].south_illegals
                                        for entropy in self.grid[y - 1][x]["entropy"]
                                    ]
                                    removals = set.intersection(*[set(x) for x in illegals]) if len(illegals) > 0 else set()

                                    if type(self.grid[y][x]['tile']) is type(None):
                                        self.grid[y][x]["entropy"] = [x for x in self.grid[y][x]["entropy"] if x not in removals]
                                        if len(self.grid[y][x]["entropy"]) == 0:
                                            return False

                            elif x_diff > 0:
                                # print(f"({x}, {y}) is South-East of ({x_index}, {y_index})")

                                # remove all illegal Southern neighbours of entropies in grid[y - 1][x] from grid[y][x]
                                south_illegals = [
                                    self.tile_set.tiles[entropy].south_illegals
                                    for entropy in self.grid[y - 1][x]["entropy"]
                                ]

                                # if an entry is in ALL south illegals for all entropy values, then it's a valid removal.  If it's missing from even one, we keep it as a possible.
                                south_removals = set.intersection(*[set(x) for x in south_illegals]) if len(south_illegals) > 0 else set()

                                # remove all illegal Eastern neighbours of entropies in grid[y][x - 1] from grid[y][x]
                                east_illegals = [
                                    self.tile_set.tiles[entropy].east_illegals
                                    for entropy in self.grid[y][x - 1]["entropy"]
                                ]

                                # if an entry is in ALL south illegals for all entropy values, then it's a valid removal.  If it's missing from even one, we keep it as a possible.
                                east_removals = set.intersection(*[set(x) for x in east_illegals]) if len(east_illegals) > 0 else set()

                                # if an entry is in either the south removal list OR the west removal list, we remove it
                                removals = set.union(set(south_removals), set(east_removals))

                                if type(self.grid[y][x]["tile"]) is type(None):
                                    self.grid[y][x]["entropy"] = [
                                        x
                                        for x in self.grid[y][x]["entropy"]
                                        if x not in removals
                                    ]
                                    if len(self.grid[y][x]["entropy"]) == 0:
                                        return False

                            else:
                                # print(f"({x}, {y}) is South-West of ({x_index}, {y_index})")
                                # remove all illegal Southern neighbours of entropies in grid[y - 1][x] from grid[y][x]
                                south_illegals = [
                                    self.tile_set.tiles[entropy].south_illegals
                                    for entropy in self.grid[y - 1][x]["entropy"]
                                ]

                                # if an entry is in ALL south illegals for all entropy values, then it's a valid removal.  If it's missing from even one, we keep it as a possible.
                                south_removals = set.intersection(*[set(x) for x in south_illegals]) if len(south_illegals) > 0 else set()

                                # remove all illegal Western neighbours of entropies in grid[y][x + 1] from grid[y][x]
                                west_illegals = [
                                    self.tile_set.tiles[entropy].west_illegals
                                    for entropy in self.grid[y][x + 1]["entropy"]
                                ]

                                # if an entry is in ALL south illegals for all entropy values, then it's a valid removal.  If it's missing from even one, we keep it as a possible.
                                west_removals = set.intersection(*[set(x) for x in west_illegals]) if len(west_illegals) > 0 else set()

                                # if an entry is in either the south removal list OR the west removal list, we remove it
                                removals = set.union(set(south_removals), set(west_removals))

                                if type(self.grid[y][x]["tile"]) is type(None):
                                    self.grid[y][x]["entropy"] = [
                                        x
                                        for x in self.grid[y][x]["entropy"]
                                        if x not in removals
                                    ]
                                    if len(self.grid[y][x]["entropy"]) == 0:
                                        return False

                else:

                    for x in range(self.width_in_cells):
                        x_diff = x - x_index
                        if abs(y_diff) + abs(x_diff) != manhattan_dist:
                            continue

                        else:
                            if x_diff == 0:
                                # print(f"({x}, {y}) is North of ({x_index}, {y_index})")
                                if manhattan_dist == 1:
                                    # remove illegal Northern neighbours of grid[y_index][x_index] from grid[y][x]
                                    removals = self.tile_set.tiles[tile_id].north_illegals
                                    if type(self.grid[y][x]['tile']) is type(None):
                                        self.grid[y][x]["entropy"] = [x for x in self.grid[y][x]["entropy"] if x not in removals]
                                        if len(self.grid[y][x]['entropy']) == 0:
                                            return False
                                else:
                                    # remove all illegal Northern neighbours of entropies in grid[y + 1][x] from grid[y][x]
                                    # if an entry is in ALL north illegals for all entropy values, then it's a valid removal.  If it's missing from even one, we keep it as a possible.
                                    illegals = [
                                        self.tile_set.tiles[entropy].north_illegals
                                        for entropy in self.grid[y + 1][x]["entropy"]
                                    ]
                                    removals = set.intersection(*[set(x) for x in illegals]) if len(illegals) > 0 else set()

                                    if type(self.grid[y][x]['tile']) is type(None):
                                        self.grid[y][x]["entropy"] = [x for x in self.grid[y][x]["entropy"] if x not in removals]
                                        if len(self.grid[y][x]['entropy']) == 0:
                                            return False

                            elif x_diff > 0:
                                # print(f"({x}, {y}) is North-East of ({x_index}, {y_index})")
                                # remove all illegal Northern neighbours of entropies in grid[y + 1][x] from grid[y][x]
                                north_illegals = [
                                    self.tile_set.tiles[entropy].north_illegals
                                    for entropy in self.grid[y + 1][x]["entropy"]
                                ]

                                # if an entry is in ALL north illegals for all entropy values, then it's a valid removal.  If it's missing from even one, we keep it as a possible.
                                north_removals = set.intersection(*[set(x) for x in north_illegals]) if len(north_illegals) > 0 else set()

                                # remove all illegal Eastern neighbours of entropies in grid[y][x - 1] from grid[y][x]
                                east_illegals = [
                                    self.tile_set.tiles[entropy].east_illegals
                                    for entropy in self.grid[y][x - 1]["entropy"]
                                ]

                                # if an entry is in ALL north illegals for all entropy values, then it's a valid removal.  If it's missing from even one, we keep it as a possible.
                                east_removals = set.intersection(*[set(x) for x in east_illegals]) if len(east_illegals) > 0 else set()

                                # if an entry is in either the north removal list OR the east removal list, we remove it
                                removals = set.union(set(north_removals), set(east_removals))

                                if type(self.grid[y][x]["tile"]) is type(None):
                                    self.grid[y][x]["entropy"] = [
                                        x
                                        for x in self.grid[y][x]["entropy"]
                                        if x not in removals
                                    ]
                                    if len(self.grid[y][x]["entropy"]) == 0:
                                        return False

                            else:
                                # print(f"({x}, {y}) is North-West of ({x_index}, {y_index})")
                                # remove all illegal Northern neighbours of entropies in grid[y + 1][x] from grid[y][x]
                                north_illegals = [
                                    self.tile_set.tiles[entropy].north_illegals
                                    for entropy in self.grid[y + 1][x]["entropy"]
                                ]

                                # if an entry is in ALL north illegals for all entropy values, then it's a valid removal.  If it's missing from even one, we keep it as a possible.
                                north_removals = set.intersection(*[set(x) for x in north_illegals]) if len(north_illegals) > 0 else set()

                                # remove all illegal Western neighbours of entropies in grid[y][x + 1] from grid[y][x]
                                west_illegals = [
                                    self.tile_set.tiles[entropy].west_illegals
                                    for entropy in self.grid[y][x + 1]["entropy"]
                                ]

                                # if an entry is in ALL north illegals for all entropy values, then it's a valid removal.  If it's missing from even one, we keep it as a possible.
                                west_removals = set.intersection(*[set(x) for x in west_illegals]) if len(west_illegals) > 0 else set()

                                # if an entry is in either the north removal list OR the west removal list, we remove it
                                removals = set.union(set(north_removals), set(west_removals))

                                if type(self.grid[y][x]["tile"]) is type(None):
                                    self.grid[y][x]["entropy"] = [
                                        x
                                        for x in self.grid[y][x]["entropy"]
                                        if x not in removals
                                    ]
                                    if len(self.grid[y][x]["entropy"]) == 0:
                                        return False
        return True

    def get_lowest_entropy_cell(self):
        lowest = []
        for y in range(self.height_in_cells):
            for x in range(self.width_in_cells):
                if type(self.grid[y][x]['tile']) is not type(None):
                    continue

                if len(lowest) == 0 or len(self.grid[y][x]['entropy']) < len(self.grid[lowest[0][0]][lowest[0][1]]['entropy']):
                    lowest = [(y, x)]
                elif len(self.grid[y][x]["entropy"]) == len(
                    self.grid[lowest[0][0]][lowest[0][1]]["entropy"]
                ):
                    lowest.append((y, x))

        if len(lowest) == 0:
            # print("Finished!")
            return None, None
        elif len(lowest) == 1:
            return lowest[0]
        else:
            return choice(lowest)

    def draw(self, surface, debugging=False):
        for y in range(self.height_in_cells):
            for x in range(self.width_in_cells):
                pygame.draw.rect(surface, (100, 100, 100), (x * self.draw_size[1], y * self.draw_size[0], self.draw_size[1], self.draw_size[0]), 1)
                if type(self.grid[y][x]['tile']) is not type(None):
                    self.tile_set.tiles[self.grid[y][x]['tile']].draw(surface, x * self.draw_size[1], y * self.draw_size[0], self.scaling)
                else:
                    if debugging:
                        # note that these are hard-coded values for debugging the tileset "Circuit" containing 14 tiles on a 1400x1050 screen with 4 horizontal cells and 3 vertical cells
                        for candidate in self.grid[y][x]["entropy"]:
                            c_x = candidate % 4
                            c_y = candidate // 4
                            self.tile_set.tiles[candidate].draw(
                                surface,
                                x * self.draw_size[1] + c_x * self.cell_size // 4 + 9,
                                y * self.draw_size[0] + c_y * self.cell_size // 4 + 9,
                                5  #self.scaling,
                            )
