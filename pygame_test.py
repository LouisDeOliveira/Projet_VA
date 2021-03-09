import pygame
import math
import uuid
import random
import numpy as np

white = (255, 255, 255)
red = (255, 0, 0)
f = 0.1
maxacc = 300.0


class Drone():
    """
    speed : int/float : vitess du drone
    env : Environment
    state : normal (pas de cible, en recherche), finder (à trouvé une cible), helper (aide un finder) 
    battery : niveau de batterie : 0 -> dcd
    dir : float : direction du drone
    size : Taille d'affichage du drone
    target : Target :  cible du drone
    id : int : identifiant unique du Drone
    destination : tuple : destination du drone
    inbox : list : liste des messages reçus par le drone
    message :  dict : message a envoyer

    """

    def __init__(self, x, y, speed, direction, size, id, env):
        self.speed = speed
        self.env = env
        self.pos = np.array([x, y])
        self.speed = np.array([0, 0])
        self.acc = np.array([0, 0])
        self.k = 1
        self.l0 = 150
        self.maxspeed = speed
        self.state = 'normal'
        self.battery = None
        self.dir = direction
        self.size = size
        self.target = None
        self.id = id
        self.destination = None
        self.inbox = []
        self.message = {'sender_id': None, 'recipient_id': None, 'time': None, 'message': {'status': {'x': None, 'y': None, 'z': None, 'dir': None,
                                                                                                      'speed': None, 'state': None, 'battery': None}, 'alert': {'verif': None, 'help': None, 't_x': None, 't_y': None, 't_z': None}}}

    def make_message(self, recipient):
        self.message['sender_id'] = self.id
        self.message['recipient_id'] = recipient.id
        self.message['time'] = t
        self.message['message']['status']['x'] = self.x
        self.message['message']['status']['y'] = self.y
        self.message['message']['status']['z'] = self.z
        self.message['message']['status']['dir'] = self.dir
        self.message['message']['status']['speed'] = self.speed
        self.message['message']['status']['state'] = self.state
        self.message['message']['status']['battery'] = self.battery

        if self.target != None:
            self.message['message']['alert']['t_x'] = self.target.x
            self.message['message']['alert']['t_y'] = self.target.y
            self.message['message']['alert']['t_z'] = self.target.z

    def read_message(self):
        pass

    def send_message(self):
        pass

    def score(self):
        pass

    def display(self):
        """ Dessine le drone sur l'écran """

        a = self.dir
        x = self.pos[0]
        y = self.pos[1]
        s = self.size

        pygame.draw.line(screen, white,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) - a),
                          y - (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) - a)),
                         (x + s * math.cos(-a), y + s * math.sin(-a)))

        pygame.draw.line(screen, white,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) + a),
                          y + (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) + a)),
                         (x + s * math.cos(a), y + s * math.sin(-a)))

        pygame.draw.line(screen, white,
                         (x - (s * math.sqrt(2) / 2) * math.cos(-a + math.pi / 4),
                          y - (s * math.sqrt(2) / 2) * math.sin(-a + math.pi / 4)),
                         (x - (s * math.sqrt(2) / 2) * math.cos(a + math.pi / 4),
                          y + (s * math.sqrt(2) / 2) * math.sin(a + math.pi / 4)))

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

    def move(self):

        try:

            d = point_distance(
                self.x, self.y, self.destination[0], self.destination[1])

            cosr = (self.destination[0] - self.x)/d
            sinr = (self.destination[1] - self.y)/d
            new_x = max(min(self.x + cosr * self.speed*dt,
                            self.env.width), 0)
            new_y = max(min(self.y + sinr * self.speed*dt,
                            self.env.height), 0)
            new_dir = math.atan2(-sinr, cosr)
            return new_x, new_y, new_dir

        except:
            return self.x, self.y, self.dir

    def neighbours(self, r=200):
        """ liste des agents (Drone ou Target) à distance <= r du Drone """

        return [self.env.Agent_list[i] for i in range(len(self.env.Agent_list)) if distance(self, self.env.Agent_list[i]) < r and self.env.Agent_list[i] != self]

    def target_agent(self):
        """ Attribue en tant que cible la cible la plus proche du champ de vision du drone si celui-ci n'en a pas déjà une """

        if self.target == None:
            min_distance = math.inf
            best_agent = None
            for agent in self.neighbours():
                if type(agent) == Target:
                    if distance(self, agent) < min_distance and agent.targeted == False:
                        min_distance = distance(self, agent)
                        best_agent = agent
            if best_agent != None:
                best_agent.targeted = True
            return best_agent
        else:
            return self.target

    def step(self):
        self.target = self.target_agent()
        self.wander()
        self.x, self.y, self.dir = self.move()


class Target():
    """ Voir drone
        targeted : Boolean : True si ciblé par un Drone """

    def __init__(self, x, y, speed, direction, size, id, env):
        self.id = id
        self.speed = speed
        self.env = env
        self.x = x
        self.y = y
        self.dir = direction
        self.size = size
        self.targeted = False

    def display(self):
        a = self.dir
        x = self.x
        y = self.y
        s = self.size

        pygame.draw.line(screen, red,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) - a),
                          y - (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) - a)),
                         (x + s * math.cos(-a), y + s * math.sin(-a)))

        pygame.draw.line(screen, red,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) + a),
                          y + (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) + a)),
                         (x + s * math.cos(a), y + s * math.sin(-a)))

        pygame.draw.line(screen, red,
                         (x - (s * math.sqrt(2) / 2) * math.cos(-a + math.pi / 4),
                          y - (s * math.sqrt(2) / 2) * math.sin(-a + math.pi / 4)),
                         (x - (s * math.sqrt(2) / 2) * math.cos(a + math.pi / 4),
                          y + (s * math.sqrt(2) / 2) * math.sin(a + math.pi / 4)))

    def wander(self):
        return self.x, self.y, self.dir

    def step(self):
        self.x, self.y, self.dir = self.wander()


class Environment():
    """ 
    width : int : largeur de l'écran
    height : int : hauteur de l'écran
    Agent_list : list : liste de tous les agents (Drone et Target) de l'environment"""

    def __init__(self, n_drones, n_targets, width, height):
        self.width = width
        self.height = height
        self.Agent_list = []
        for _ in range(n_drones):
            self.Agent_list.append(Drone(random.random(
            )*self.width/2, random.random()*self.height/2, 100, -90, 5, int(uuid.uuid1()), self))
        for _ in range(n_targets):
            self.Agent_list.append(Target(random.random(
            )*self.width, random.random()*self.height, 5, -90, 5, int(uuid.uuid1()), self))

    def step(self):
        for agent in self.Agent_list:
            agent.step()

    def update(self):
        for agentA in self.Agent_list:
            ax = 0
            ay = 0
            for agentB in self.Agent_list:
                if agentA.id != agentB.id and agentB in agentA.neighbours():
                    ax += agentA.k*(distance(agentA, agentB) -
                                    agentA.l0)*vect_AB(agentA, agentB)[0]-f*agentA.speed[0]
                    ay += agentA.k*(distance(agentA, agentB) -
                                    agentA.l0)*vect_AB(agentA, agentB)[1]-f*agentA.speed[1]

            agentA.acc = np.array([ax, ay])

        for agent in self.Agent_list:
            agent.speed[0] = agent.speed[0] + dt*agent.acc[0]
            agent.speed[1] = agent.speed[1] + dt*agent.acc[1]
            agent.pos[0] = agent.pos[0] + dt*agent.speed[0]
            agent.pos[1] = agent.pos[1] + dt*agent.speed[1]

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
        edge_list = []
        for agent in self.Agent_list:
            if type(agent) == Drone:
                for neighbour in agent.neighbours():
                    if type(neighbour) == Drone:
                        if [(neighbour.pos[0], neighbour.pos[1]), (agent.pos[0], agent.pos[1])] not in edge_list and [(agent.pos[0], agent.pos[1]), (neighbour.pos[0], neighbour.pos[1])] not in edge_list:
                            edge_list.append(
                                [(neighbour.pos[0], neighbour.pos[1]), (agent.pos[0], agent.pos[1])])

        for edge in edge_list:
            pygame.draw.line(
                screen, white, (edge[0][0], edge[0][1]), (edge[1][0], edge[1][1]))


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

    return np.array([v_x, v_y])/np.sqrt(v_x**2+v_x**2)


if __name__ == '__main__':
    env = Environment(10, 0, 750, 750)
    pygame.init()
    width, height = env.width, env.height
    screen = pygame.display.set_mode((width, height))
    Running = True
    tick_freq = 60
    dt = 1/tick_freq
    t = 0
    # Screen Update Speed (FPS)
    clock = pygame.time.Clock()

    while Running:
        t += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Running = False

        env.update()
        for agent in env.Agent_list:
            agent.display()
        env.draw_graph()
        pygame.display.update()
        screen.fill((0, 0, 0))
        # Setting FPS
        clock.tick(tick_freq)
    # Shutdown
    pygame.quit()
