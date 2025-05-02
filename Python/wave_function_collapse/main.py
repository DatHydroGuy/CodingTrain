from random import choice
import pygame
from grid import Grid
from tile_set import TileSet


def main():
    screen_size = (1400, 1050)
    default_tile_scaling = 2
    tile_set = TileSet(r'tilesets\Circuit', colour_tolerance=10, match_ratio=0.7, max_mismatch_run=1)
    horizonal_cells = screen_size[0] // (default_tile_scaling * tile_set.tile_size[1])
    vertical_cells = screen_size[1] // (default_tile_scaling * tile_set.tile_size[0])
    grid = Grid(screen_size, tile_set, horizonal_cells, vertical_cells, scaling=default_tile_scaling)

    pygame.init()

    screen = pygame.display.set_mode(screen_size)
    screen.fill((0, 0, 0))
    pygame.display.set_caption("Wave Function Collapse in Python")

    y, x = grid.get_lowest_entropy_cell()
    first_tile = choice(tile_set.tiles)
    grid.collapse(x, y, first_tile.id, [n for n in grid.grid[y][x]["entropy"] if n != first_tile.id])

    clock = pygame.time.Clock()
    running = True
    debugging = False
    collapsing = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_d:
                    debugging = not debugging

        grid.draw(screen, debugging)

        if collapsing:
            y, x = grid.get_lowest_entropy_cell()
            if x is not None and y is not None:
                next_tile_id = choice(grid.grid[y][x]["entropy"])
                grid.collapse(x, y, next_tile_id, [n for n in grid.grid[y][x]["entropy"] if n != next_tile_id])
            else:
                print("Finished")
                collapsing = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
