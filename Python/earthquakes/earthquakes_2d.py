from math import pi, tan, log, radians
from datetime import datetime

from numpy import interp
import pygame
import csv

from pygame import Vector2

from earthquakes.marker import Marker


class Earthquakes2D:
    def __init__(self) -> None:
        self.screen_width = 1024
        self.screen_height = 661

        pygame.init()
        pygame.display.set_caption("Visualising 30 days of earthquake data")

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF, 32)

    @staticmethod
    def convert_longitude_to_screen_x_coordinate(longitude, zoom):
        longitude = radians(longitude)
        a = (256 / pi) * pow(2, zoom)
        b = longitude + pi
        return a * b

    @staticmethod
    def convert_latitude_to_screen_y_coordinate(latitude, zoom):
        latitude = radians(latitude)
        a = (256 / pi) * pow(2, zoom)
        b = tan(pi / 4 + latitude / 2)
        c = pi - log(b)
        return a * c

    def start(self) -> None:
        world = pygame.image.load(r'res\Web_maps_Mercator_projection.png')

        markers = []
        max_time = 0
        min_time = 9999999999

        zoom = 1
        center_lat = 0
        center_lon = 0
        center_x = self.convert_longitude_to_screen_x_coordinate(center_lon, zoom)
        center_y = self.convert_latitude_to_screen_y_coordinate(center_lat, zoom)
        center_x = self.screen_width / 2 - center_x
        center_y = self.screen_height / 2 - center_y

        # # https://earthquake.usgs.gov/earthquakes/feed/v1.0/csv.php
        # feed = r"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv"
        with open(r"res\all_month.csv", encoding='utf8', newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"', dialect='unix')
            for idx, row in enumerate(csv_reader):
                if idx == 0:
                    continue
                lat = float(row[1])
                lon = float(row[2])
                mag = float(row[4])
                x = self.convert_longitude_to_screen_x_coordinate(lon, zoom) + center_x
                y = self.convert_latitude_to_screen_y_coordinate(lat, zoom) + center_y
                timestamp = datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
                if timestamp > max_time:
                    max_time = timestamp
                if timestamp < min_time:
                    min_time = timestamp
                markers.append(Marker(Vector2(x, y), mag, timestamp))

        for marker in markers:
            marker.timestamp = interp(marker.timestamp - min_time, [0, max_time - min_time], [0, 4])

        marker_time = 0

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            self.screen.fill((0, 0, 0))
            self.screen.blit(world, (0, 0))

            # render
            for marker in markers:
                marker.update(marker_time)
                marker.show(self.screen)

            marker_time += 1 / 60
            pygame.display.update()
            self.__clock.tick(60)
