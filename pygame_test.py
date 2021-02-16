import pygame
import math
import uuid
import random

white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)

class Drone():
    def __init__(self, x, y, speed, direction, size, id, env):
        self.speed = speed
        self.env = env
        self.x = x
        self.y = y
        self.dir = direction
        self.size = size
        self.target = None
        self.id = id
        self.destination = None
        self.guide = None

    def display(self):
        a = self.dir
        x = self.x
        y = self.y
        s = self.size

        if self.guide == None:
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

        elif self.guide != None:
            pygame.draw.line(screen, blue,
                            (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) - a),
                            y - (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) - a)),
                            (x + s * math.cos(-a), y + s * math.sin(-a)))

            pygame.draw.line(screen, blue,
                            (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) + a),
                            y + (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) + a)),
                            (x + s * math.cos(a), y + s * math.sin(-a)))

            pygame.draw.line(screen, blue,
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
        
        elif self.guide != None:
            t_agent = self.guide.target
            self.destination = t_agent.x, t_agent.y
            

        elif point_distance(self.x, self.y, self.destination[0], self.destination[1]) < 1 and self.target == None:
            self.destination = None
            theta = random.random()*2*math.pi
            dest_x, dest_y = max(min(self.x + r*math.cos(theta), self.env.width), 0), max(
                min(self.y + r*math.sin(theta), self.env.height), 0)
            self.destination = dest_x, dest_y

        elif self.destination != None and self.target != None:
            if self.destination != self.target:
                self.destination = self.target.x, self.target.y
            for agent in self.neighbours(1000):
                agent.guide = self

    def move(self):
        try:
            d = point_distance(
                self.x, self.y, self.destination[0], self.destination[1])

            cosr = (self.destination[0] - self.x)/d
            sinr = (self.destination[1] - self.y)/d
            new_x = max(min(self.x + cosr * self.speed,
                            self.env.width), 0)
            new_y = max(min(self.y + sinr * self.speed,
                            self.env.height), 0)
            new_dir = math.atan2(-sinr, cosr)
            return new_x, new_y, new_dir
        except:
            self.wander()
            self.move()

    def neighbours(self, r=100):
        return [self.env.Agent_list[i] for i in range(len(self.env.Agent_list)) if distance(self, self.env.Agent_list[i]) < r]

    def target_agent(self):
        if self.guide != None:
            return self.guide.target

        elif self.target == None:
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
    def __init__(self, n_drones, n_targets, width, height):
        self.width = width
        self.height = height
        self.Agent_list = []
        for _ in range(n_drones):
            self.Agent_list.append(Drone(random.random(
            )*self.width, random.random()*self.height, 1, -90, 5, int(uuid.uuid1()), self))
        for _ in range(n_targets):
            self.Agent_list.append(Target(random.random(
            )*self.width, random.random()*self.height, 5, -90, 5, int(uuid.uuid1()), self))

    def step(self):
        for agent in self.Agent_list:
            agent.step()


def distance(Agent1, Agent2):
    x1, y1 = Agent1.x, Agent1.y
    x2, y2 = Agent2.x, Agent2.y

    d = math.sqrt((x1-x2)**2+(y1-y2)**2)
    return d


def point_distance(x1, y1, x2, y2):
    d = math.sqrt((x1-x2)**2+(y1-y2)**2)
    return d


if __name__ == '__main__':
    env = Environment(5, 1, 800, 800)
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

        pygame.display.update()
        screen.fill((0, 0, 0))
        # Setting FPS
        clock.tick(tick_freq)
    # Shutdown
    pygame.quit()
