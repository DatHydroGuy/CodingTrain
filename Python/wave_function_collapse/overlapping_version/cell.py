from random import random

import numpy as np
import pygame


class Cell:
    def __init__(self, x_pos: int, y_pos: int, width: int, height: int, adjacency_rules: np.ndarray, frequency_rules: np.ndarray) -> None:
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.adjacency_rules = adjacency_rules
        self.frequency_rules = frequency_rules
        self.possible = np.full(len(frequency_rules), True, dtype=np.bool_)
        self.weight_sum = self.total_possible_tile_frequency()
        self.weight_sum_log = np.sum(frequency_rules * np.log2(frequency_rules))
        self.tile = None
        self.entropy_noise = random() * 0.00001
        self.is_collapsed = False

    def set_tile(self, tile: np.ndarray) -> None:
        self.tile = tile

    def get_tile(self) -> np.ndarray:
        return self.tile

    # def get_tile_average(self) -> list[int]:
    #     return np.average(self.tile, axis=(0, 1)).astype(int)

    def remove_tile(self, tile_index: int) -> None:
        self.possible[tile_index] = False
        freq = self.frequency_rules[tile_index]
        self.weight_sum -= freq
        self.weight_sum_log -= float(freq) * np.log2(float(freq))

    def total_possible_tile_frequency(self) -> int:
        return np.sum(self.frequency_rules[self.possible])

    def choose_tile_index(self) -> np.ndarray:
        weights = self.frequency_rules[self.possible]
        total_weight = weights.sum()

        # pick random position in the list of possible tile indices
        remaining = random() * total_weight
        cumulative_weights = np.cumsum(weights)

        index = np.searchsorted(cumulative_weights, remaining, side="right")
        possible_indices = np.flatnonzero(self.possible)

        return possible_indices[index]

    # def relative_frequency(self, tile_index: int) -> np.ndarray:
    #     return self.frequency_rules[tile_index]

    def entropy(self) -> float:
        return np.log2(float(self.weight_sum)) - self.weight_sum_log / float(self.weight_sum)
        # total_weight = np.sum(self.frequency_rules[self.possible])
        # relative_frequencies = self.frequency_rules[self.possible].astype(float)
        # sum_weight_log_weight = np.sum(relative_frequencies * np.log2(relative_frequencies))
        #
        # return np.log2(total_weight) - (sum_weight_log_weight / total_weight)

    def draw(self, surface: pygame.Surface):
        colour = (0, 0, 0)

        if self.tile is not None:
            colour = self.tile[0, 0]

        pygame.draw.rect(surface, colour, (self.x_pos, self.y_pos, self.width, self.height))
