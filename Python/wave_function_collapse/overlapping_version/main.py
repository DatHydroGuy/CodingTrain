from random import choice
import pygame

from grid import Grid
from tile_set import TileSet


def main():
    window_size = (1000, 800)
    default_tile_scaling = 2
    tile_set = TileSet(r'..\samples\city.png', tile_size=3, colour_tolerance=10, match_ratio=0.9, max_mismatch_run=1)
    horizonal_cells = window_size[0] // (default_tile_scaling * tile_set.tile_size[1])
    vertical_cells = window_size[1] // (default_tile_scaling * tile_set.tile_size[0])
    grid = Grid(window_size, tile_set, horizonal_cells, vertical_cells, scaling=default_tile_scaling, wrap=True)

    pygame.init()

    screen_size = (window_size[0] // default_tile_scaling, window_size[1] // default_tile_scaling)
    screen = pygame.Surface(screen_size)
    width_offset = (window_size[0] - horizonal_cells * default_tile_scaling * tile_set.tile_size[1]) // 2
    height_offset = (window_size[1] - vertical_cells * default_tile_scaling * tile_set.tile_size[0]) // 2
    window_surface = pygame.display.set_mode(window_size)
    screen.fill((0, 0, 0))
    pygame.display.set_caption("Wave Function Collapse in Python")

    y, x = grid.get_lowest_entropy_cell()
    first_tile = choice(tile_set.tiles)
    grid.collapse(x, y, first_tile.id, [n for n in grid.entropy[y, x] if n != first_tile.id])

    clock = pygame.time.Clock()
    running = True
    collapsing = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    running = False

        grid.draw(screen)
        scaled_screen = pygame.transform.scale(screen, window_size)

        if collapsing:
            y, x = grid.get_lowest_entropy_cell()
            if x is not None and y is not None:
                current_entropies = [i for i, e in enumerate(grid.entropy[y, x]) if e]
                next_tile_id = choice(current_entropies)
                grid.collapse(x, y, next_tile_id, [n for n in current_entropies if n != next_tile_id])
            else:
                print("Finished")
                collapsing = False

        window_surface.blit(scaled_screen, (width_offset, height_offset))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
