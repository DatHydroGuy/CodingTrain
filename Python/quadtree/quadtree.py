import pygame.draw


class Point:
    def __init__(self, x, y, user_data):
        self.x = x
        self.y = y
        self.user_data = user_data

    def __repr__(self):
        return f'(x, y) = ({self.x}, {self.y})'


class Rectangle:
    def __init__(self, x, y, half_width, half_height):
        self.x = x
        self.y = y
        self.half_width = half_width
        self.half_height = half_height

    def contains(self, point: Point) -> bool:
        return (self.x - self.half_width <= point.x < self.x + self.half_width and
                self.y - self.half_height <= point.y < self.y + self.half_height)

    def intersects(self, rectangle):
        return not (rectangle.x - rectangle.half_width > self.x + self.half_width or
                    rectangle.x + rectangle.half_width < self.x - self.half_width or
                    rectangle.y - rectangle.half_height > self.y + self.half_height or
                    rectangle.y + rectangle.half_height < self.y - self.half_height)

    def __repr__(self):
        return f'(x, y, w/2, h/2): ({self.x}, {self.y}, {self.half_width}, {self.half_height})'


class Circle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.half_width = radius
        self.half_height = radius

    def contains(self, point: Point) -> bool:
        return (self.x - point.x) ** 2 + (self.y - point.y) ** 2 <= self.half_width ** 2

    def intersects(self, other):
        return not (other.x - other.half_width > self.x + self.half_width or
                    other.x + other.half_width < self.x - self.half_width or
                    other.y - other.half_height > self.y + self.half_height or
                    other.y + other.half_height < self.y - self.half_height)

    def __repr__(self):
        return f'(x, y, w/2, h/2): ({self.x}, {self.y}, {self.half_width}, {self.half_height})'


class QuadTree:
    def __init__(self, boundary: Rectangle, capacity: int) -> None:
        self.boundary = boundary
        self.capacity = capacity
        self.points = []
        self.nw = None
        self.ne = None
        self.sw = None
        self.se = None
        self.subdivided = False

    def subdivide(self):
        self.nw = QuadTree(Rectangle(self.boundary.x - self.boundary.half_width / 2,
                                     self.boundary.y - self.boundary.half_height / 2,
                                     self.boundary.half_width / 2,
                                     self.boundary.half_height / 2), self.capacity)
        self.ne = QuadTree(Rectangle(self.boundary.x + self.boundary.half_width / 2,
                                     self.boundary.y - self.boundary.half_height / 2,
                                     self.boundary.half_width / 2,
                                     self.boundary.half_height / 2), self.capacity)
        self.sw = QuadTree(Rectangle(self.boundary.x - self.boundary.half_width / 2,
                                     self.boundary.y + self.boundary.half_height / 2,
                                     self.boundary.half_width / 2,
                                     self.boundary.half_height / 2), self.capacity)
        self.se = QuadTree(Rectangle(self.boundary.x + self.boundary.half_width / 2,
                                     self.boundary.y + self.boundary.half_height / 2,
                                     self.boundary.half_width / 2,
                                     self.boundary.half_height / 2), self.capacity)
        self.subdivided = True

    def insert(self, point: Point) -> bool:
        if not self.boundary.contains(point):
            return False

        if self.subdivided:
            return self.nw.insert(point) or self.ne.insert(point) or self.sw.insert(point) or self.se.insert(point)
        else:
            if len(self.points) < self.capacity:
                self.points.append(point)
                return True
            else:
                if not self.subdivided:
                    self.subdivide()

                for p in self.points[::-1]:
                    self.nw.insert(p)
                    self.ne.insert(p)
                    self.sw.insert(p)
                    self.se.insert(p)
                    self.points.remove(p)

                return self.nw.insert(point) or self.ne.insert(point) or self.sw.insert(point) or self.se.insert(point)

    def query(self, query_rect, found):
        if found is None:
            found = []

        if not self.boundary.intersects(query_rect):
            return found
        else:
            for p in self.points:
                if query_rect.contains(p):
                    found.append(p)

            if self.subdivided:
                self.nw.query(query_rect, found)
                self.ne.query(query_rect, found)
                self.sw.query(query_rect, found)
                self.se.query(query_rect, found)

            return found

    def show(self, screen: pygame.display):
        pygame.draw.rect(screen, pygame.color.Color('green'),
                         (self.boundary.x - self.boundary.half_width,
                          self.boundary.y - self.boundary.half_height,
                          self.boundary.half_width * 2,
                          self.boundary.half_height * 2),
                         width=1)
        if self.subdivided:
            self.nw.show(screen)
            self.ne.show(screen)
            self.sw.show(screen)
            self.se.show(screen)

        for point in self.points:
            pygame.draw.circle(screen, pygame.color.Color('blue'), (point.x, point.y), 2)

    def __repr__(self):
        ret_str = (f'boundary: {self.boundary}\ncapacity: {self.capacity}\n'
                   f'points: {self.points}\nsubdivided: {self.subdivided}\n')
        if self.subdivided:
            ret_str += f'QUADS:\nnw: {self.nw}\nne: {self.ne}\nsw: {self.sw}\nse: {self.se}\n'
        return ret_str
