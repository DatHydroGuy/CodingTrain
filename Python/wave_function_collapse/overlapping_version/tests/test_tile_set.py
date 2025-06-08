import numpy as np
import pytest

from tile_set import TileSet


class TestTileSet:
    @pytest.fixture
    def setup(self):
        # tile will not make adjacencies with itself or tile3 but will with tile2 in all 4 directions
        self.bad_file_path = r"this is not a path"
        self.good_file_path = r"..\samples\City.png"
        self.tile = np.array([[[0, 0, 255], [0, 0, 0], [0, 0, 255]],
                              [[0, 0, 0], [0, 0, 255], [0, 0, 0]],
                              [[0, 0, 255], [0, 0, 0], [0, 0, 255]]])

    def test_initialise_tile_set_reads_pixels_of_valid_passed_in_file(self, mocker, setup):
        # Arrange
        mock_read = mocker.patch("tile_set.TileSet.read_source_file")
        mocker.patch("tile_set.TileSet.create_tiles")
        mocker.patch("tile_set.Adjacencies")
        mocker.patch("tile_set.Frequencies")

        # Act
        TileSet(source_file=self.good_file_path)

        # Assert
        assert mock_read.call_count == 1

    def test_initialise_tile_set_throws_error_with_invalid_passed_in_file(self, setup):
        # Arrange

        # Act & Assert
        with pytest.raises(TypeError):
            TileSet(source_file=self.bad_file_path)

    def test_initialise_tile_set_correctly_reads_pixels_of_valid_passed_in_file(self, setup):
        # Arrange
        expected = np.array([[[255, 255, 255], [255, 255, 255], [255, 255, 255]],
                             [[255, 255, 255], [0, 0, 0], [0, 0, 0]],
                             [[255, 255, 255], [0, 0, 0], [237, 28, 36]]])

        # Act
        ts = TileSet(source_file=self.good_file_path)

        # Assert
        assert np.all(np.equal(ts.pixels[:3, :3, :], expected))

    def test_initialise_tile_set_creates_tiles_from_passed_in_pixels(self, mocker, setup):
        # Arrange
        mock_create = mocker.patch("tile_set.TileSet.create_tiles")
        mocker.patch("tile_set.Adjacencies")
        mocker.patch("tile_set.Frequencies")

        # Act
        TileSet(source_file=self.good_file_path)

        # Assert
        assert mock_create.call_count == 1

    def test_initialise_tile_set_correctly_creates_first_tile(self, setup):
        # Arrange
        expected = np.array([[[255, 255, 255], [255, 255, 255], [255, 255, 255]],
                             [[255, 255, 255], [0, 0, 0], [0, 0, 0]],
                             [[255, 255, 255], [0, 0, 0], [237, 28, 36]]])

        # Act
        ts = TileSet(source_file=self.good_file_path)

        # Assert
        assert np.all(np.equal(ts.tiles[0], expected))

    def test_initialise_tile_set_correctly_creates_seventh_tile(self, setup):
        # Arrange
        expected = np.array([[[255, 255, 255], [255, 255, 255], [255, 255, 255]],
                             [[0, 0, 0], [0, 0, 0], [255, 255, 255]],
                             [[237, 28, 36], [0, 0, 0], [255, 255, 255]]])

        # Act
        ts = TileSet(source_file=self.good_file_path)

        # Assert
        assert np.all(np.equal(ts.tiles[6], expected))

    def test_initialise_tile_set_correctly_creates_eighth_tile(self, setup):
        # Arrange
        expected = np.array([[[255, 255, 255], [255, 255, 255], [255, 255, 255]],
                             [[0, 0, 0], [255, 255, 255], [255, 255, 255]],
                             [[0, 0, 0], [255, 255, 255], [255, 255, 255]]])

        # Act
        ts = TileSet(source_file=self.good_file_path)

        # Assert
        assert np.all(np.equal(ts.tiles[7], expected))

    def test_initialise_tile_set_correctly_creates_ninth_tile(self, setup):
        # Arrange
        expected = np.array([[[255, 255, 255], [255, 255, 255], [255, 255, 255]],
                             [[255, 255, 255], [255, 255, 255], [0, 0, 0]],
                             [[255, 255, 255], [255, 255, 255], [0, 0, 0]]])

        # Act
        ts = TileSet(source_file=self.good_file_path)

        # Assert
        assert np.all(np.equal(ts.tiles[8], expected))

    def test_initialise_tile_set_correctly_creates_55th_tile(self, setup):
        # Arrange
        expected = np.array([[[255, 255, 255], [0, 0, 0], [237, 28, 36]],
                             [[255, 255, 255], [0, 0, 0], [0, 0, 0]],
                             [[255, 255, 255], [255, 255, 255], [255, 255, 255]]])

        # Act
        ts = TileSet(source_file=self.good_file_path)

        # Assert
        assert np.all(np.equal(ts.tiles[54], expected))

    def test_initialise_tile_set_correctly_creates_61st_tile(self, setup):
        # Arrange
        expected = np.array([[[237, 28, 36], [0, 0, 0], [255, 255, 255]],
                             [[0, 0, 0], [0, 0, 0], [255, 255, 255]],
                             [[255, 255, 255], [255, 255, 255], [255, 255, 255]]])

        # Act
        ts = TileSet(source_file=self.good_file_path)

        # Assert
        assert np.all(np.equal(ts.tiles[60], expected))

    def test_initialise_tile_set_correctly_creates_64th_tile(self, setup):
        # Arrange
        expected = np.array([[[255, 255, 255], [0, 0, 0], [0, 0, 0]],
                             [[255, 255, 255], [255, 255, 255], [255, 255, 255]],
                             [[255, 255, 255], [255, 255, 255], [255, 255, 255]]])

        # Act
        ts = TileSet(source_file=self.good_file_path)

        # Assert
        assert np.all(np.equal(ts.tiles[63], expected))

    def test_initialise_tile_set_correctly_creates_71st_tile(self, setup):
        # Arrange
        expected = np.array([[[0, 0, 0], [255, 255, 255], [255, 255, 255]],
                             [[255, 255, 255], [255, 255, 255], [255, 255, 255]],
                             [[255, 255, 255], [255, 255, 255], [255, 255, 255]]])

        # Act
        ts = TileSet(source_file=self.good_file_path)

        # Assert
        assert np.all(np.equal(ts.tiles[70], expected))

    def test_initialise_tile_set_correctly_creates_73rd_tile(self, setup):
        # Arrange
        expected = np.array([[[255, 255, 255], [255, 255, 255], [255, 255, 255]],
                             [[255, 255, 255], [255, 255, 255], [255, 255, 255]],
                             [[255, 255, 255], [0, 0, 0], [0, 0, 0]]])

        # Act
        ts = TileSet(source_file=self.good_file_path)

        # Assert
        assert np.all(np.equal(ts.tiles[72], expected))

    def test_initialise_tile_set_correctly_creates_81st_tile(self, setup):
        # Arrange
        expected = np.array([[[255, 255, 255], [255, 255, 255], [255, 255, 255]],
                             [[255, 255, 255], [255, 255, 255], [255, 255, 255]],
                             [[255, 255, 255], [255, 255, 255], [0, 0, 0]]])

        # Act
        ts = TileSet(source_file=self.good_file_path)

        # Assert
        assert np.all(np.equal(ts.tiles[80], expected))

    def test_initialise_tile_set_correctly_creates_first_tile_with_rotation(self, setup):
        # Arrange
        expected = np.array([[[255, 255, 255], [0, 0, 0], [237, 28, 36]],
                             [[255, 255, 255], [0, 0, 0], [0, 0, 0]],
                             [[255, 255, 255], [255, 255, 255], [255, 255, 255]]])

        # Act
        ts = TileSet(source_file=self.good_file_path, include_rotated_kernels=True)

        # Assert
        assert np.all(np.equal(ts.tiles[1], expected))

    def test_initialise_tile_set_correctly_creates_second_tile_with_rotation(self, setup):
        # Arrange
        expected = np.array([[[237, 28, 36], [0, 0, 0], [255, 255, 255]],
                             [[0, 0, 0], [0, 0, 0], [255, 255, 255]],
                             [[255, 255, 255], [255, 255, 255], [255, 255, 255]]])

        # Act
        ts = TileSet(source_file=self.good_file_path, include_rotated_kernels=True)

        # Assert
        assert np.all(np.equal(ts.tiles[2], expected))

    def test_initialise_tile_set_correctly_creates_third_tile_with_rotation(self, setup):
        # Arrange
        expected = np.array([[[255, 255, 255], [255, 255, 255], [255, 255, 255]],
                             [[0, 0, 0], [0, 0, 0], [255, 255, 255]],
                             [[237, 28, 36], [0, 0, 0], [255, 255, 255]]])

        # Act
        ts = TileSet(source_file=self.good_file_path, include_rotated_kernels=True)

        # Assert
        assert np.all(np.equal(ts.tiles[3], expected))

    def test_initialise_tile_set_correctly_creates_first_tile_with_flipping(self, setup):
        # Arrange
        expected = np.array([[[255, 255, 255], [0, 0, 0], [237, 28, 36]],
                             [[255, 255, 255], [0, 0, 0], [0, 0, 0]],
                             [[255, 255, 255], [255, 255, 255], [255, 255, 255]]])

        # Act
        ts = TileSet(source_file=self.good_file_path, include_flipped_kernels=True)

        # Assert
        assert np.all(np.equal(ts.tiles[1], expected))

    def test_initialise_tile_set_creates_tiles_with_deterministic_sequence_with_rotations_and_flipping(self, setup):
        # Arrange
        expected = np.array([[[255, 255, 255], [255, 255, 255], [255, 255, 255]],
                             [[255, 255, 255], [0, 0, 0], [0, 0, 0]],
                             [[255, 255, 255], [0, 0, 0], [237, 28, 36]]])
        expected2 = np.rot90(expected, 1)
        expected3 = np.rot90(expected, 2)
        expected4 = np.rot90(expected, 3)
        expected5 = np.flip(expected, axis=0)
        expected6 = np.rot90(expected5, 1)
        expected7 = np.rot90(expected5, 2)
        expected8 = np.rot90(expected5, 3)

        # Act
        ts = TileSet(source_file=self.good_file_path, include_rotated_kernels=True, include_flipped_kernels=True)

        # Assert
        assert np.all(np.equal(ts.tiles[0], expected))
        assert np.all(np.equal(ts.tiles[1], expected2))
        assert np.all(np.equal(ts.tiles[2], expected3))
        assert np.all(np.equal(ts.tiles[3], expected4))
        assert np.all(np.equal(ts.tiles[4], expected5))
        assert np.all(np.equal(ts.tiles[5], expected6))
        assert np.all(np.equal(ts.tiles[6], expected7))
        assert np.all(np.equal(ts.tiles[7], expected8))

    def test_initialise_tile_set_creates_a_tile_for_every_pixel_without_rotation_or_flipping(self, setup):
        # Arrange

        # Act
        ts = TileSet(source_file=self.good_file_path)
        expected = ts.pixels.shape[0] * ts.pixels.shape[1]

        # Assert
        assert len(ts.tiles) == expected

    def test_initialise_tile_set_creates_4_tiles_for_every_pixel_with_rotation_without_flipping(self, setup):
        # Arrange

        # Act
        ts = TileSet(source_file=self.good_file_path, include_rotated_kernels=True)
        expected = ts.pixels.shape[0] * ts.pixels.shape[1] * 4

        # Assert
        assert len(ts.tiles) == expected

    def test_initialise_tile_set_creates_2_tiles_for_every_pixel_without_rotation_with_flipping(self, setup):
        # Arrange

        # Act
        ts = TileSet(source_file=self.good_file_path, include_flipped_kernels=True)
        expected = ts.pixels.shape[0] * ts.pixels.shape[1] * 2

        # Assert
        assert len(ts.tiles) == expected

    def test_initialise_tile_set_creates_8_tiles_for_every_pixel_with_rotation_and_flipping(self, setup):
        # Arrange

        # Act
        ts = TileSet(source_file=self.good_file_path, include_rotated_kernels=True, include_flipped_kernels=True)
        expected = ts.pixels.shape[0] * ts.pixels.shape[1] * 8

        # Assert
        assert len(ts.tiles) == expected

    def test_initialise_tile_set_creates_adjacency_rules(self, setup):
        # Arrange

        # Act
        ts = TileSet(source_file=self.good_file_path)
        expected = (ts.pixels.shape[0] * ts.pixels.shape[1], 4, ts.pixels.shape[0] * ts.pixels.shape[1])

        # Assert
        assert ts.adjacencies.shape == expected

    def test_initialise_tile_set_creates_frequency_rules(self, setup):
        # Arrange

        # Act
        ts = TileSet(source_file=self.good_file_path)
        expected = ts.pixels.shape[0] * ts.pixels.shape[1]

        # Assert
        assert len(ts.frequencies) == expected
