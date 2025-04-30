import numpy as np
import pygame


class Tile:
    def __init__(self, pixels, id_number):
        self.pixels = pixels
        self.id = id_number
        self.north_pixels = None
        self.west_pixels = None
        self.south_pixels = None
        self.east_pixels = None
        self.north_illegals = []
        self.east_illegals = []
        self.south_illegals = []
        self.west_illegals = []
        self.set_edge_pixels()

    def set_edge_pixels(self):
        self.set_north_edge_pixels()
        self.set_south_edge_pixels()
        self.set_west_edge_pixels()
        self.set_east_edge_pixels()

    def set_north_edge_pixels(self):
        self.north_pixels = self.pixels[0, :]

    def set_east_edge_pixels(self):
        self.east_pixels = self.pixels[:, -1]

    def set_south_edge_pixels(self):
        # self.south_pixels = self.pixels[-1, ::-1]
        self.south_pixels = self.pixels[-1, :]

    def set_west_edge_pixels(self):
        # self.west_pixels = self.pixels[::-1, 0]
        self.west_pixels = self.pixels[:, 0]

    def draw(self, surface, top_left_x, top_left_y, scaling):
        for ty in range(self.pixels.shape[0]):
            for tx in range(self.pixels.shape[1]):
                pygame.draw.rect(
                    surface,
                    self.pixels[ty, tx],
                    (
                        top_left_x + tx * scaling,
                        top_left_y + ty * scaling,
                        scaling,
                        scaling,
                    ),
                    0,
                )

    # Circuit:     def compare_edges(edge_a, edge_b, colour_tolerance=10, match_ratio=0.7, max_mismatch_run=1):
    @staticmethod
    def compare_edges(edge_a, edge_b, colour_tolerance=20, match_ratio=0.5, max_mismatch_run=1):
        # Absolute difference per channel
        diff = np.abs(edge_a.astype(int) - edge_b.astype(int))

        # A pixel matches if all RGB channels are within tolerance
        # tolerance_array = np.array([colour_tolerance, colour_tolerance, colour_tolerance])
        # pixel_matches = [all(d <= tolerance_array) for d in diff]
        pixel_matches = np.all(diff <= colour_tolerance, axis=1)

        # Count how many pixels matched
        match_fraction = np.count_nonzero(pixel_matches) / len(edge_a)

        # Limit number of consecutive mismatched pixels
        max_run = Tile.max_consecutive_false(pixel_matches)

        return match_fraction >= match_ratio and max_run <= max_mismatch_run

    @staticmethod
    def max_consecutive_false(mask):
        max_run = run = 0
        for val in mask:
            if val:
                run = 0
            else:
                run += 1
                max_run = max(max_run, run)
        return max_run
