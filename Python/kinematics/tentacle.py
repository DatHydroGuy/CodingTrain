from pygame import Vector2
from inverse_segment_fixed_point import Segment


class Tentacle:
    def __init__(self, base_position: Vector2, num_segments: int, segment_length: int):
        self.num_segments = num_segments
        self.base_position = base_position
        self.segment_length = segment_length
        segment_width = 4
        self.segments = [Segment(base_position, segment_length, segment_width)]
        for i in range(1, num_segments):
            self.segments.append(Segment(self.segments[i - 1].end, segment_length, segment_width))

    def update(self, target_x, target_y):
        end_seg = self.segments[self.num_segments - 1]
        end_seg.follow(target_x, target_y)
        end_seg.update()

        for i in range(self.num_segments - 2, -1, -1):
            self.segments[i].follow(self.segments[i + 1].position.x, self.segments[i + 1].position.y)
            self.segments[i].update()

        self.segments[0].constrain_position(self.base_position)
        for i in range(1, self.num_segments):
            self.segments[i].constrain_position(self.segments[i - 1].end)

    def show(self, surface):
        for segment in self.segments:
            segment.show(surface)
