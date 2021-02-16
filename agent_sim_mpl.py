import numpy as np
import random
import math
import matplotlib.pyplot as plt
import tkinter
import matplotlib.colors as colors
"team A == 1, team B == 2, empty == 0"


class Env:
    def __init__(self, size, n_team_A, n_team_B):
        self.N = n_team_A+n_team_B
        self.size = size
        self.Agent_list = []
        for _ in range(n_team_A):
            a_pos = (random.random()*self.size, random.random()*self.size)
            self.Agent_list.append(Agent(a_pos[0], a_pos[1], 'A', self))
        for _ in range(n_team_B):
            b_pos = (random.random()*self.size, random.random()*self.size)
            self.Agent_list.append(
                Agent(b_pos[0], b_pos[1], 'B', self))

    def step(self):
        new_list = []
        for agent in self.Agent_list:
            agent.step()
            new_list.append(agent)
        self.Agent_list = new_list


class Agent:
    def __init__(self, x, y, team, env, speed=1):
        self.x = x
        self.y = y
        self.speed = speed
        self.team = team
        self.env = env
        self.target = None
        self.targeted = False

    def step(self):
        self.target = self.target_agent()
        self.x, self.y = self.wander()

    def wander(self):
        if self.team == 'B' or (self.team == 'A' and self.target == None):
            r = random.random() * math.pi * 2
            new_x = max(min(self.x + math.cos(r) * self.speed,
                            self.env.size), 0)
            new_y = max(min(self.y + math.sin(r) * self.speed,
                            self.env.size), 0)

            return new_x, new_y

        t_agent = self.target
        d = distance(self, t_agent)
        cosr = (t_agent.x - self.x)/d
        sinr = (t_agent.y-self.y)/d

        new_x = max(min(self.x + cosr * self.speed,
                        self.env.size), 0)
        new_y = max(min(self.y + sinr * self.speed,
                        self.env.size), 0)

        return new_x, new_y

    def neighbours(self, r=20):
        return [self.env.Agent_list[i] for i in range(len(self.env.Agent_list)) if distance(self, self.env.Agent_list[i]) < r]

    def target_agent(self):
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


class Simulator():
    pass


def distance(Agent1, Agent2):
    x1, y1 = Agent1.x, Agent1.y
    x2, y2 = Agent2.x, Agent2.y

    d = np.sqrt((x1-x2)**2+(y1-y2)**2)
    return d


def display(env):
    fig = plt.figure(figsize=(12, 12))
    population = env.Agent_list
    for agent in population:
        if agent.team == 'A':
            plt.scatter(agent.x, agent.y, c='green')
        else:
            plt.scatter(agent.x, agent.y, c='blue')

    # using plt add a title
    plt.title("battlefield before simulation run (green = A, blue = B)",
              fontsize=24)
    # using plt add x and y labels
    plt.xlabel("x coordinates", fontsize=20)
    plt.ylabel("y coordinates", fontsize=20)
    # adjust x and y axis ticks, using plt
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    # use .imshow() method from plt to visualize agent locations
    plt.show()


def simulate(env, n_steps=20):
    plt.ion()
    fig = plt.figure(figsize=(12, 12))
    for i in range(n_steps):
        if i == n_steps-1:
            plt.ioff()
        plt.clf()
        population = env.Agent_list
        for agent in population:
            if agent.team == 'A':
                plt.scatter(agent.x, agent.y, c='green')
            else:
                plt.scatter(agent.x, agent.y, c='blue')

        # using plt add a title
        plt.title("battlefield at step "+str(i), fontsize=24)
        # using plt add x and y labels
        plt.xlim([0, env.size])
        plt.ylim([0, env.size])
        plt.xlabel("x coordinates", fontsize=20)
        plt.ylabel("y coordinates", fontsize=20)
        # adjust x and y axis ticks, using plt
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        # use .imshow() method from plt to visualize agent locations
        fig.canvas.update()
        fig.canvas.flush_events()
        env.step()


if __name__ == "__main__":
    env = Env(50, 25, 25)
    simulate(env, n_steps=150)
    for agent in env.Agent_list:
        print(agent.target)
