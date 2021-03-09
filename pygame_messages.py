import pygame
import math
import uuid
import random

shadow = (192, 192, 192)
white = (255, 255, 255)
lightgreen = (0, 255, 0)
green = (0, 200, 0)
blue = (0, 0, 128)
lightblue= (0, 0, 255)
red = (200, 0, 0)
lightred = (255, 100, 100)
purple = (102, 0, 102)
lightpurple = (153, 0, 153)

circle_list = []


#Basé sur le fichier de Louis du 09/03/21

class Chercheur():
    """
    Ces drones cherchent des cibles, avant d'appeler un vérificateur

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
        self.x = x
        self.y = y
        self.state = 'normal'
        self.battery = None
        self.dir = direction
        self.size = size
        self.target = None
        self.id = id
        self.destination = None
        self.inbox = []
        self.message = {'sender_id':None, 'recipient_id':None, 'time':None, 'message':{'status':{'x':None, 'y':None, 'z':None, 'dir':None, 'speed':None, 'state':None, 'battery':None}, 'alert':{'verif':None, 'help':None, 't_x':None, 't_y':None, 't_z':None}}}


    def make_message(self, recipient):
        self.message['sender_id']=self.id
        self.message['recipient_id']=recipient.id
        self.message['time'] = t
        self.message['message']['status']['x']=self.x
        self.message['message']['status']['y']=self.y
        self.message['message']['status']['z']=self.z
        self.message['message']['status']['dir']=self.dir
        self.message['message']['status']['speed']=self.speed
        self.message['message']['status']['state']=self.state
        self.message['message']['status']['battery']=self.battery

        if self.target != None:
            self.message['message']['alert']['t_x']=self.target.x
            self.message['message']['alert']['t_y']=self.target.y
            self.message['message']['alert']['t_z']=self.target.z

    def read_message(self):
        pass
    
    def send_message(self):
        pass

    def score(self):
        pass


    

    def display(self):
        """ Dessine le drone sur l'écran """
        
        a = self.dir
        x = self.x
        y = self.y
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
        """ liste des agents (Chercheur ou Verificateur ou Target) à distance <= r du Drone """ 

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


class Verificateur():
    """
    Ces drones vérifient les cibles, après avoir été appelés par un Chercheur.
    Ils restent au voisinage du barycentre des Chercheurs lorsqu'ils ne sont pas appelés

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
        self.x = x
        self.y = y
        self.state = 'normal'
        self.battery = None
        self.dir = direction
        self.size = size
        self.target = None
        self.id = id
        self.destination = None
        self.inbox = []
        self.message = {'sender_id':None, 'recipient_id':None, 'time':None, 'message':{'status':{'x':None, 'y':None, 'z':None, 'dir':None, 'speed':None, 'state':None, 'battery':None}, 'alert':{'verif':None, 'help':None, 't_x':None, 't_y':None, 't_z':None}}}

    def make_message(self, recipient):
        self.message['sender_id']=self.id
        self.message['recipient_id']=recipient.id
        self.message['time'] = t
        self.message['message']['status']['x']=self.x
        self.message['message']['status']['y']=self.y
        self.message['message']['status']['z']=self.z
        self.message['message']['status']['dir']=self.dir
        self.message['message']['status']['speed']=self.speed
        self.message['message']['status']['state']=self.state
        self.message['message']['status']['battery']=self.battery

        if self.target != None:
            self.message['message']['alert']['t_x']=self.target.x
            self.message['message']['alert']['t_y']=self.target.y
            self.message['message']['alert']['t_z']=self.target.z

    def read_message(self):
        pass
    
    def send_message(self):
        pass

    def score(self):
        pass


    def display(self):
        """ Dessine le drone sur l'écran """
        
        a = self.dir
        x = self.x
        y = self.y
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

    def map(self):
        pass

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
        """ liste des agents (Chercheur ou Verificateur ou Target) à distance <= r du Drone """ 

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
        targeted : Boolean : True si ciblé par un Chercheur"""


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
    Agent_list : list : liste de tous les agents (Chercheur et Verificateur et Target) de l'environment"""

    def __init__(self, n_chercheurs, n_verificateurs, n_targets, width, height):
        self.width = width
        self.height = height
        self.Agent_list = []
        for _ in range(n_chercheurs):
            self.Agent_list.append(Chercheur(random.random(
            )*self.width, random.random()*self.height, 100, -90, 5, int(uuid.uuid1()), self))
        for _ in range(n_targets):
            self.Agent_list.append(Target(random.random(
            )*self.width, random.random()*self.height, 5, -90, 5, int(uuid.uuid1()), self))
        for _ in range(n_verificateurs):
            self.Agent_list.append(Verificateur(random.random(
            )*self.width, random.random()*self.height, 100, -90, 5, int(uuid.uuid1()), self))

    def step(self):
        for agent in self.Agent_list:
            agent.step()

    def draw_graph(self):
        """ Dessine le graphe reliant les Drones à portée de communication (càd qui sont voisins)"""
        edge_list_c=[]
        edge_list_v=[]
        for agent in self.Agent_list:
            if type(agent) == Chercheur:
                for neighbour in agent.neighbours():
                    if type(neighbour)==Chercheur:
                        if [(neighbour.x,neighbour.y),(agent.x,agent.y)] not in edge_list_c and [(agent.x,agent.y),(neighbour.x,neighbour.y)] not in edge_list_c:
                            edge_list_c.append([(neighbour.x,neighbour.y),(agent.x,agent.y)])

            if type(agent) == Verificateur:
                for neighbour in agent.neighbours():
                    if type(neighbour)==Chercheur:
                        if [(neighbour.x,neighbour.y),(agent.x,agent.y)] not in edge_list_v and [(agent.x,agent.y),(neighbour.x,neighbour.y)] not in edge_list_v:
                            edge_list_v.append([(neighbour.x,neighbour.y),(agent.x,agent.y)])
                    if type(neighbour)==Verificateur:
                        if [(neighbour.x,neighbour.y),(agent.x,agent.y)] not in edge_list_v and [(agent.x,agent.y),(neighbour.x,neighbour.y)] not in edge_list_v:
                            edge_list_v.append([(neighbour.x,neighbour.y),(agent.x,agent.y)])

        for edge in edge_list_c:
            pygame.draw.line(screen,white,(edge[0][0],edge[0][1]),(edge[1][0],edge[1][1]))
        for edge in edge_list_v:
            pygame.draw.line(screen,lightgreen,(edge[0][0],edge[0][1]),(edge[1][0],edge[1][1]))        
    


    def map_circle_c(self):
        for agent in self.Agent_list:
            if type(agent)==Chercheur:
                circle_list.append((agent.x, agent.y))
        for coord in circle_list:
            pygame.draw.circle(screen, shadow, coord, 10)
        


def distance(Agent1, Agent2):
    """ distance entre deux agents """
    x1, y1 = Agent1.x, Agent1.y
    x2, y2 = Agent2.x, Agent2.y

    d = math.sqrt((x1-x2)**2+(y1-y2)**2)
    return d


def point_distance(x1, y1, x2, y2):
    """ distance entre deux points """
    d = math.sqrt((x1-x2)**2+(y1-y2)**2)
    return d


if __name__ == '__main__':
    env = Environment(10, 3, 0, 750, 750)
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

        env.step()
        for agent in env.Agent_list:
            agent.display()
        env.draw_graph()
        env.map_circle_c()
        pygame.display.update()
        screen.fill((0, 0, 0))
        # Setting FPS
        clock.tick(tick_freq)
    # Shutdown
    pygame.quit()
