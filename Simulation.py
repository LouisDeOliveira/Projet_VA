import pygame
import math
import uuid
import random
import numpy as np
from Environnement import Environment
from Target import Target
from Verificateur import Verificateur
from Chercheur import Chercheur
from Utils import *

white = (255, 255, 255)
red = (255, 0, 0)
shadow = (80, 80, 80)
lightgreen = (0, 255, 0)
green = (0, 200, 0)
blue = (0, 0, 128)
lightblue = (0, 0, 255)
lightred = (255, 100, 100)
purple = (102, 0, 102)
lightpurple = (153, 0, 153)


pygame.init()
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
env = Environment(5, 0, 0, width, height, screen)
Running = True
tick_freq = env.tick_freq
dt = env.dt
t = 0
# Screen Update Speed (FPS)
clock = pygame.time.Clock()
env.mesh_matrix()
while Running:
    t += dt
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False

    env.update()
    #env.show_circles()
    for agent in env.Agent_list:
        if type(agent) == Chercheur:
            agent.check_mesh()
        agent.display()

    env.draw_graph()
    env.show_mesh()
    pygame.display.update()
    screen.fill((0, 0, 0))

    # Setting FPS
    clock.tick(tick_freq)
# Shutdown
pygame.quit()
