import numpy as np
from numba import jit, prange, types
from numba.typed import Dict


class Adjacencies:
    def __init__(self, all_tiles: list[np.ndarray]) -> None:
        # Stack all tiles into a single numpy array for efficient processing
        self.tiles = np.stack(all_tiles)
        self.length = len(all_tiles)
        self.allowed = np.full((self.length, 4, self.length), False, dtype=np.bool_)
        print(f"Creating {self.length} Adjacency rules")

        # Pre-compute all hashes using vectorized operations
        hashes = self._compute_all_hashes_vectorized(self.tiles)

        # Use numba-compiled function for the main computation
        self.allowed = self._compute_adjacency_rules_numba(
            self.tiles, hashes, self.allowed
        )

        print("Adjacency rules created")

    def _compute_all_hashes_vectorized(self, tiles: np.ndarray) -> np.ndarray:
        """Compute hashes for all tiles using vectorized operations."""
        # Reshape tiles to 2D for easier processing
        flat_tiles = tiles.reshape(tiles.shape[0], -1)

        # Use a simple but fast hash based on array content
        # This assumes tiles are small enough that hash collisions are rare
        return np.array([hash(tile.tobytes()) for tile in flat_tiles])

    @staticmethod
    @jit(nopython=True, parallel=True, cache=True)
    def _compute_adjacency_rules_numba(tiles, hashes, allowed):
        """Numba-compiled function for computing adjacency rules."""
        length = tiles.shape[0]
        opposite = np.array([1, 0, 3, 2])  # Opposite directions for N,S,W,E

        # Pre-allocate cache arrays for numba compatibility
        max_cache_size = length * length * 4
        cache_keys = np.zeros((max_cache_size, 3), dtype=np.int64)
        cache_values = np.zeros(max_cache_size, dtype=np.bool_)
        cache_count = 0

        for i in prange(length):
            for j in range(i, length):
                for direction in range(4):
                    # Check cache first
                    cache_key = (hashes[i], hashes[j], direction)
                    cached_result = False
                    found_in_cache = False

                    # Simple linear search in cache (could be optimized further)
                    for k in range(cache_count):
                        if (
                            cache_keys[k, 0] == cache_key[0]
                            and cache_keys[k, 1] == cache_key[1]
                            and cache_keys[k, 2] == cache_key[2]
                        ):
                            cached_result = cache_values[k]
                            found_in_cache = True
                            break

                    if not found_in_cache:
                        # Compute compatibility
                        cached_result = get_valid_adjacencies(tiles[i], tiles[j], direction)

                        # Add to cache
                        if cache_count < max_cache_size:
                            cache_keys[cache_count, 0] = cache_key[0]
                            cache_keys[cache_count, 1] = cache_key[1]
                            cache_keys[cache_count, 2] = cache_key[2]
                            cache_values[cache_count] = cached_result
                            cache_count += 1

                    if cached_result:
                        allowed[i, direction, j] = True
                        allowed[j, opposite[direction], i] = True

        return allowed


@jit(nopython=True, cache=True)
def get_valid_adjacencies(tile_a, tile_b, direction):
    """
    Numba-compiled compatibility function.
    You'll need to adapt this to your specific compatibility logic.
    This is a placeholder implementation.
    """
    # Example: Check if adjacent edges match
    # Direction: 0=North, 1=South, 2=West, 3=East

    if direction == 0:  # North
        return np.array_equal(tile_a[:2, :], tile_b[-2:, :])
    elif direction == 1:  # South
        return np.array_equal(tile_a[-2:, :], tile_b[:2, :])
    elif direction == 2:  # West
        return np.array_equal(tile_a[:, :2], tile_b[:, -2:])
    else:  # East
        return np.array_equal(tile_a[:, -2:], tile_b[:, :2])


class Frequencies:
    def __init__(self, all_tiles: list[np.ndarray]) -> None:
        print(f"Creating {len(all_tiles)} Frequency rules")

        # Stack into a 3D array: shape (N, H, W)
        stacked = np.stack(all_tiles)

        # Use the fastest method based on tile characteristics
        if self._should_use_hash_method(stacked):
            self.rules = self._compute_frequencies_hash(stacked)
        else:
            self.rules = self._compute_frequencies_numpy(stacked)

        print(f"Frequency rules created")

    def _should_use_hash_method(self, stacked: np.ndarray) -> bool:
        """Determine whether to use hash-based or numpy-based method."""
        # Hash method is typically faster for larger tiles or when many duplicates expected
        total_elements = stacked.size
        return total_elements > 10000 or stacked.shape[0] > 100

    def _compute_frequencies_numpy(self, stacked: np.ndarray) -> np.ndarray:
        """Original numpy-based method, optimised."""
        # Use a more efficient reshape that maintains memory layout
        flattened = stacked.reshape(stacked.shape[0], -1)

        # Optimise numpy.unique call with specific parameters
        _, inverse_indices, counts = np.unique(
            flattened,
            axis=0,
            return_inverse=True,
            return_counts=True,
            equal_nan=False,  # Slight performance boost if no NaNs expected
        )

        return counts[inverse_indices]

    def _compute_frequencies_hash(self, stacked: np.ndarray) -> np.ndarray:
        """Hash-based method for potentially better performance on large datasets."""
        # Convert to bytes for fast hashing
        tile_hashes = np.array([hash(tile.tobytes()) for tile in stacked])

        # Use numba for the counting
        return self._count_frequencies_numba(tile_hashes)

    @staticmethod
    @jit(nopython=True, cache=True)
    def _count_frequencies_numba(hashes: np.ndarray) -> np.ndarray:
        """Numba-compiled frequency counting."""
        # Create a simple hash->count mapping
        unique_hashes = np.unique(hashes)
        hash_to_count = Dict.empty(key_type=types.int64, value_type=types.int64)

        # Count occurrences
        for hash_val in hashes:
            if hash_val in hash_to_count:
                hash_to_count[hash_val] += 1
            else:
                hash_to_count[hash_val] = 1

        # Map back to original order
        result = np.zeros(len(hashes), dtype=np.int64)
        for i in range(len(hashes)):
            result[i] = hash_to_count[hashes[i]]

        return result

    # Optimised method with type hints and potential caching
    def relative_frequency(self, tile_index: int) -> int:
        """
        Returns the number of times the corresponding tile appears in the input.
        This corresponds to the weight of a possibility in the simplified entropy equation.
        """
        return int(self.rules[tile_index])  # Convert to Python int for consistency


class EnablerCounts:
    def __init__(self, grid_shape: tuple[int, int], num_tiles: int, adjacency_rules: np.ndarray):
        self.height, self.width = grid_shape
        self.num_tiles = num_tiles
        self.adjacency_rules = adjacency_rules
        self.enablers = np.zeros((self.height, self.width, 4, num_tiles), dtype=np.int32)
        self._initialise_enablers()

    def _initialise_enablers(self):
        """Initialise enabler counts assuming all tiles are possible everywhere."""
        for y in range(self.height):
            for x in range(self.width):
                for direction in range(4):
                    for t in range(self.num_tiles):
                        # Count how many tiles can support tile t from this direction
                        allowed = self.adjacency_rules[t, direction]
                        self.enablers[y, x, direction, t] = np.count_nonzero(allowed)

    def get_enabler_count(self, y: int, x: int, direction: int, tile_index: int) -> int:
        return self.enablers[y, x, direction, tile_index]

    def decrement(self, y: int, x: int, direction: int, tile_index: int):
        self.enablers[y, x, direction, tile_index] -= 1

    def is_enabled(self, y: int, x: int, tile_index: int) -> bool:
        """Check if tile is still enabled in all directions."""
        return np.all(self.enablers[y, x, :, tile_index] > 0)

    def disable_tile(self, y: int, x: int, tile_index: int):
        self.enablers[y, x, :, tile_index] = 0
