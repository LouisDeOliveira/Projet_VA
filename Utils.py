import pygame
import math
import uuid
import random
import numpy as np


def distance(Agent1, Agent2):
    """ distance entre deux agents """
    x1, y1 = Agent1.pos
    x2, y2 = Agent2.pos

    d = math.sqrt((x1-x2)**2+(y1-y2)**2)
    return d


def point_distance(x1, y1, x2, y2):
    """ distance entre deux points """
    d = math.sqrt((x1-x2)**2+(y1-y2)**2)
    return d


def vect_AB(agentA, agentB):
    v_x = agentB.pos[0]-agentA.pos[0]
    v_y = agentB.pos[1]-agentA.pos[1]

    if (v_x**2+v_x**2) == 0:
        return np.array([0, 0])
    else:
        return np.array([v_x, v_y])/np.sqrt(v_x**2+v_x**2)


def vect_norme_carre(vect):
    return vect[0]**2 + vect[1]**2


def normalize_vector(vect):
    return vect/np.sqrt(vect_norme_carre(vect))
