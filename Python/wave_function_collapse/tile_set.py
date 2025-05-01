import os
import numpy as np
from PIL import Image
from tile import Tile


class TileSet:
    def __init__(self, folder=None, colour_tolerance=0, match_ratio=1.0, max_mismatch_run=1):
        self.tiles = []
        self.neighbours = []
        if folder is not None:
            self.read_tile_set(folder)
            self.get_illegal_neighbours(colour_tolerance, match_ratio, max_mismatch_run)

    def __len__(self):
        return len(self.tiles)

    def add_tile(self, tile):
        self.tiles.append(tile)

    def tile_size(self):
        return self.tiles[0].pixels.shape[:2]

    def get_illegal_neighbours(self, colour_tolerance, match_ratio, max_mismatch_run):
        for this_tile in self.tiles:
            for other_tile in self.tiles:
                valid_neighbour = Tile.compare_edges(this_tile.north_pixels, other_tile.south_pixels, colour_tolerance, match_ratio, max_mismatch_run)
                if not valid_neighbour:
                    this_tile.north_illegals.append(other_tile.id)

                valid_neighbour = Tile.compare_edges(this_tile.south_pixels, other_tile.north_pixels, colour_tolerance, match_ratio, max_mismatch_run)
                if not valid_neighbour:
                    this_tile.south_illegals.append(other_tile.id)

                valid_neighbour = Tile.compare_edges(this_tile.east_pixels, other_tile.west_pixels, colour_tolerance, match_ratio, max_mismatch_run)
                if not valid_neighbour:
                    this_tile.east_illegals.append(other_tile.id)

                valid_neighbour = Tile.compare_edges(this_tile.west_pixels, other_tile.east_pixels, colour_tolerance, match_ratio, max_mismatch_run)
                if not valid_neighbour:
                    this_tile.west_illegals.append(other_tile.id)

    def read_tile_set(self, folder):
        id_num = 0
        for root, dirs, files in os.walk(folder):
            for filename in files:
                if filename.endswith('.png'):
                    orig_pixels = self.read_image_into_pixels(os.path.join(root, filename))
                    self.add_tile(Tile(orig_pixels, id_num))
                    id_num += 1
                    pixels = np.rot90(orig_pixels)
                    if not any([np.array_equal(pixels, tile.pixels) for tile in self.tiles]):
                        self.add_tile(Tile(pixels, id_num))
                        id_num += 1
                    pixels = np.rot90(pixels)
                    if not any([np.array_equal(pixels, tile.pixels) for tile in self.tiles]):
                        self.add_tile(Tile(pixels, id_num))
                        id_num += 1
                    pixels = np.rot90(pixels)
                    if not any([np.array_equal(pixels, tile.pixels) for tile in self.tiles]):
                        self.add_tile(Tile(pixels, id_num))
                        id_num += 1
                    pixels = np.flip(orig_pixels, axis=0)
                    if not any([np.array_equal(pixels, tile.pixels) for tile in self.tiles]):
                        self.add_tile(Tile(pixels, id_num))
                        id_num += 1
                    pixels = np.flip(orig_pixels, axis=1)
                    if not any([np.array_equal(pixels, tile.pixels) for tile in self.tiles]):
                        self.add_tile(Tile(pixels, id_num))
                        id_num += 1

    @staticmethod
    def read_image_into_pixels(image):
        img = Image.open(image).convert("RGB")
        img_np = np.array(img)
        return img_np
