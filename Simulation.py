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
from Benchmark import *


# constantes
white = (255, 255, 255)
red = (255, 0, 0)
f = 2
maxacc = 2.0
maxspeed = 20.0
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
tick_freq = 30
dt = 1/tick_freq
t = 0
# initialisation des listes
T = np.linspace(0, 100, 10000)
V = []


pygame.init()
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
env = Environment(5, 0, 0, width, height, screen)
Running = True

# Screen Update Speed (FPS)
clock = pygame.time.Clock()
env.mesh_matrix()
while Running and t < 100:
    t += dt
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False

    env.update()
    # env.show_circles()
    for agent in env.Agent_list:
        if type(agent) == Chercheur:
            agent.check_mesh()
        agent.display()
    V.append(np.sqrt(vect_norme_carre(env.Agent_list[0].speed)))

    env.draw_graph()
    env.show_mesh()
    pygame.display.update()
    screen.fill((0, 0, 0))

    # Setting FPS
    clock.tick(tick_freq)
# Shutdown
pygame.quit()

# calculs vitesse
show_XY_graph(T, V)
