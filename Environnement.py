import pygame
import math
import uuid
import random
import numpy as np
from Target import Target
from Verificateur import Verificateur
from Chercheur import Chercheur
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
tick_freq = 100
dt = 1/tick_freq
q = 100000


class Environment():
    """
    width : int : largeur de l'écran
    height : int : hauteur de l'écran
    Agent_list : list : liste de tous les agents (Chercheur et Target) de l'environment"""

    def __init__(self, n_chercheurs, n_verificateurs, n_targets, width, height, screen):
        self.width = width
        self.height = height
        self.Agent_list = []
        self.res = 50
        self.screen = screen
        for _ in range(n_chercheurs):
            self.Agent_list.append(Chercheur(random.random(
            )*self.width/2, random.random()*self.height/2, 100, -90, 5, int(uuid.uuid1()), self))

        for _ in range(n_targets):
            self.Agent_list.append(Target(random.random(
            )*self.width, random.random()*self.height, int(uuid.uuid1()), self))

        for _ in range(n_verificateurs):
            self.Agent_list.append(Verificateur(random.random(
            )*self.width/2, random.random()*self.height/2, 100, -90, 5, int(uuid.uuid1()), self))

    def step(self):
        for agent in self.Agent_list:
            agent.step()

    def barycentre(self):
        gx = 0
        gy = 0
        g = np.zeros(2)
        n = 0
        for agent in self.Agent_list:
            if type(agent) == Chercheur:
                n += 1
                gx += agent.pos[0]
                gy += agent.pos[1]
        g[0], g[1] = gx/n, gy/n
        return g

    def update(self):
        self.N0 = np.shape(self.mesh)[0]*np.shape(self.mesh)[1]
        for agentA in self.Agent_list:
            if type(agentA) == Chercheur:
                ax = 0
                ay = 0
                for agentB in self.Agent_list:
                    if type(agentB) == Chercheur:
                        if agentA.id != agentB.id and agentB in agentA.neighbours():

                            f_ressort_x = agentA.k * \
                                (distance(agentA, agentB) - agentA.l0) * \
                                vect_AB(agentA, agentB)[0]

                            f_ressort_y = agentA.k * \
                                (distance(agentA, agentB) - agentA.l0) * \
                                vect_AB(agentA, agentB)[1]
                            ax += f_ressort_x
                            ay += f_ressort_y

                f_frott_x = f*agentA.speed[0]
                f_frott_y = f*agentA.speed[1]
                f_charge_x = 0
                f_charge_y = 0
                size = np.shape(self.mesh)
                for i in range(size[0]):
                    for j in range(size[1]):
                        if self.mesh[i][j] == 1:
                            pos_charge = np.array([self.res*j, self.res*i])
                            r = point_distance(
                                agentA.pos[0], agentA.pos[1], pos_charge[0], pos_charge[1])
                            vect = agentA.pos - pos_charge
                            vect = vect/r
                            f_charge_x += -k/(r**2)*vect[0]
                            f_charge_y += -k/(r**2)*vect[1]
                if self.active_nodes() > 0:
                    ax += f_charge_x*self.N0/self.active_nodes()
                    ay += f_charge_y*self.N0/self.active_nodes()

                ax -= f_frott_x
                ay -= f_frott_y

                vect_acc = np.array([ax, ay])
                if vect_norme_carre(vect_acc) > maxacc**2:
                    agentA.acc = maxacc*normalize_vector(vect_acc)
                else:
                    agentA.acc = vect_acc

            if type(agentA) == Verificateur:
                dx = agentA.pos[0]-self.barycentre()[0]
                dy = agentA.pos[1]-self.barycentre()[1]
                f_ressort_x = -agentA.k * \
                    (math.sqrt((dx)**2+(dy)**2) - agentA.l0) * \
                    dx/(np.sqrt(dx**2+dy**2))
                f_ressort_y = -agentA.k * \
                    (math.sqrt((dx)**2+(dy)**2) - agentA.l0) * \
                    dy/(np.sqrt(dx**2+dy**2))

                f_frott_x = f*agentA.speed[0]
                f_frott_y = f*agentA.speed[1]
                for agentB in self.Agent_list:
                    if type(agentB) == Verificateur and agentA.id != agentB.id:
                        f_charge_x += q / \
                            distance(agentA, agentB)**2 * \
                            vect_AB(agentA, agentB)[0]
                        f_charge_y += q / \
                            distance(agentA, agentB)**2 * \
                            vect_AB(agentA, agentB)[1]
                ax = f_ressort_x-f_frott_x
                ay = f_ressort_y-f_frott_y

                vect_acc = np.array([ax, ay])
                if vect_norme_carre(vect_acc) > maxacc**2:
                    agentA.acc = maxacc*normalize_vector(vect_acc)
                else:
                    agentA.acc = vect_acc

        for agent in self.Agent_list:
            if type(agent) != Target:
                vect_vit = np.array(
                    [agent.speed[0] + dt*agent.acc[0], agent.speed[1] + dt*agent.acc[1]])
                if vect_norme_carre(vect_vit) > maxspeed**2:
                    agentA.speed = maxspeed*normalize_vector(vect_vit)
                else:
                    agent.speed = vect_vit

                agent.pos[0] = agent.pos[0] + dt*agent.speed[0]
                agent.pos[1] = agent.pos[1] + dt*agent.speed[1]

            # conditions de bord :  a revoir pour rendre plus réaliste
            if agent.pos[0] < 0:
                agent.pos[0] = 0
                agent.speed[0] = 0
            if agent.pos[0] > self.width:
                agent.pos[0] = self.width
                agent.speed[0] = 0
            if agent.pos[1] < 0:
                agent.pos[1] = 0
                agent.speed[1] = 0
            if agent.pos[1] > self.height:
                agent.pos[1] = self.height
                agent.speed[1] = 0

    def draw_graph(self):
        """ Dessine le graphe reliant les Drones à portée de communication (càd qui sont voisins)"""
        edge_list_c = []
        edge_list_v = []
        for agent in self.Agent_list:
            if type(agent) == Chercheur:
                for neighbour in agent.neighbours():
                    if type(neighbour) == Chercheur:
                        if [(neighbour.pos[0], neighbour.pos[1]), (agent.pos[0], agent.pos[1])] not in edge_list_c and [(agent.pos[0], agent.pos[1]), (neighbour.pos[0], neighbour.pos[1])] not in edge_list_c:
                            edge_list_c.append(
                                [(neighbour.pos[0], neighbour.pos[1]), (agent.pos[0], agent.pos[1])])

            if type(agent) == Verificateur:
                for neighbour in agent.neighbours():
                    if type(neighbour) == Chercheur:
                        if [(neighbour.pos[0], neighbour.pos[1]), (agent.pos[0], agent.pos[1])] not in edge_list_v and [(agent.pos[0], agent.pos[1]), (neighbour.pos[0], neighbour.pos[1])] not in edge_list_v:
                            edge_list_v.append(
                                [(neighbour.pos[0], neighbour.pos[1]), (agent.pos[0], agent.pos[1])])
                    if type(neighbour) == Verificateur:
                        if [(neighbour.pos[0], neighbour.pos[1]), (agent.pos[0], agent.pos[1])] not in edge_list_v and [(agent.pos[0], agent.pos[1]), (neighbour.pos[0], neighbour.pos[1])] not in edge_list_v:
                            edge_list_v.append(
                                [(neighbour.pos[0], neighbour.pos[1]), (agent.pos[0], agent.pos[1])])

        for edge in edge_list_c:
            pygame.draw.line(
                self.screen, white, (edge[0][0], edge[0][1]), (edge[1][0], edge[1][1]))
        for edge in edge_list_v:
            pygame.draw.line(self.screen, lightgreen,
                             (edge[0][0], edge[0][1]), (edge[1][0], edge[1][1]))

    def show_circles(self):
        for agent in self.Agent_list:
            if type(agent) == Chercheur:
                circle_list.append((agent.pos[0], agent.pos[1]))
        for circle in circle_list:
            pygame.draw.circle(self.screen, shadow, circle, self.res/2)

    def mesh_matrix(self):
        m_width = int(np.floor(self.width/self.res))+1
        m_height = int(np.floor(self.height/self.res))+1
        mesh = np.ones((m_height, m_width))
        self.mesh = mesh

    def show_mesh(self):
        size = np.shape(self.mesh)
        for i in range(size[0]):
            for j in range(size[1]):
                if self.mesh[i][j] == 1:
                    point = (j*self.res, i*self.res)
                    pygame.draw.circle(self.screen, red, point, 3)

    def active_nodes(self):
        N = 0
        size = np.shape(self.mesh)
        for i in range(size[0]):
            for j in range(size[1]):
                if self.mesh[i][j] == 1:
                    N += 1
        return N

    def score(self):
        score_couverture = 0
        score_cibles = 0
        score_temps = 0
        score_batterie = 0
