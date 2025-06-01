from typing import AnyStr
import numpy as np
from PIL import Image
from numpy import ndarray, dtype
from helpers import Adjacencies, Frequencies


class TileSet:
    def __init__(self, source_file: AnyStr, kernel_size: int = 3, include_rotated_kernels: bool=False, include_flipped_kernels: bool=False):
        self.pixels = self.read_source_file(source_file)
        self.kernel_size = kernel_size
        self.tiles = []
        self.create_tiles(include_rotated_kernels, include_flipped_kernels)
        self.adjacencies = Adjacencies(self.tiles).allowed
        self.frequencies = Frequencies(self.tiles).rules

    def create_tiles(self, include_rotated_kernels: bool=False, include_flipped_kernels: bool=False) -> None:

        for y in range(self.pixels.shape[0]):
            cols = [(y + dy) % self.pixels.shape[0] for dy in range(self.kernel_size)]

            for x in range(self.pixels.shape[1]):
                rows = [(x + dx) % self.pixels.shape[1] for dx in range(self.kernel_size)]

                tile_pixels = self.pixels[np.ix_(cols, rows)]
                self.tiles.append(tile_pixels)

                if include_rotated_kernels:
                    self.add_kernel_rotations(tile_pixels)

                if include_flipped_kernels:
                    tile_pixels = np.flip(tile_pixels, axis=0)
                    self.tiles.append(tile_pixels)

                    if include_rotated_kernels:
                        self.add_kernel_rotations(tile_pixels)

    def add_kernel_rotations(self, kernel_pixels: ndarray) -> None:
        self.tiles.append(np.rot90(kernel_pixels, 1))
        self.tiles.append(np.rot90(kernel_pixels, 2))
        self.tiles.append(np.rot90(kernel_pixels, 3))

    @staticmethod
    def read_source_file(source_file: AnyStr) -> ndarray[tuple[int, ...], dtype[int]] | None:
        if str(source_file).endswith(".png"):
            img = Image.open(source_file).convert("RGB")
            return np.array(img)

        raise TypeError("source_file must be a valid PNG image")
