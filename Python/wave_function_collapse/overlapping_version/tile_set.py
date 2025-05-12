import numpy as np
from PIL import Image
from tile import Tile


class TileSet:
    def __init__(self, source_file=None, tile_size=3):
        self.tiles = []
        self.tile_size = (tile_size, tile_size)
        if source_file is not None:
            self.read_tile_set(source_file, tile_size)
            self.get_illegal_neighbours()

    def __len__(self):
        return len(self.tiles)

    def add_tile(self, tile):
        self.tiles.append(tile)

    # def tile_size(self):
    #     return self.tiles[0].pixels.shape[:2]

    def get_illegal_neighbours(self):
        for this_tile in self.tiles:
            for other_tile in self.tiles:
                valid_neighbour = Tile.compare_edges(this_tile.north_pixels, other_tile.south_pixels)
                if not valid_neighbour:
                    this_tile.north_illegals.append(other_tile.id)

                valid_neighbour = Tile.compare_edges(this_tile.south_pixels, other_tile.north_pixels)
                if not valid_neighbour:
                    this_tile.south_illegals.append(other_tile.id)

                valid_neighbour = Tile.compare_edges(this_tile.east_pixels, other_tile.west_pixels)
                if not valid_neighbour:
                    this_tile.east_illegals.append(other_tile.id)

                valid_neighbour = Tile.compare_edges(this_tile.west_pixels, other_tile.east_pixels)
                if not valid_neighbour:
                    this_tile.west_illegals.append(other_tile.id)

    def read_tile_set(self, file_name, tile_size):
        id_num = 0
        if file_name.endswith('.png'):
            orig_pixels = self.read_image_into_pixels(file_name)
            for y in range(orig_pixels.shape[0]):
                cols = [(y + dy) % orig_pixels.shape[0] for dy in range(tile_size)]
                for x in range(orig_pixels.shape[1]):
                    rows = [(x + dx) % orig_pixels.shape[1] for dx in range(tile_size)]
                    self.add_tile(Tile(orig_pixels[np.ix_(cols, rows)], id_num))
                    id_num += 1
                    # id_num, pixels = self.add_tile_rotation(id_num, orig_pixels)
                    # id_num, pixels = self.add_tile_rotation(id_num, pixels)
                    # id_num, pixels = self.add_tile_rotation(id_num, pixels)
                    # pixels = np.flip(orig_pixels, axis=0)
                    # self.add_tile(Tile(pixels, id_num))
                    # id_num += 1
                    # id_num, pixels = self.add_tile_rotation(id_num, pixels)
                    # id_num, pixels = self.add_tile_rotation(id_num, pixels)
                    # id_num, pixels = self.add_tile_rotation(id_num, pixels)

    def add_tile_rotation(self, id_num, orig_pixels):
        pixels = np.rot90(orig_pixels)
        self.add_tile(Tile(pixels, id_num))
        id_num += 1
        return id_num, pixels

    @staticmethod
    def read_image_into_pixels(image):
        img = Image.open(image).convert("RGB")
        img_np = np.array(img)
        return img_np
