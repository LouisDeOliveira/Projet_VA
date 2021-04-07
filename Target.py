import pygame
import math
import uuid
import random
import numpy as np
from Utils import *
white = (255, 255, 255)
red = (255, 0, 0)
f = 2
maxacc = 900.0
maxspeed = 100.0
circle_list = []
shadow = (80, 80, 80)
lightgreen = (0, 255, 0)
green = (0, 200, 0)
blue = (0, 0, 128)
lightblue = (0, 0, 255)
lightred = (255, 100, 100)
purple = (102, 0, 102)
lightpurple = (153, 0, 153)
res = 150
k = 50000


class Target():
    """ Voir drone
        targeted : Boolean : True si ciblé par un Chercheur """

    def __init__(self, x, y, speed, direction, size, id, env):
        self.id = id
        self.speed = speed
        self.acc = acc
        self.env = env
        self.pos = x, y
        self.dir = direction
        self.size = size
        self.targeted = False

    def display(self):
        a = self.dir
        x, y = self.pos
        s = self.size

        pygame.draw.line(env.screen, red,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) - a),
                          y - (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) - a)),
                         (x + s * math.cos(-a), y + s * math.sin(-a)))

        pygame.draw.line(env.screen, red,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) + a),
                          y + (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) + a)),
                         (x + s * math.cos(a), y + s * math.sin(-a)))

        pygame.draw.line(env.screen, red,
                         (x - (s * math.sqrt(2) / 2) * math.cos(-a + math.pi / 4),
                          y - (s * math.sqrt(2) / 2) * math.sin(-a + math.pi / 4)),
                         (x - (s * math.sqrt(2) / 2) * math.cos(a + math.pi / 4),
                          y + (s * math.sqrt(2) / 2) * math.sin(a + math.pi / 4)))

    def wander(self):
        return self.x, self.y, self.dir

    def step(self):
        self.x, self.y, self.dir = self.wander()

    def wander(self, r=100):
        if self.destination == None:
            if self.target == None:
                theta = random.random()*2*math.pi
                dest_x, dest_y = max(min(self.x + r*math.cos(theta), self.env.width), 0), max(
                    min(self.y + r*math.sin(theta), self.env.height), 0)

                self.destination = dest_x, dest_y
            else:
                dest_x, dest_y = self.target.x, self.target.y
                self.destination = dest_x, dest_y

        elif point_distance(self.x, self.y, self.destination[0], self.destination[1]) < 1 and self.target == None:
            self.destination = None
            theta = random.random()*2*math.pi
            dest_x, dest_y = max(min(self.x + r*math.cos(theta), self.env.width), 0), max(
                min(self.y + r*math.sin(theta), self.env.height), 0)
            self.destination = dest_x, dest_y

        elif self.destination != None and self.target != None:
            if self.destination != self.target:
                self .destination = self.target.x, self.target.y
