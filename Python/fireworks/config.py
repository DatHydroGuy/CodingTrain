from colorsys import hls_to_rgb
from pygame import Vector2, Color

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000
GRAVITY = Vector2(0, 0.2)
NUM_PARTICLES_IN_BURST = 100
FIREWORK_LAUNCH_THRESHOLD = 0.1
MAX_ANGLE = 5
LIFESPAN_DECAY_RATE = 4
MAX_LIFESPAN = 255
MAX_BURST_SPEED = 7


def colour_by_hue(hue, alpha, is_rocket):
    r, g, b = hls_to_rgb(hue, 0.5, 1.0)
    r, g, b = [int(255 * i) for i in (r, g, b)]
    return Color(r, g, b, 255 if is_rocket else int(alpha * 255))
