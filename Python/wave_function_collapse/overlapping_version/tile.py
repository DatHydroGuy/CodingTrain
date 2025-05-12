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
        self.north_pixels = self.pixels[:2, :]

    def set_east_edge_pixels(self):
        self.east_pixels = self.pixels[:, -2:]

    def set_south_edge_pixels(self):
        self.south_pixels = self.pixels[-2:, :]

    def set_west_edge_pixels(self):
        self.west_pixels = self.pixels[:, :2]

    def draw(self, surface, top_left_x, top_left_y):
        # Transpose pixel array from (H, W, C) to (W, H, C)
        blit_array = np.transpose(self.pixels, (1, 0, 2))

        # Create a pygame surface from the numpy array
        temp_surface = pygame.Surface((blit_array.shape[0], blit_array.shape[1]))

        # Faster way to transfer numpy data to pygame surface
        pygame.surfarray.blit_array(temp_surface, blit_array)

        # Scale and blit
        scaled = pygame.transform.scale(temp_surface, (blit_array.shape[0], blit_array.shape[1]))
        surface.blit(scaled, (top_left_x, top_left_y))

    @staticmethod
    def compare_edges(edge_a, edge_b, colour_tolerance=20, match_ratio=0.5, max_mismatch_run=1):
        matched = np.zeros(edge_a.shape, dtype=np.uint32)

        # Absolute difference per channel
        diff = np.abs(edge_a.astype(int) - edge_b.astype(int))

        differences = np.equal(matched, diff)

        return np.all(differences)

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
