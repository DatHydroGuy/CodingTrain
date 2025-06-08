import heapq
from collections import deque

import numpy as np
import pytest
from grid import Grid
from tile_set import TileSet


class TestGrid:
    @pytest.fixture
    def setup(self):
        self.screen_size = (800, 600)
        self.tile_set = TileSet(r"..\samples\City.png")
        self.size_in_cells = (20, 14)
        self.scaling = 1
        self.wrap = False
        self.entropy_heap = []
        self.tile_removals = deque()

    def test_initialise_grid(self, setup):
        # Arrange

        # Act
        grid = Grid(self.screen_size, self.size_in_cells, self.tile_set, self.scaling, self.wrap)

        # Act
        assert grid.screen_size == self.screen_size
        assert grid.size_in_cells == self.size_in_cells
        assert grid.tile_set == self.tile_set
        assert grid.cell_size == min(self.screen_size[0] // self.size_in_cells[0], self.screen_size[1] // self.size_in_cells[1])
        assert grid.num_cells == len(self.tile_set.tiles)
        assert grid.num_uncollapsed_cells == len(self.tile_set.tiles)
        assert grid.scaling == self.scaling
        assert grid.wrap == self.wrap
        assert grid.entropy_heap == self.entropy_heap
        assert grid.tile_removals == self.tile_removals

    def test_grid_step_sequence_of_events(self, setup, mocker):
        # Arrange
        mock_choose_cell = mocker.patch("grid.Grid.choose_next_cell")
        mock_choose_cell.return_value = (0, 0)
        mock_collapse_cell = mocker.patch("grid.Grid.collapse_cell_at")
        mock_propagate = mocker.patch("grid.Grid.propagate")
        grid = Grid(self.screen_size, self.size_in_cells, self.tile_set, self.scaling, self.wrap)

        # Act
        grid.step()

        # Act
        assert mock_choose_cell.call_count == 1
        assert mock_collapse_cell.call_count == 1
        assert mock_collapse_cell.call_args_list[0][0][0] == (0, 0)
        assert mock_propagate.call_count == 1

    def test_grid_choose_next_cell_returns_cell(self, setup):
        # Arrange
        grid = Grid(self.screen_size, self.size_in_cells, self.tile_set, self.scaling, self.wrap)
        expected = (1.23, 7, 3)
        heapq.heappush(grid.entropy_heap, expected)

        # Act
        result = grid.choose_next_cell()

        # Act
        assert result == expected

    def test_grid_choose_next_cell_returns_first_uncollapsed_cell(self, setup):
        # Arrange
        grid = Grid(self.screen_size, self.size_in_cells, self.tile_set, self.scaling, self.wrap)
        grid.cells[4][1].is_collapsed = True
        expected = (1.23, 2, 5)
        heapq.heappush(grid.entropy_heap, expected)
        heapq.heappush(grid.entropy_heap, (1.23, 1, 4))

        # Act
        result = grid.choose_next_cell()

        # Act
        assert result == expected

    def test_grid_choose_next_cell_returns_the_cell_with_the_lowest_entropy(self, setup):
        # Arrange
        grid = Grid(self.screen_size, self.size_in_cells, self.tile_set, self.scaling, self.wrap)
        expected = (1.21, 11, 9)
        heapq.heappush(grid.entropy_heap, (1.22, 19, 16))
        heapq.heappush(grid.entropy_heap, expected)
        heapq.heappush(grid.entropy_heap, (1.23, 1, 4))

        # Act
        result = grid.choose_next_cell()

        # Act
        assert result == expected

    def test_grid_choose_next_cell_returns_the_uncollapsed_cell_with_the_lowest_entropy(self, setup):
        # Arrange
        grid = Grid(self.screen_size, self.size_in_cells, self.tile_set, self.scaling, self.wrap)
        grid.cells[4][1].is_collapsed = True
        expected = (1.21, 11, 9)
        heapq.heappush(grid.entropy_heap, (1.22, 19, 16))
        heapq.heappush(grid.entropy_heap, expected)
        heapq.heappush(grid.entropy_heap, (1.2, 1, 4))

        # Act
        result = grid.choose_next_cell()

        # Act
        assert result == expected

    def test_grid_choose_next_cell_throws_error_if_heap_becomes_empty(self, setup):
        # Arrange
        grid = Grid(self.screen_size, self.size_in_cells, self.tile_set, self.scaling, self.wrap)

        # Act & Assert
        with pytest.raises(IndexError):
            grid.choose_next_cell()

    def test_grid_collapse_cell_at_sets_collapsed_flag_of_target_cell(self, setup):
        # Arrange
        grid = Grid(self.screen_size, self.size_in_cells, self.tile_set, self.scaling, self.wrap)
        target_cell_coord = (1, 4)
        pre_collapsed = grid.cells[target_cell_coord[1]][target_cell_coord[0]].is_collapsed

        # Act
        grid.collapse_cell_at(target_cell_coord)

        # Assert
        assert pre_collapsed is False
        assert grid.cells[target_cell_coord[1]][target_cell_coord[0]].is_collapsed is True

    def test_grid_collapse_cell_at_sets_possible_flag_to_true_and_all_others_to_false(self, setup):
        # Arrange
        grid = Grid(self.screen_size, self.size_in_cells, self.tile_set, self.scaling, self.wrap)
        target_cell_coord = (1, 4)

        # Act
        grid.collapse_cell_at(target_cell_coord)
        possibles = grid.cells[target_cell_coord[1]][target_cell_coord[0]].possible

        # Assert
        assert len(possibles[possibles == True]) == 1
        assert len(possibles[possibles == False]) == len(possibles) - 1

    def test_grid_collapse_cell_at_adds_current_tile_number_and_cell_coordinate_to_removal_history(self, setup):
        # Arrange
        grid = Grid(self.screen_size, self.size_in_cells, self.tile_set, self.scaling, self.wrap)
        target_cell_coord = (1, 4)

        # Act
        grid.collapse_cell_at(target_cell_coord)
        expected_tile = np.flatnonzero(grid.cells[target_cell_coord[1]][target_cell_coord[0]].possible)
        removals = grid.tile_removals.popleft()

        # Assert
        assert removals[0] == expected_tile
        assert removals[1] == target_cell_coord







    def test_grid_step(self, setup):
        # Arrange
        self.size_in_cells = (2, 3)
        self.tile_set = TileSet(r"..\tests\CityTest.png")
        grid = Grid(self.screen_size, self.size_in_cells, self.tile_set, self.scaling, self.wrap)

        # Act
        grid.step()

        # Assert
        assert True
