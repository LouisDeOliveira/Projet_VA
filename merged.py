import pygame
import math
import uuid
import random
import numpy as np

white = (255, 255, 255)
red = (255, 0, 0)
f = 1
maxacc = 900.0
maxspeed = 10.0
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


class Chercheur():
    """
    speed : int/float : vitess du drone
    env : Environment
    state : normal (pas de cible, en recherche), finder (à trouvé une cible), helper (aide un finder)
    battery : niveau de batterie : 0 -> dcd
    dir : float : direction du drone
    size : Taille d'affichage du drone
    target : Target :  cible du drone
    id : int : identifiant unique du drone
    destination : tuple : destination du drone
    inbox : list : liste des messages reçus par le drone
    message :  dict : message a envoyer

    """

    def __init__(self, x, y, speed, direction, size, id, env):
        self.speed = speed
        self.env = env
        self.pos = np.array([x, y])
        self.speed = np.array([0., 0.])
        self.acc = np.array([0., 0.])
        self.k = 12
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

    def neighbours(self, r=200):
        """ liste des agents (Chercheur ou Target) à distance <= r du Chercheur """

        return [self.env.Agent_list[i] for i in range(len(self.env.Agent_list)) if distance(self, self.env.Agent_list[i]) < r and self.env.Agent_list[i] != self]

    def check_mesh(self):
        colonne = round(self.pos[0] / self.env.res)
        ligne = round(self.pos[1] / self.env.res)
        if point_distance(self.pos[0], self.pos[1], self.env.res*colonne, self.env.res*ligne) < self.env.res:
            self.env.mesh[ligne][colonne] = 0
        if point_distance(self.pos[0], self.pos[1], self.env.res*(colonne+1), self.env.res*ligne) < self.env.res:
            self.env.mesh[ligne][colonne] = 0
        if point_distance(self.pos[0], self.pos[1], self.env.res*colonne, self.env.res*(ligne+1)) < self.env.res:
            self.env.mesh[ligne][colonne] = 0
        if point_distance(self.pos[0], self.pos[1], self.env.res*(colonne+1), self.env.res*(ligne+1)) < self.env.res:
            self.env.mesh[ligne][colonne] = 0
        if point_distance(self.pos[0], self.pos[1], self.env.res*(colonne), self.env.res*(ligne-1)) < self.env.res:
            self.env.mesh[ligne][colonne] = 0
        if point_distance(self.pos[0], self.pos[1], self.env.res*(colonne-1), self.env.res*(ligne)) < self.env.res:
            self.env.mesh[ligne][colonne] = 0
        if point_distance(self.pos[0], self.pos[1], self.env.res*(colonne-1), self.env.res*(ligne-1)) < self.env.res:
            self.env.mesh[ligne][colonne] = 0
        if point_distance(self.pos[0], self.pos[1], self.env.res*(colonne-1), self.env.res*(ligne+1)) < self.env.res:
            self.env.mesh[ligne][colonne] = 0
        if point_distance(self.pos[0], self.pos[1], self.env.res*(colonne+1), self.env.res*(ligne-1)) < self.env.res:
            self.env.mesh[ligne][colonne] = 0


class Verificateur():
    """
    speed : int/float : vitess du drone
    env : Environment
    state : normal (pas de cible, en recherche), finder (à trouvé une cible), helper (aide un finder)
    battery : niveau de batterie : 0 -> dcd
    dir : float : direction du drone
    size : Taille d'affichage du drone
    target : Target :  cible du drone
    id : int : identifiant unique du drone
    destination : tuple : destination du drone
    inbox : list : liste des messages reçus par le drone
    message :  dict : message a envoyer

    """

    def __init__(self, x, y, speed, direction, size, id, env):
        self.speed = speed
        self.env = env
        self.pos = np.array([x, y])
        self.speed = np.array([0., 0.])
        self.acc = np.array([0., 0.])
        self.k = 10
        self.l0 = 150
        self.maxspeed = maxspeed
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

    def step(self):
        self.target = self.target_agent()
        self.wander()
        self.x, self.y, self.dir = self.move()

    def display(self):
        """ Dessine le drone sur l'écran """

        a = self.dir
        x = self.pos[0]
        y = self.pos[1]
        s = self.size

        pygame.draw.line(screen, lightgreen,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) - a),
                          y - (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) - a)),
                         (x + s * math.cos(-a), y + s * math.sin(-a)))

        pygame.draw.line(screen, lightgreen,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) + a),
                          y + (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) + a)),
                         (x + s * math.cos(a), y + s * math.sin(-a)))

        pygame.draw.line(screen, lightgreen,
                         (x - (s * math.sqrt(2) / 2) * math.cos(-a + math.pi / 4),
                          y - (s * math.sqrt(2) / 2) * math.sin(-a + math.pi / 4)),
                         (x - (s * math.sqrt(2) / 2) * math.cos(a + math.pi / 4),
                          y + (s * math.sqrt(2) / 2) * math.sin(a + math.pi / 4)))

    def neighbours(self, r=200):
        """ liste des agents (Chercheur ou Target) à distance <= r du Chercheur """

        return [self.env.Agent_list[i] for i in range(len(self.env.Agent_list)) if distance(self, self.env.Agent_list[i]) < r and self.env.Agent_list[i] != self]


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


class Charges():
    def __init__(self, value, pos, env):
        self.value = value
        self.pos = pos
        self.env = env


class Environment():
    """
    width : int : largeur de l'écran
    height : int : hauteur de l'écran
    Agent_list : list : liste de tous les agents (Chercheur et Target) de l'environment"""

    def __init__(self, n_chercheurs, n_verificateurs, n_targets, width, height):
        self.width = width
        self.height = height
        self.Agent_list = []
        self.res = 50
        for _ in range(n_chercheurs):
            self.Agent_list.append(Chercheur(random.random(
            )*self.width/2, random.random()*self.height/2, 100, -90, 5, int(uuid.uuid1()), self))

        for _ in range(n_targets):
            self.Agent_list.append(Target(random.random(
            )*self.width, random.random()*self.height, 5, -90, 5, int(uuid.uuid1()), self))

        for _ in range(n_verificateurs):
            self.Agent_list.append(Verificateur(random.random(
            )*self.width/2, random.random()*self.height/2, 100, -90, 5, int(uuid.uuid1()), self))

    def step(self):
        for agent in self.Agent_list:
            agent.step()

    def update(self):
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
                            f_frott_x = f*agentA.speed[0]
                            f_ressort_y = agentA.k * \
                                (distance(agentA, agentB) - agentA.l0) * \
                                vect_AB(agentA, agentB)[1]
                            f_frott_y = f*agentA.speed[1]
                            f_charge_x = 0
                            f_charge_y = 0
                            # forces attractive du maillage
                            size = np.shape(self.env.mesh)
                            for i in range(size[0]):
                                for j in range(size[1]):
                                    if self.env.mesh[i][j] == 1:

                            ax += f_ressort_x - f_frott_x
                            ay += f_ressort_y - f_frott_y

                vect_acc = np.array([ax, ay])
                if vect_norme_carre(vect_acc) > maxacc**2:
                    agentA.acc = maxacc*normalize_vector(vect_acc)
                else:
                    agentA.acc = vect_acc

        for agent in self.Agent_list:
            vect_vit = np.array(
                [agent.speed[0] + dt*agent.acc[0], agent.speed[1] + dt*agent.acc[1]])
            if vect_norme_carre(vect_vit) > maxspeed**2:
                agentA.speed = maxspeed*normalize_vector(vect_vit)
            else:
                agent.speed = vect_vit

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
                screen, white, (edge[0][0], edge[0][1]), (edge[1][0], edge[1][1]))
        for edge in edge_list_v:
            pygame.draw.line(screen, lightgreen,
                             (edge[0][0], edge[0][1]), (edge[1][0], edge[1][1]))

    def show_circles(self):
        for agent in self.Agent_list:
            if type(agent) == Chercheur:
                circle_list.append((agent.pos[0], agent.pos[1]))
        for circle in circle_list:
            pygame.draw.circle(screen, shadow, circle, self.res/2)

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
                    pygame.draw.circle(screen, red, point, 3)


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


def vect_norme_carre(vect):
    return vect[0]**2 + vect[1]**2


def normalize_vector(vect):
    return vect/np.sqrt(vect_norme_carre(vect))


if __name__ == '__main__':
    env = Environment(10, 2, 0, 750, 750)
    pygame.init()
    width, height = env.width, env.height
    screen = pygame.display.set_mode((width, height))
    Running = True
    tick_freq = 100
    dt = 1/tick_freq
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
        env.show_circles()
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
