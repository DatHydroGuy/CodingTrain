import pygame
from grid import Grid
from tile_set import TileSet


def main():
    screen_size = (1600, 1200)
    tile_set = TileSet(r'..\samples\city.png', kernel_size=3, include_rotated_kernels=False, include_flipped_kernels=False)
    grid_resolution = (40, 30)
    grid = Grid(screen_size, grid_resolution, tile_set, wrap=False)

    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    screen.fill((0, 0, 0))
    pygame.display.set_caption("Wave Function Collapse in Python")

    grid.step()

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    running = False

        if not grid.finished:
            grid.step()
        grid.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
