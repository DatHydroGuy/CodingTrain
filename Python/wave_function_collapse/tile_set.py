import os
import numpy as np
from PIL import Image
from tile import Tile


directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]     # (dy, dx)


class TileSet:
    def __init__(self, folder=None):
        self.tiles = []
        self.neighbours = []
        if folder is not None:
            self.read_tile_set(folder)
            self.get_illegal_neighbours()

    def __len__(self):
        return len(self.tiles)

    def add_tile(self, tile):
        self.tiles.append(tile)

    def tile_size(self):
        return self.tiles[0].pixels.shape[:2]

    def get_illegal_neighbours(self):
        for this_tile in self.tiles:
            for other_tile in self.tiles:
                for dy, dx in directions:
                    if dy == -1 and dx == 0:
                        meh = Tile.compare_edges(this_tile.north_pixels, other_tile.south_pixels)
                        if not meh:
                            this_tile.north_illegals.append(other_tile.id)
                    elif dy == 1 and dx == 0:
                        meh = Tile.compare_edges(this_tile.south_pixels, other_tile.north_pixels)
                        if not meh:
                            this_tile.south_illegals.append(other_tile.id)
                    elif dy == 0 and dx == 1:
                        meh = Tile.compare_edges(this_tile.east_pixels, other_tile.west_pixels)
                        if not meh:
                            this_tile.east_illegals.append(other_tile.id)
                    else:
                        meh = Tile.compare_edges(this_tile.west_pixels, other_tile.east_pixels)
                        if not meh:
                            this_tile.west_illegals.append(other_tile.id)

    def get_neighbouring_entropies(self, tile_id, dx, dy, tiles):
        curr_tile = self.tiles[tile_id]
        if dx == 0 and dy == -1:
            return [t for t in tiles if Tile.compare_edges(self.tiles[t].south_pixels, curr_tile.north_pixels)]
        elif dx == 1 and dy == 0:
            return [t for t in tiles if Tile.compare_edges(self.tiles[t].west_pixels, curr_tile.east_pixels)]
        elif dx == 0 and dy == 1:
            return [t for t in tiles if Tile.compare_edges(self.tiles[t].north_pixels, curr_tile.south_pixels)]
        else:
            return [t for t in tiles if Tile.compare_edges(self.tiles[t].east_pixels, curr_tile.west_pixels)]

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
