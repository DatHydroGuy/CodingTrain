import numpy as np
import pygame
import pytest
from cell import Cell
from helpers import Adjacencies, Frequencies


class TestCell:
    @pytest.fixture
    def setup(self, mocker):
        # tile will not make adjacencies with itself or tile3 but will with tile2 in all 4 directions
        self.tile1 = np.array([[[0, 0, 255], [0, 0, 0], [0, 0, 255]],
                              [[0, 0, 0], [0, 0, 255], [0, 0, 0]],
                              [[0, 0, 255], [0, 0, 0], [0, 0, 255]]])
        # tile will not make adjacencies with itself but will with tile1 in all 4 directions
        # will make adjacencies with tile3 to the South and West
        self.tile2 = np.array([[[0, 0, 0], [0, 0, 255], [0, 0, 0]],
                              [[0, 0, 255], [0, 0, 0], [0, 0, 255]],
                               [[0, 0, 0], [0, 0, 255], [0, 0, 0]]])
        # tile will not make adjacencies with itself or tile1 but will with tile2 to the North and East
        self.tile3 = np.array([[[0, 0, 255], [0, 0, 0], [0, 0, 255]],
                              [[0, 0, 0], [0, 0, 255], [0, 0, 0]],
                              [[255, 255, 255], [0, 0, 0], [0, 0, 255]]])
        self.tile4 = np.rot90(self.tile2, 1)    # Identical to tile2
        self.adjacencies = Adjacencies(
            [self.tile1, self.tile2, self.tile3, self.tile4]
        ).allowed
        self.frequencies = Frequencies(
            [self.tile1, self.tile2, self.tile3, self.tile4]
        ).rules
        self.x = 100
        self.y = 200
        self.grid_size = (80, 50)
        self.cell_size = 60
        # self.weight_sum = 17
        # self.weight_sum_log = float(self.weight_sum) * np.log2(float(self.weight_sum))

        self.mock_draw = mocker.patch("pygame.draw.rect")


    # @pytest.fixture
    # def mock_draw(self, monkeypatch):
    #     def mock_draw_rect(surface, colour, rectangle):
    #         return
    #
    #     monkeypatch.setattr(pygame.draw, "rect", staticmethod(mock_draw_rect))

    def test_initialise_cell_sets_everything_except_tile(self, setup):
        # Arrange

        # Act
        cell = Cell(self.x, self.y, self.grid_size, self.cell_size, self.adjacencies, self.frequencies)#, self.weight_sum, self.weight_sum_log)

        # Assert
        assert cell.x_pos == self.x
        assert cell.y_pos == self.y
        assert cell.width == self.cell_size
        assert cell.height == self.cell_size
        assert np.all(np.equal(cell.adjacency_rules, self.adjacencies))
        assert np.all(np.equal(cell.frequency_rules, self.frequencies))
        # assert cell.weight_sum == self.weight_sum
        # assert cell.weight_sum_log == self.weight_sum_log
        assert cell.tile is None
        assert cell.entropy_noise == pytest.approx(0.00001, abs=0.00001)
        assert cell.is_collapsed is False

    def test_cell_set_tile(self, setup):
        # Arrange
        cell = Cell(self.x, self.y, self.grid_size, self.cell_size, self.adjacencies, self.frequencies)#, self.weight_sum, self.weight_sum_log)

        # Act
        cell.set_tile(self.tile1)

        # Assert
        assert np.all(np.equal(cell.tile, self.tile1))

    def test_cell_get_tile(self, setup):
        # Arrange
        cell = Cell(self.x, self.y, self.grid_size, self.cell_size, self.adjacencies, self.frequencies)#, self.weight_sum, self.weight_sum_log)
        cell.set_tile(self.tile1)

        # Act
        result = cell.get_tile()

        # Assert
        assert np.all(np.equal(result, self.tile1))

    @pytest.mark.parametrize("tile_number", [0, 1, 2, 3])
    def test_cell_remove_tile(self, setup, tile_number):
        # Arrange
        cell = Cell(self.x, self.y, self.grid_size, self.cell_size, self.adjacencies, self.frequencies)#, self.weight_sum, self.weight_sum_log)
        expected_weight_sum = cell.weight_sum - self.frequencies[tile_number]
        expected_weight_sum_log = cell.weight_sum_log - self.frequencies[tile_number] * np.log2(self.frequencies[tile_number])

        # Act
        cell.remove_tile(tile_number)

        # Assert
        assert cell.weight_sum == expected_weight_sum
        assert cell.weight_sum_log == expected_weight_sum_log

    def test_cell_total_possible_tile_frequency_is_initially_the_sum_of_all_frequencies(self, setup):
        # Arrange
        cell = Cell(self.x, self.y, self.grid_size, self.cell_size, self.adjacencies, self.frequencies)#, self.weight_sum, self.weight_sum_log)

        # Act
        result = cell.total_possible_tile_frequency()

        # Assert
        assert result == sum(self.frequencies)

    def test_cell_total_possible_tile_frequency_calculates_the_sum_of_only_possible_frequencies(self, setup):
        # Arrange
        cell = Cell(self.x, self.y, self.grid_size, self.cell_size, self.adjacencies, self.frequencies)#, self.weight_sum, self.weight_sum_log)
        cell.possible[1] = False
        expected = sum(self.frequencies) - cell.frequency_rules[1]

        # Act
        result = cell.total_possible_tile_frequency()

        # Assert
        assert result == expected

    def test_cell_choose_tile_index(self, setup):
        # Arrange
        cell = Cell(self.x, self.y, self.grid_size, self.cell_size, self.adjacencies, self.frequencies)#, self.weight_sum, self.weight_sum_log)
        forbidden_index = 1
        cell.possible[forbidden_index] = False

        # Act
        results = np.array([0, 0, 0, 0])
        for _ in range(100000):
            result = cell.choose_tile_index()
            results[result] += 1

        # Assert
        assert results[forbidden_index] == 0
        assert np.all(np.not_equal(np.delete(results, forbidden_index), 0))

    # @pytest.mark.parametrize("tile_number,expected", [(0, 1), (1, 2), (2, 1), (3, 2)])
    # def test_cell_relative_frequency_for_a_given_tile(self, setup, tile_number, expected):
    #     # Arrange
    #     cell = Cell(self.x, self.y, self.width, self.height, self.adjacencies, self.frequencies)#, self.weight_sum, self.weight_sum_log)
    #
    #     # Act
    #     result = cell.relative_frequency(tile_number)
    #
    #     # Act
    #     assert result == expected

    @pytest.mark.parametrize("frequencies, expected", [([1, 2, 1, 2], 1.9182958340544896), ([17], 0.0), ([2, 3, 5, 7, 11], 2.090577770771398), ([1, 1, 1, 121, 1], 0.26832467098028)])
    def test_cell_entropy(self, setup, frequencies, expected):
        # Arrange
        cell = Cell(self.x, self.y, self.grid_size, self.cell_size, self.adjacencies, np.array(frequencies))#, self.weight_sum, self.weight_sum_log)

        # Act
        result = cell.entropy()

        # Act
        assert result == pytest.approx(expected, abs=0.000001)

    def test_cell_draw_draws_a_rectangle_if_no_tile(self, setup):
        # Arrange
        cell = Cell(self.x, self.y, self.grid_size, self.cell_size, self.adjacencies, self.frequencies)#, self.weight_sum, self.weight_sum_log)

        # Act
        cell.draw(pygame.Surface((self.cell_size, self.cell_size)))

        # Assert
        assert self.mock_draw.call_count == 1

    def test_cell_draw_draws_a_rectangle_if_tile_present(self, setup):
        # Arrange
        cell = Cell(self.x, self.y, self.grid_size, self.cell_size, self.adjacencies, self.frequencies)#, self.weight_sum, self.weight_sum_log)
        cell.set_tile(self.tile1)

        # Act
        cell.draw(pygame.Surface((self.cell_size, self.cell_size)))

        # Assert
        assert self.mock_draw.call_count == 1

    def test_cell_draw_draws_black_rectangle_on_passed_in_surface_if_no_tile(self, setup):
        # Arrange
        cell = Cell(self.x, self.y, self.grid_size, self.cell_size, self.adjacencies, self.frequencies)#, self.weight_sum, self.weight_sum_log)
        test_surface = pygame.Surface((self.cell_size, self.cell_size))
        black = (0, 0, 0)

        # Act
        cell.draw(test_surface)

        # Assert
        assert self.mock_draw.call_args_list[0][0][0] == test_surface
        assert self.mock_draw.call_args_list[0][0][1] == black

    def test_cell_draw_draws_coloured_rectangle_on_passed_in_surface_if_tile_present(self, setup):
        # Arrange
        cell = Cell(self.x, self.y, self.grid_size, self.cell_size, self.adjacencies, self.frequencies)#, self.weight_sum, self.weight_sum_log)
        test_surface = pygame.Surface((self.cell_size, self.cell_size))
        cell.set_tile(self.tile1)
        colour = self.tile1[0][0]

        # Act
        cell.draw(test_surface)

        # Assert
        assert self.mock_draw.call_args_list[0][0][0] == test_surface
        assert np.all(np.equal(self.mock_draw.call_args_list[0][0][1], colour))
