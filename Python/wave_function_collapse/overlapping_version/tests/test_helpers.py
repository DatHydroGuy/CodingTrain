import math

import numpy as np
import pytest

from helpers import (
    Adjacencies,
    Frequencies,
    get_valid_adjacencies,
    EnablerCounts,
)


class TestAdjacencies:
    @pytest.fixture
    def setup(self):
        self.num_tiles = 5000
        self.tile_data = [np.ones((3, 3)) for _ in range(self.num_tiles)]

    @pytest.fixture
    def mock_compat(self, monkeypatch):
        def mock_compatible(tile_a, tile_b, direction):
            return True

        monkeypatch.setattr(Adjacencies, "compatible", staticmethod(mock_compatible))

    def test_initialise_adjacencies_sets_length(self, setup):#, mock_compat):
        # Arrange

        # Act
        adj = Adjacencies(self.tile_data)

        # Act
        assert adj.length == self.num_tiles

    def test_initialise_adjacencies_initialises_adjacency_rules(self, setup):
        # Arrange

        # Act
        adj = Adjacencies(self.tile_data)

        # Act
        assert type(adj.allowed) is np.ndarray
        assert adj.allowed.shape == (self.num_tiles, 4, self.num_tiles)
        assert np.all(adj.allowed == True)

    def test_initialise_adjacencies_creates_adjacency_rules(self):
        # Arrange
        tile = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        match_north = np.array([[7, 8, 9], [1, 2, 3], [4, 5, 6]])
        match_south = np.array([[4, 5, 6], [7, 8, 9], [1, 2, 3]])
        match_west = np.array([[3, 1, 2], [6, 4, 5], [9, 7, 8]])
        match_east = np.array([[2, 3, 1], [5, 6, 4], [8, 9, 7]])
        match_none = np.zeros_like(tile)
        tile_data = [tile, match_north, match_south, match_west, match_east, match_none]

        # Act
        adj = Adjacencies(tile_data)
        tile_matches = adj.allowed[0, :, :]

        # Act
        assert np.all(tile_matches[0] == np.array([False, True, False, False, False, False]))
        assert np.all(tile_matches[1] == np.array([False, False, True, False, False, False]))
        assert np.all(tile_matches[2] == np.array([False, False, False, True, False, False]))
        assert np.all(tile_matches[3] == np.array([False, False, False, False, True, False]))

    def test_compatible_compares_tile_to_the_north(self, setup):
        # Arrange
        tile = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        match = np.array([[7, 8, 9], [1, 2, 3], [4, 5, 6]])
        non_match = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        # Act
        should_pass = get_valid_adjacencies(tile, match, 0)
        should_fail = get_valid_adjacencies(tile, non_match, 0)

        # Act
        assert should_pass == True
        assert should_fail == False

    def test_compatible_compares_tile_to_the_south(self, setup):
        # Arrange
        tile = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        match = np.array([[4, 5, 6], [7, 8, 9], [1, 2, 3]])
        non_match = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        # Act
        should_pass = get_valid_adjacencies(tile, match, 1)
        should_fail = get_valid_adjacencies(tile, non_match, 1)

        # Act
        assert should_pass == True
        assert should_fail == False

    def test_compatible_compares_tile_to_the_west(self, setup):
        # Arrange
        tile = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        match = np.array([[3, 1, 2], [6, 4, 5], [9, 7, 8]])
        non_match = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        # Act
        should_pass = get_valid_adjacencies(tile, match, 2)
        should_fail = get_valid_adjacencies(tile, non_match, 2)

        # Act
        assert should_pass == True
        assert should_fail == False

    def test_compatible_compares_tile_to_the_east(self, setup):
        # Arrange
        tile = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        match = np.array([[2, 3, 1], [5, 6, 4], [8, 9, 7]])
        non_match = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        # Act
        should_pass = get_valid_adjacencies(tile, match, 3)
        should_fail = get_valid_adjacencies(tile, non_match, 3)

        # Act
        assert should_pass == True
        assert should_fail == False


class TestFrequencies:
    @pytest.fixture
    def setup(self):
        self.tiles = [i for i in range(1, 17)]
        self.tile_data = []     # (np.ones((3, 3)), i) for i in range(self.num_tiles)] + [(np.zeros((3, 3)), i) for i in range(self.num_tiles)]
        for i in range(len(self.tiles)):
            for _ in range(self.tiles[i]):
                self.tile_data.append(np.full((3, 3), self.tiles[i]))

    def test_initialise_frequencies_creates_a_rule_for_every_passed_in_tile(self, setup):
        # Arrange
        expected = sum(self.tiles)

        # Act
        freq = Frequencies(self.tile_data)

        # Act
        assert len(freq.rules) == expected

    def test_frequencies_returns_relative_frequency_of_first_tile(self, setup):
        # Arrange
        tile_number = 0
        expected = 1 + int(math.sqrt(tile_number * 2))
        freq = Frequencies(self.tile_data)

        # Act
        result = freq.relative_frequency(tile_number)

        # Act
        assert result == expected

    @pytest.mark.parametrize("tile_number,expected", [(0, 1), (1, 2), (2, 2), (3, 3), (10, 5), (57, 11), (135, 16)])
    def test_frequencies_returns_relative_frequency_of_any_tile(self, setup, tile_number, expected):
        # Arrange
        freq = Frequencies(self.tile_data)

        # Act
        result = freq.relative_frequency(tile_number)

        # Act
        assert result == expected


class TestEnablers:
    @pytest.fixture
    def setup(self):
        tile = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        match_north = np.array([[7, 8, 9], [1, 2, 3], [4, 5, 6]])
        match_south = np.array([[4, 5, 6], [7, 8, 9], [1, 2, 3]])
        match_west = np.array([[3, 1, 2], [6, 4, 5], [9, 7, 8]])
        match_east = np.array([[2, 3, 1], [5, 6, 4], [8, 9, 7]])
        match_none = np.zeros_like(tile)
        self.tile_data = [tile, match_north, match_south, match_west, match_east, match_none]
        self.adjacency_rules = Adjacencies(self.tile_data)
        self.grid_height = 3
        self.grid_width = 3

    def test_initialise_enabler_counts(self, setup):
        # Arrange
        # Lowest level array such as [1, 1, 1, 0, 0, 1] means the following:
        # tiles 0, 1, 2, and 5 each have 1 adjacency to the North (if in first element of parent array)
        enabler_counts = [[1, 1, 1, 0, 0, 1], [1, 1, 1, 0, 0, 1], [1, 0, 0, 1, 1, 1], [1, 0, 0, 1, 1, 1]]  # N, S, W, E
        expected = np.full((self.grid_height, self.grid_width, 4, len(self.tile_data)), enabler_counts)

        # Act
        enabler_counts = EnablerCounts((self.grid_height, self.grid_width), len(self.tile_data), self.adjacency_rules.allowed)

        # Assert
        assert enabler_counts.height == self.grid_height
        assert enabler_counts.width == self.grid_width
        assert enabler_counts.num_tiles == len(self.tile_data)
        assert np.all(np.equal(enabler_counts.enablers, expected))

    @pytest.mark.parametrize("index, expected", [(0, 1), (1, 1), (2, 1), (3, 0), (4, 0), (5, 1)])
    def test_enabler_counts_get_enabler_count_returns_values_to_the_north(self, setup, index, expected):
        # Arrange
        enabler_counts = EnablerCounts((self.grid_height, self.grid_width), len(self.tile_data), self.adjacency_rules.allowed)

        # Act
        result = enabler_counts.get_enabler_count(1, 1, 0, index)

        # Assert
        assert result == expected

    @pytest.mark.parametrize("index, expected", [(0, 1), (1, 1), (2, 1), (3, 0), (4, 0), (5, 1)])
    def test_enabler_counts_get_enabler_count_returns_values_to_the_south(self, setup, index, expected):
        # Arrange
        enabler_counts = EnablerCounts((self.grid_height, self.grid_width), len(self.tile_data), self.adjacency_rules.allowed)

        # Act
        result = enabler_counts.get_enabler_count(1, 1, 1, index)

        # Assert
        assert result == expected

    @pytest.mark.parametrize("index, expected", [(0, 1), (1, 0), (2, 0), (3, 1), (4, 1), (5, 1)])
    def test_enabler_counts_get_enabler_count_returns_values_to_the_west(self, setup, index, expected):
        # Arrange
        enabler_counts = EnablerCounts((self.grid_height, self.grid_width), len(self.tile_data), self.adjacency_rules.allowed)

        # Act
        result = enabler_counts.get_enabler_count(1, 1, 2, index)

        # Assert
        assert result == expected

    @pytest.mark.parametrize("index, expected", [(0, 1), (1, 0), (2, 0), (3, 1), (4, 1), (5, 1)])
    def test_enabler_counts_get_enabler_count_returns_values_to_the_east(self, setup, index, expected):
        # Arrange
        enabler_counts = EnablerCounts((self.grid_height, self.grid_width), len(self.tile_data), self.adjacency_rules.allowed)

        # Act
        result = enabler_counts.get_enabler_count(1, 1, 3, index)

        # Assert
        assert result == expected

    def test_enabler_counts_decrement_decreases_enablers_to_the_north_by_1(self, setup):
        # Arrange
        expected = [1, 1, 0, 0, 0, 1]
        enabler_counts = EnablerCounts((self.grid_height, self.grid_width), len(self.tile_data), self.adjacency_rules.allowed)

        # Act
        enabler_counts.decrement(0, 0, 0, 2)

        # Assert
        assert np.all(np.equal(enabler_counts.enablers[0][0][0], expected))

    def test_enabler_counts_decrement_decreases_enablers_to_the_south_by_1(self, setup):
        # Arrange
        expected = [0, 1, 1, 0, 0, 1]
        enabler_counts = EnablerCounts((self.grid_height, self.grid_width), len(self.tile_data), self.adjacency_rules.allowed)

        # Act
        enabler_counts.decrement(0, 0, 1, 0)

        # Assert
        assert np.all(np.equal(enabler_counts.enablers[0][0][1], expected))

    def test_enabler_counts_decrement_decreases_enablers_to_the_west_by_1(self, setup):
        # Arrange
        expected = [1, 0, 0, 0, 1, 1]
        enabler_counts = EnablerCounts((self.grid_height, self.grid_width), len(self.tile_data), self.adjacency_rules.allowed)

        # Act
        enabler_counts.decrement(0, 0, 2, 3)

        # Assert
        assert np.all(np.equal(enabler_counts.enablers[0][0][2], expected))

    def test_enabler_counts_decrement_decreases_enablers_to_the_east_by_1(self, setup):
        # Arrange
        expected = [1, 0, 0, 1, 1, 0]
        enabler_counts = EnablerCounts((self.grid_height, self.grid_width), len(self.tile_data), self.adjacency_rules.allowed)

        # Act
        enabler_counts.decrement(0, 0, 3, 5)

        # Assert
        assert np.all(np.equal(enabler_counts.enablers[0][0][3], expected))

    @pytest.mark.parametrize("tile_no, expected", [(0, True), (5, True)])
    def test_enabler_counts_is_enabled_returns_true_for_enabled_tiles(self, setup, tile_no, expected):
        # Arrange
        enabler_counts = EnablerCounts((self.grid_height, self.grid_width), len(self.tile_data), self.adjacency_rules.allowed)

        # Act
        result = enabler_counts.is_enabled(1, 1, tile_no)

        # Assert
        assert result == expected

    @pytest.mark.parametrize("tile_no, expected", [(1, False), (2, False), (3, False), (4, False)])
    def test_enabler_counts_is_enabled_returns_false_if_any_direction_has_no_enablers(self, setup, tile_no, expected):
        # Arrange
        enabler_counts = EnablerCounts((self.grid_height, self.grid_width), len(self.tile_data), self.adjacency_rules.allowed)

        # Act
        result = enabler_counts.is_enabled(1, 1, tile_no)

        # Assert
        assert result == expected

    @pytest.mark.parametrize("direction, expected", [(0, 1), (1, 1), (2, 1), (3, 1)])
    def test_enabler_counts_disable_tile_reduces_north_enablers_to_zero(
        self, setup, direction, expected
    ):
        # Arrange
        enabler_counts = EnablerCounts((self.grid_height, self.grid_width), len(self.tile_data), self.adjacency_rules.allowed)
        pre_disabled_value = enabler_counts.get_enabler_count(1, 1, direction, 5)

        # Act
        enabler_counts.disable_tile(1, 1, 5)
        post_disabled_value = enabler_counts.get_enabler_count(1, 1, direction, 5)

        # Assert
        assert pre_disabled_value == expected
        assert post_disabled_value == 0
