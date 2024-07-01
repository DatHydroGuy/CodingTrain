import ctypes
import pygame
import pymunk
import pymunk.pygame_util
from random import uniform


# https://www.youtube.com/watch?v=KakpnfDv_f0&list=PLRqwX-V7Uu6ZiZxtDDRCi6uhfTH4FilpH&index=79
# https://github.com/viblo/pymunk/blob/master/pymunk/examples/bouncing_balls.py
class Plinko:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = 800  # user32.GetSystemMetrics(0)
        self.screen_height = 1100  # user32.GetSystemMetrics(1)

        pygame.init()
        # pygame.display.set_caption("PyGame Framework")

        self.__clock = pygame.time.Clock()
        self.fps = 60.0

        window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF, 32)

        self.cols = 11
        self.rows = 10
        self.spacing = self.screen_width / self.cols

        # Space
        self._space = pymunk.Space()
        self._space.gravity = (0.0, 900.0)

        # Physics
        # Time step
        self._dt = 1.0 / self.fps

        # Number of physics steps per screen frame
        self._physics_steps_per_frame = 1

        self._draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        # Balls that exist in the world
        self.balls = []

        # Static barrier walls (lines) that the balls bounce off of
        self._add_static_scenery()

        # Execution control and time until the next ball spawns
        self._running = True
        self._ticks_to_next_ball = 10

    def start(self) -> None:
        start = pygame.time.get_ticks()
        old_time = start - 2000

        while 1:
            # Progress time forward
            for x in range(self._physics_steps_per_frame):
                self._space.step(self._dt)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            self.screen.fill((0, 0, 0))
            if start - old_time >= 2000:
                self._add_balls()
                old_time = start
            start = pygame.time.get_ticks()
            self._update_balls()

            # render
            self._space.debug_draw(self._draw_options)
            pygame.display.flip()

            self.__clock.tick(self.fps)

    def _add_static_scenery(self):
        static_body = self._space.static_body

        static_lines = [
            pymunk.Segment(static_body, (0.0, self.screen_height), (self.screen_width, self.screen_height), 5.0)
        ]
        for i in range(self.cols + 2):
            static_lines.append(pymunk.Segment(static_body,
                                               (i * self.spacing, self.screen_height),
                                               (i * self.spacing, self.screen_height * 0.85),
                                               5.0
                                               ))
        for line in static_lines:
            line.elasticity = 0.0
            line.friction = 0.9
        self._space.add(*static_lines)

        pegs = []
        peg_radius = min(self.screen_width, self.screen_height) * 0.025
        for j in range(self.rows):
            y_off = self.spacing + j * self.spacing
            for i in range(self.cols + 1):
                x_off = i * self.spacing if j % 2 == 1 else (i + 0.5) * self.spacing
                pegs.append(pymunk.Circle(static_body, peg_radius, (x_off, y_off)))
        for peg in pegs:
            peg.elasticity = 0.2
            peg.friction = 0.5
        self._space.add(*pegs)

    def _add_balls(self):
        mass = 10
        radius = min(self.screen_width, self.screen_height) * 0.01875  # peg_radius * 0.75
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
        body = pymunk.Body(mass, inertia)
        body.position = self.screen_width // 2 + uniform(-1, 1), 0
        shape = pymunk.Circle(body, radius, (0, 0))
        shape.color = pygame.Color.from_hsla(uniform(0, 360), 100, 50, 50)
        shape.elasticity = 0.1
        shape.friction = 0.3
        self._space.add(body, shape)
        self.balls.append(shape)

    def _update_balls(self):
        balls_to_remove = [ball for ball in self.balls if ball.body.position.x < -50 or ball.body.position.x > self.screen_width + 50]
        for ball in balls_to_remove:
            self._space.remove(ball, ball.body)
            self.balls.remove(ball)
