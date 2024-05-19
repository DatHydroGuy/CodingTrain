from pygame.locals import (K_ESCAPE, KEYDOWN, QUIT)

from particle import Particle
from quadtree import *

# define constants for screen width and height
SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 1000

pygame.init()

boundary = Rectangle(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
particles = []

for i in range(1200):
    p = Particle(SCREEN_WIDTH, SCREEN_HEIGHT)
    particles.append(p)

# create the drawing surface (screen)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()

# main loop
running = True
meh = 0
while running:

    # process user inputs
    for event in pygame.event.get():
        # did the user press a key?
        if event.type == KEYDOWN:
            # was it the escape key? If so, then exit program
            if event.key == K_ESCAPE:
                running = False
        # did the user click the close window button? If so, then exit program
        elif event.type == QUIT:
            running = False

    pressed_keys = pygame.key.get_pressed()

    quad_tree = QuadTree(boundary, 1)

    # fill the background with black
    screen.fill((0, 0, 0))

    # update
    for particle in particles:
        point = Point(particle.x, particle.y, particle)
        quad_tree.insert(point)
        particle.move()
        particle.render(screen)
        particle.set_highlight(False)

    for p in particles:
        circular_area_to_test = Circle(p.x, p.y, p.r * 2)
        points = quad_tree.query(circular_area_to_test, [])
        for pt in points:
            other = pt.user_data
            if p != other and p.intersects(other):
                p.set_highlight(True)

    # quad_tree.show(screen)
    #
    # rnd_rect_pts = quad_tree.query(rnd_rect, [])
    # for pt in rnd_rect_pts:
    #     pygame.draw.circle(screen, pygame.color.Color('red'), (pt.x, pt.y), 2)

    # update the display
    pygame.display.flip()

    clock.tick(100)
    # meh += 1
    # if meh % 60 == 0:
    #     print(clock.get_fps())

# exit pygame
pygame.quit()
